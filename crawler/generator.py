"""docs/index.html 생성기"""
from datetime import datetime, timezone, timedelta
import json

KST = timezone(timedelta(hours=9))

CATEGORY_KO = {
    "intern": "인턴십",
    "bootcamp": "부트캠프",
    "training": "교육 프로그램",
    "hiring_linked_program": "채용연계형",
}

JOB_AREA_KO = {
    "backend": "백엔드",
    "frontend": "프론트엔드",
    "fullstack": "풀스택",
    "mobile": "모바일",
    "data": "데이터",
    "ai": "AI",
    "cloud": "클라우드",
    "embedded": "임베디드",
    "security": "보안",
}

STATUS_CONFIG = {
    "open":      ("모집중",   "status-open"),
    "closed":    ("마감",     "status-closed"),
    "recurring": ("정기모집", "status-recurring"),
    "unclear":   ("확인필요", "status-unclear"),
}


def _badge(status: str) -> str:
    label, cls = STATUS_CONFIG.get(status, ("확인필요", "status-unclear"))
    return f'<span class="badge {cls}">{label}</span>'


def _area_tags(items: list) -> str:
    return " ".join(
        f'<span class="tag">{JOB_AREA_KO.get(i, i)}</span>'
        for i in items
    )


def _tech_tags(items: list) -> str:
    return " ".join(
        f'<span class="tag-tech">{t}</span>'
        for t in items[:6]
    )


def render_card(p: dict) -> str:
    status  = p.get("display_status") or p.get("status", "unclear")
    cat     = CATEGORY_KO.get(p.get("category", ""), p.get("category", ""))
    areas   = _area_tags(p.get("job_area", []))
    techs   = _tech_tags(p.get("tech_keywords", []))
    benefits_li = "".join(f"<li>{b}</li>" for b in p.get("benefits", []))
    benefits_html = f'<ul class="card-benefits">{benefits_li}</ul>' if benefits_li else ""
    url     = p.get("official_url", "#")
    period  = p.get("application_period", "확인 필요")
    location = p.get("location", "확인 필요")
    online  = p.get("online_offline", "확인 필요")
    paid    = p.get("paid_or_free", "확인 필요")

    return (
        f'<article class="card" '
        f'data-category="{p.get("category","")}" '
        f'data-status="{status}" '
        f'data-area="{" ".join(p.get("job_area",[]))}">\n'
        f'  <div class="card-header">\n'
        f'    <div class="card-meta">\n'
        f'      <span class="cat-label">{cat}</span>\n'
        f'      {_badge(status)}\n'
        f'    </div>\n'
        f'    <h2 class="card-title">{p["program_name"]}</h2>\n'
        f'    <p class="card-org">{p["company_or_org"]}</p>\n'
        f'  </div>\n'
        f'  <div class="card-body">\n'
        f'    <p class="card-summary">{p.get("summary","")}</p>\n'
        f'    <div class="card-areas">{areas}</div>\n'
        f'    <div class="card-info">\n'
        f'      <div class="info-row"><span class="info-icon">📅</span>'
        f'<span>모집 기간: <strong>{period}</strong></span></div>\n'
        f'      <div class="info-row"><span class="info-icon">📍</span>'
        f'<span>{location} ({online})</span></div>\n'
        f'      <div class="info-row"><span class="info-icon">💰</span>'
        f'<span>{paid}</span></div>\n'
        f'    </div>\n'
        f'    {benefits_html}\n'
        f'    <div class="card-techs">{techs}</div>\n'
        f'  </div>\n'
        f'  <div class="card-footer">\n'
        f'    <a href="{url}" target="_blank" rel="noopener" class="btn-official">'
        f'공식 사이트 →</a>\n'
        f'  </div>\n'
        f'</article>\n'
    )


