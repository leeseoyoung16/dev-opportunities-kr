"""
메인 실행 스크립트.
1. programs_data.json 로드
2. 각 URL 상태 체크 (scraper)
3. docs/data.json + docs/index.html 생성 (generator)
"""
import json
import logging
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path

from scraper import check_program
from generator import generate_html, generate_json

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

ROOT = Path(__file__).parent.parent
DOCS = ROOT / "docs"
DATA_FILE = Path(__file__).parent / "programs_data.json"

KST = timezone(timedelta(hours=9))


def load_programs() -> list:
    with open(DATA_FILE, encoding="utf-8") as f:
        return json.load(f)


def sort_programs(programs: list) -> list:
    priority = {"open": 0, "recurring": 1, "unclear": 2, "closed": 3}
    return sorted(
        programs,
        key=lambda p: (
            priority.get(p.get("display_status", "unclear"), 2),
            p.get("program_name", ""),
        ),
    )


def main():
    DOCS.mkdir(exist_ok=True)

    programs = load_programs()
    logger.info(f"프로그램 {len(programs)}개 로드 완료")

    results = []
    for i, program in enumerate(programs, 1):
        logger.info(f"[{i}/{len(programs)}] 체크 중: {program['program_name']}")
        checked = check_program(program)
        results.append(checked)
        time.sleep(0.5)  # 서버 부하 방지

    results = sort_programs(results)

    now_kst = datetime.now(KST)
    updated_at = now_kst.strftime("%Y-%m-%d %H:%M")

    # docs/data.json
    json_path = DOCS / "data.json"
    json_path.write_text(generate_json(results), encoding="utf-8")
    logger.info(f"data.json 저장: {json_path}")

    # docs/index.html
    html_path = DOCS / "index.html"
    html_path.write_text(generate_html(results, updated_at), encoding="utf-8")
    logger.info(f"index.html 저장: {html_path}")

    open_cnt = sum(1 for p in results if p.get("display_status") == "open")
    logger.info(f"완료 — 전체 {len(results)}개 / 모집중 {open_cnt}개")


if __name__ == "__main__":
    main()