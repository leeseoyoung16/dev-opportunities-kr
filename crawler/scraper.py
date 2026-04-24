import requests
from bs4 import BeautifulSoup
import logging
import time
import re

logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

TIMEOUT = 10
RETRY = 2


def fetch_page(url: str) -> tuple[int, str]:
    """HTTP 상태코드와 텍스트 반환. 실패 시 (0, '')."""
    for attempt in range(RETRY):
        try:
            resp = requests.get(url, headers=HEADERS, timeout=TIMEOUT, allow_redirects=True)
            return resp.status_code, resp.text
        except Exception as e:
            logger.warning(f"[{attempt+1}/{RETRY}] fetch failed {url}: {e}")
            time.sleep(2)
    return 0, ""


def detect_status(html: str, open_keywords: list[str], closed_keywords: list[str]) -> str:
    """
    페이지 텍스트에서 모집 상태를 추론.
    반환값: 'open' | 'closed' | 'unclear'
    """
    if not html:
        return "unclear"

    soup = BeautifulSoup(html, "html.parser")
    # script/style 제거
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()
    text = soup.get_text(separator=" ", strip=True)

    closed_score = sum(1 for kw in closed_keywords if kw in text)
    open_score = sum(1 for kw in open_keywords if kw in text)

    # "마감" + 날짜 패턴이 있으면 closed 가중치 추가
    if re.search(r"(접수\s*마감|모집\s*마감|지원\s*종료|모집\s*종료)", text):
        closed_score += 2

    if re.search(r"(모집\s*중|접수\s*중|지원\s*중|신청\s*가능)", text):
        open_score += 2

    if open_score > closed_score:
        return "open"
    if closed_score > open_score:
        return "closed"
    return "unclear"


def check_program(program: dict) -> dict:
    """단일 프로그램 URL 체크 후 상태 업데이트된 dict 반환."""
    url = program.get("check_url") or program.get("official_url")
    http_code, html = fetch_page(url)

    result = program.copy()
    result["http_status"] = http_code

    if http_code == 0:
        result["url_reachable"] = False
        result["detected_status"] = "unclear"
    elif http_code >= 400:
        result["url_reachable"] = False
        result["detected_status"] = "unclear"
    else:
        result["url_reachable"] = True
        detected = detect_status(
            html,
            program.get("status_keywords", []),
            program.get("closed_keywords", []),
        )
        result["detected_status"] = detected

        # 원래 status가 'open'/'closed'로 명시된 경우 감지 결과로 보완
        if program.get("status") == "recurring":
            result["display_status"] = detected if detected != "unclear" else "recurring"
        else:
            result["display_status"] = detected if detected != "unclear" else program.get("status", "unclear")

    return result