# JavaScript는 f-string 밖에 따로 정의해 충돌 방지
_JS = r"""
(function() {
  const grid = document.getElementById('card-grid');
  const cards = Array.from(grid.querySelectorAll('.card'));
  const countEl = document.getElementById('result-count');
  const searchInput = document.getElementById('search');
  const filters = { status: 'all', category: 'all', area: 'all' };

  function applyFilters() {
    const q = searchInput.value.toLowerCase().trim();
    let visible = 0;
    cards.forEach(card => {
      const status   = card.dataset.status   || '';
      const category = card.dataset.category || '';
      const areas    = (card.dataset.area    || '').split(' ');
      const text     = card.textContent.toLowerCase();

      const ok = (filters.status   === 'all' || status    === filters.status)
              && (filters.category === 'all' || category  === filters.category)
              && (filters.area     === 'all' || areas.includes(filters.area))
              && (!q || text.includes(q));

      card.classList.toggle('hidden', !ok);
      if (ok) visible++;
    });
    countEl.textContent = visible + '개 프로그램';
  }

  document.querySelectorAll('.filter-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const type  = btn.dataset.filter;
      const value = btn.dataset.value;
      filters[type] = value;
      document.querySelectorAll(`.filter-btn[data-filter="${type}"]`)
        .forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      applyFilters();
    });
  });

  let timer;
  searchInput.addEventListener('input', () => {
    clearTimeout(timer);
    timer = setTimeout(applyFilters, 200);
  });

  applyFilters();
})();
"""

# CSS도 f-string 밖에 정의
_CSS = r"""
:root {
  --bg: #0f1117; --surface: #1a1d27; --surface2: #22263a;
  --border: #2d3248; --text: #e2e8f0; --text-muted: #8892a4;
  --accent: #6366f1; --accent2: #818cf8;
  --open: #10b981; --closed: #ef4444; --recurring: #f59e0b;
  --radius: 12px; --shadow: 0 4px 24px rgba(0,0,0,.4);
}
* { box-sizing: border-box; margin: 0; padding: 0; }
body {
  font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  background: var(--bg); color: var(--text); min-height: 100vh; line-height: 1.6;
}
.hero {
  background: linear-gradient(135deg, #1e1b4b 0%, #0f172a 60%, #1a1d27 100%);
  padding: 60px 24px 48px; text-align: center;
  border-bottom: 1px solid var(--border);
  position: relative; overflow: hidden;
}
.hero::before {
  content: ''; position: absolute; inset: 0;
  background: radial-gradient(ellipse at 50% 0%, rgba(99,102,241,.15) 0%, transparent 70%);
}
.hero-badge {
  display: inline-block; background: rgba(99,102,241,.2);
  border: 1px solid rgba(99,102,241,.4); color: var(--accent2);
  padding: 4px 14px; border-radius: 999px;
  font-size: .8rem; font-weight: 600; letter-spacing: .05em; margin-bottom: 16px;
}
.hero h1 {
  font-size: clamp(1.8rem, 5vw, 3rem); font-weight: 800;
  background: linear-gradient(135deg, #e0e7ff, #818cf8);
  -webkit-background-clip: text; -webkit-text-fill-color: transparent;
  background-clip: text; margin-bottom: 12px;
}
.hero-sub { color: var(--text-muted); font-size: 1rem; margin-bottom: 24px; }
.hero-stats { display: flex; justify-content: center; gap: 32px; flex-wrap: wrap; }
.stat { text-align: center; }
.stat-num { font-size: 2rem; font-weight: 800; color: var(--accent2); }
.stat-label { font-size: .8rem; color: var(--text-muted); }
.updated-at { margin-top: 20px; font-size: .75rem; color: var(--text-muted); }

.controls {
  position: sticky; top: 0; z-index: 100;
  background: rgba(15,17,23,.92); backdrop-filter: blur(12px);
  border-bottom: 1px solid var(--border); padding: 14px 24px;
}
.controls-inner {
  max-width: 1280px; margin: 0 auto;
  display: flex; flex-wrap: wrap; gap: 12px; align-items: center;
}
.search-box { flex: 1; min-width: 200px; position: relative; }
.search-box input {
  width: 100%; background: var(--surface); border: 1px solid var(--border);
  border-radius: 8px; padding: 8px 14px 8px 36px;
  color: var(--text); font-size: .9rem; outline: none; transition: border-color .2s;
}
.search-box input:focus { border-color: var(--accent); }
.search-box::before {
  content: '🔍'; position: absolute; left: 10px;
  top: 50%; transform: translateY(-50%); font-size: .85rem;
}
.filter-group { display: flex; flex-wrap: wrap; gap: 6px; align-items: center; }
.filter-label { font-size: .75rem; color: var(--text-muted); white-space: nowrap; }
.filter-btn {
  background: var(--surface); border: 1px solid var(--border);
  color: var(--text-muted); padding: 5px 12px; border-radius: 6px;
  font-size: .8rem; cursor: pointer; transition: all .2s; white-space: nowrap;
}
.filter-btn:hover, .filter-btn.active { background: var(--accent); border-color: var(--accent); color: #fff; }
.filter-btn.s-open.active   { background: var(--open);      border-color: var(--open); }
.filter-btn.s-closed.active { background: var(--closed);    border-color: var(--closed); }
.filter-btn.s-rec.active    { background: var(--recurring); border-color: var(--recurring); }

.main { max-width: 1280px; margin: 0 auto; padding: 32px 24px 80px; }
.result-count { font-size: .85rem; color: var(--text-muted); margin-bottom: 20px; }
.grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(340px, 1fr)); gap: 20px; }
.card {
  background: var(--surface); border: 1px solid var(--border);
  border-radius: var(--radius); display: flex; flex-direction: column;
  transition: transform .2s, box-shadow .2s, border-color .2s; overflow: hidden;
}
.card:hover { transform: translateY(-4px); box-shadow: var(--shadow); border-color: var(--accent); }
.card.hidden { display: none; }
.card-header {
  padding: 20px 20px 12px; border-bottom: 1px solid var(--border);
  background: linear-gradient(180deg, var(--surface2) 0%, var(--surface) 100%);
}
.card-meta { display: flex; align-items: center; gap: 8px; margin-bottom: 8px; }
.cat-label {
  font-size: .7rem; color: var(--text-muted); background: var(--bg);
  padding: 2px 8px; border-radius: 4px; border: 1px solid var(--border);
}
.card-title { font-size: 1rem; font-weight: 700; color: var(--text); line-height: 1.4; margin-bottom: 4px; }
.card-org { font-size: .8rem; color: var(--text-muted); }
.card-body { padding: 16px 20px; flex: 1; display: flex; flex-direction: column; gap: 12px; }
.card-summary { font-size: .85rem; color: var(--text-muted); line-height: 1.6; }
.card-areas { display: flex; flex-wrap: wrap; gap: 4px; }
.card-info { display: flex; flex-direction: column; gap: 6px; }
.info-row { display: flex; align-items: flex-start; gap: 8px; font-size: .82rem; color: var(--text-muted); }
.info-icon { flex-shrink: 0; }
.info-row strong { color: var(--text); }
.card-benefits { padding-left: 16px; font-size: .8rem; color: var(--text-muted); display: flex; flex-direction: column; gap: 3px; }
.card-benefits li::marker { color: var(--accent); }
.card-techs { display: flex; flex-wrap: wrap; gap: 4px; margin-top: auto; }
.card-footer { padding: 14px 20px; border-top: 1px solid var(--border); }

.badge { display: inline-block; padding: 2px 10px; border-radius: 999px; font-size: .7rem; font-weight: 700; letter-spacing: .04em; }
.status-open      { background: rgba(16,185,129,.2); color: #34d399; border: 1px solid rgba(16,185,129,.3); }
.status-closed    { background: rgba(239,68,68,.15); color: #f87171; border: 1px solid rgba(239,68,68,.3); }
.status-recurring { background: rgba(245,158,11,.15); color: #fbbf24; border: 1px solid rgba(245,158,11,.3); }
.status-unclear   { background: rgba(100,116,139,.15); color: #94a3b8; border: 1px solid rgba(100,116,139,.3); }
.tag { display: inline-block; background: rgba(99,102,241,.15); color: var(--accent2); border: 1px solid rgba(99,102,241,.25); padding: 2px 8px; border-radius: 4px; font-size: .72rem; font-weight: 500; }
.tag-tech { display: inline-block; background: var(--surface2); color: var(--text-muted); border: 1px solid var(--border); padding: 2px 7px; border-radius: 4px; font-size: .7rem; }
.btn-official { display: block; text-align: center; background: linear-gradient(135deg, var(--accent), #4f46e5); color: #fff; padding: 9px 16px; border-radius: 8px; text-decoration: none; font-size: .85rem; font-weight: 600; transition: opacity .2s; }
.btn-official:hover { opacity: .85; }

footer { text-align: center; padding: 32px; border-top: 1px solid var(--border); color: var(--text-muted); font-size: .8rem; }
footer a { color: var(--accent2); text-decoration: none; }
@media (max-width: 600px) {
  .hero { padding: 40px 16px 32px; }
  .main { padding: 20px 12px 60px; }
  .grid { grid-template-columns: 1fr; }
}
"""


def generate_html(programs: list, updated_at: str) -> str:
    cards = "\n".join(render_card(p) for p in programs)
    total = len(programs)
    open_count = sum(1 for p in programs if p.get("display_status") == "open")

    return (
        "<!DOCTYPE html>\n"
        '<html lang="ko">\n'
        "<head>\n"
        '<meta charset="UTF-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
        "<title>한국 개발자 기회 모음 | Dev Opportunities KR</title>\n"
        '<meta name="description" content="한국의 개발 인턴십·부트캠프·채용연계 교육 프로그램을 매일 자동 업데이트합니다.">\n'
        f"<style>\n{_CSS}\n</style>\n"
        "</head>\n"
        "<body>\n"
        '<header class="hero">\n'
        '  <div class="hero-badge">🇰🇷 Daily Updated</div>\n'
        "  <h1>한국 개발자 기회 모음</h1>\n"
        '  <p class="hero-sub">인턴십 · 부트캠프 · 채용연계 교육 프로그램 · 공채</p>\n'
        '  <div class="hero-stats">\n'
        '    <div class="stat"><div class="stat-num">' + str(total) + "</div>"
        '<div class="stat-label">전체 프로그램</div></div>\n'
        '    <div class="stat"><div class="stat-num">' + str(open_count) + "</div>"
        '<div class="stat-label">현재 모집중</div></div>\n'
        "  </div>\n"
        f'  <p class="updated-at">마지막 업데이트: {updated_at} (KST)</p>\n'
        "</header>\n"
        '\n<div class="controls">\n'
        '  <div class="controls-inner">\n'
        '    <div class="search-box">\n'
        '      <input type="text" id="search" placeholder="프로그램명, 기업명, 기술 검색...">\n'
        "    </div>\n"
        '    <div class="filter-group">\n'
        '      <span class="filter-label">상태</span>\n'
        '      <button class="filter-btn active" data-filter="status" data-value="all">전체</button>\n'
        '      <button class="filter-btn s-open" data-filter="status" data-value="open">모집중</button>\n'
        '      <button class="filter-btn s-rec" data-filter="status" data-value="recurring">정기모집</button>\n'
        '      <button class="filter-btn s-closed" data-filter="status" data-value="closed">마감</button>\n'
        "    </div>\n"
        '    <div class="filter-group">\n'
        '      <span class="filter-label">유형</span>\n'
        '      <button class="filter-btn active" data-filter="category" data-value="all">전체</button>\n'
        '      <button class="filter-btn" data-filter="category" data-value="intern">인턴십</button>\n'
        '      <button class="filter-btn" data-filter="category" data-value="bootcamp">부트캠프</button>\n'
        '      <button class="filter-btn" data-filter="category" data-value="training">교육</button>\n'
        '      <button class="filter-btn" data-filter="category" data-value="hiring_linked_program">채용연계</button>\n'
        "    </div>\n"
        '    <div class="filter-group">\n'
        '      <span class="filter-label">분야</span>\n'
        '      <button class="filter-btn active" data-filter="area" data-value="all">전체</button>\n'
        '      <button class="filter-btn" data-filter="area" data-value="backend">백엔드</button>\n'
        '      <button class="filter-btn" data-filter="area" data-value="frontend">프론트</button>\n'
        '      <button class="filter-btn" data-filter="area" data-value="ai">AI</button>\n'
        '      <button class="filter-btn" data-filter="area" data-value="fullstack">풀스택</button>\n'
        '      <button class="filter-btn" data-filter="area" data-value="data">데이터</button>\n'
        '      <button class="filter-btn" data-filter="area" data-value="cloud">클라우드</button>\n'
        "    </div>\n"
        "  </div>\n"
        "</div>\n"
        '\n<main class="main">\n'
        '  <p class="result-count" id="result-count">' + str(total) + "개 프로그램</p>\n"
        '  <div class="grid" id="card-grid">\n'
        + cards +
        "  </div>\n"
        "</main>\n"
        "\n<footer>\n"
        "  <p>매일 09:00 KST 자동 업데이트 · 공식 사이트 정보 기준 · 최종 확인 필수</p>\n"
        '  <p style="margin-top:8px">'
        '<a href="https://github.com" target="_blank">GitHub</a> · '
        "오류 제보는 Issues로 부탁드립니다</p>\n"
        "</footer>\n"
        f"\n<script>\n{_JS}\n</script>\n"
        "</body>\n"
        "</html>\n"
    )


def generate_json(programs: list) -> str:
    export = [
        {k: v for k, v in p.items()
         if k not in ("status_keywords", "closed_keywords", "check_url")}
        for p in programs
    ]
    return json.dumps(export, ensure_ascii=False, indent=2)