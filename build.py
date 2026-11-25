#!/usr/bin/env python3
"""Render data/*.json into warm magazine-style static pages."""

from __future__ import annotations

import json
import sys
from datetime import date, datetime
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
SITE_BASE = "https://addielu-phy.github.io/adhd-parenting-digest"

WEEKDAYS = "一二三四五六日"

BADGE_CLASS = {
    "同儕審查研究": "badge-research",
    "專業衛教": "badge-edu",
    "實務經驗分享": "badge-practice",
}

CSS = """
:root {
  --bg: #FBF6EE;
  --bg-glow-top: rgba(212, 137, 74, 0.10);
  --bg-glow-bottom: rgba(180, 81, 42, 0.05);
  --paper: #FFFCF7;
  --ink: #2C241E;
  --ink-soft: #5A4C40;
  --muted: #7A6A5B;
  --line: rgba(90, 60, 30, 0.10);
  --terracotta: #B4512A;
  --terracotta-dark: #8E3A16;
  --tonight-bg: linear-gradient(180deg, #FBE8D4 0%, #F4D8B8 100%);
  --try-bg: #F8F0E3;
  --limit-bg: #F3EDE3;
  --shadow: 0 10px 30px rgba(80, 50, 20, 0.08);
  --radius: 20px;
}

* { box-sizing: border-box; }

html {
  -webkit-text-size-adjust: 100%;
  text-size-adjust: 100%;
}

body {
  margin: 0;
  color: var(--ink);
  font-family: "Noto Sans TC", "PingFang TC", "Hiragino Sans CNS", "Microsoft JhengHei", sans-serif;
  font-size: 17px;
  line-height: 1.85;
  background-color: var(--bg);
  background-image:
    radial-gradient(ellipse 120% 50% at 50% -10%, var(--bg-glow-top), transparent 60%),
    radial-gradient(ellipse 80% 40% at 80% 110%, var(--bg-glow-bottom), transparent 60%);
  min-height: 100vh;
}

a { color: var(--terracotta-dark); }
a:hover { color: var(--terracotta); }
a:focus-visible {
  outline: 3px solid var(--terracotta);
  outline-offset: 3px;
  border-radius: 4px;
}

.wrap {
  width: min(680px, calc(100% - 40px));
  margin: 0 auto;
  padding: 28px 0 72px;
}

.topbar {
  height: 6px;
  background: linear-gradient(90deg, #8E3A16, #B4512A 40%, #D4894A 75%, #E8C090);
  position: sticky;
  top: 0;
  z-index: 10;
}

.kicker {
  display: block;
  margin: 8px 0 0;
  color: var(--terracotta);
  font-size: 0.78rem;
  font-weight: 700;
  letter-spacing: 0.22em;
  text-align: center;
}

.rule {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  margin: 14px 0 18px;
  color: var(--terracotta);
}
.rule::before,
.rule::after {
  content: "";
  width: 56px;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(180, 81, 42, 0.45), transparent);
}
.rule span {
  width: 6px;
  height: 6px;
  border-radius: 1px;
  background: var(--terracotta);
  transform: rotate(45deg);
  opacity: 0.85;
}

.issue-date {
  margin: 0 0 16px;
  text-align: center;
  font-family: "Noto Serif TC", "Songti TC", "PMingLiU", Georgia, serif;
  font-size: clamp(1.65rem, 6.4vw, 2.2rem);
  font-weight: 700;
  line-height: 1.35;
  letter-spacing: 0.02em;
}

.lede {
  margin: 0 auto 28px;
  color: var(--ink-soft);
  text-align: center;
  font-size: 1.02rem;
  line-height: 1.8;
  text-wrap: balance;
  max-width: 32em;
}

.tonight {
  background: var(--tonight-bg);
  border: 1px solid rgba(180, 81, 42, 0.18);
  border-radius: var(--radius);
  box-shadow: var(--shadow);
  padding: 22px 22px 24px;
  margin-bottom: 28px;
}
.tonight-label {
  display: inline-block;
  margin: 0 0 10px;
  padding: 3px 10px;
  border-radius: 999px;
  background: rgba(142, 58, 22, 0.10);
  color: var(--terracotta-dark);
  font-size: 0.78rem;
  font-weight: 700;
  letter-spacing: 0.10em;
}
.tonight p {
  margin: 0;
  font-family: "Noto Serif TC", "Songti TC", "PMingLiU", Georgia, serif;
  font-size: 1.08rem;
  font-weight: 600;
  line-height: 1.8;
}

.card {
  background: var(--paper);
  border: 1px solid var(--line);
  border-radius: var(--radius);
  box-shadow: var(--shadow);
  padding: 24px 22px 22px;
  margin-bottom: 20px;
}

@media (hover: hover) {
  .card { transition: transform 0.2s ease, box-shadow 0.2s ease; }
  .card:hover {
    transform: translateY(-2px);
    box-shadow: 0 14px 34px rgba(80, 50, 20, 0.11);
  }
}

.card-num {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  margin-bottom: 10px;
  border-radius: 50%;
  background: var(--terracotta);
  color: #FFFDF8;
  font-family: "Noto Serif TC", Georgia, serif;
  font-size: 0.95rem;
  font-weight: 700;
  line-height: 1;
}

.card h2 {
  margin: 0 0 12px;
  font-family: "Noto Serif TC", "Songti TC", "PMingLiU", Georgia, serif;
  font-size: 1.28rem;
  font-weight: 700;
  line-height: 1.45;
  overflow-wrap: break-word;
}

.meta {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px 10px;
  margin: 0 0 14px;
}

.source {
  color: var(--muted);
  font-size: 0.88rem;
  line-height: 1.55;
  overflow-wrap: anywhere;
}

.badge {
  display: inline-block;
  flex: 0 0 auto;
  padding: 3px 10px;
  border-radius: 999px;
  font-size: 0.75rem;
  font-weight: 700;
  letter-spacing: 0.04em;
  line-height: 1.5;
  white-space: nowrap;
}
.badge-research { background: #E3EDE4; color: #2F5D3A; }
.badge-edu { background: #F6E3D2; color: #8E3A16; }
.badge-practice { background: #EFE6D8; color: #5C4632; }
.badge-default { background: #EEE7DC; color: #5A4C40; }

.limit {
  margin: 0 0 14px;
  padding: 10px 12px;
  border-radius: 12px;
  background: var(--limit-bg);
  color: var(--ink-soft);
  font-size: 0.88rem;
  line-height: 1.65;
}
.limit strong {
  color: var(--terracotta-dark);
  font-weight: 700;
}

.summary { margin: 0; overflow-wrap: break-word; text-wrap: pretty; }
.tonight p, .try p, .limit, .issue-card h2 { text-wrap: pretty; }

.try {
  margin: 16px 0 0;
  padding: 14px 16px 15px;
  border-radius: 14px;
  background: var(--try-bg);
  border-left: 3px solid var(--terracotta);
}
.try-label {
  display: block;
  margin: 0 0 6px;
  color: var(--terracotta-dark);
  font-size: 0.78rem;
  font-weight: 700;
  letter-spacing: 0.08em;
}
.try p { margin: 0; }

.read {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  margin-top: 16px;
  padding: 10px 18px;
  min-height: 44px;
  border-radius: 999px;
  background: var(--terracotta);
  color: #FFFDF8;
  text-decoration: none;
  font-weight: 600;
  font-size: 0.95rem;
}
.read:hover { background: var(--terracotta-dark); color: #FFFDF8; }
.read:focus-visible { outline-color: var(--terracotta-dark); }

.site-footer {
  margin-top: 36px;
  padding-top: 22px;
  border-top: 1px solid var(--line);
  color: var(--muted);
  font-size: 0.86rem;
  line-height: 1.7;
  text-align: center;
}
.site-footer p { margin: 0 0 8px; }
.site-footer a { font-weight: 600; }

/* Index */
.issue-list { display: grid; gap: 16px; }
.issue-card {
  display: block;
  background: var(--paper);
  border: 1px solid var(--line);
  border-radius: var(--radius);
  box-shadow: var(--shadow);
  padding: 22px 22px 20px;
  text-decoration: none;
  color: inherit;
}
.issue-card:hover { color: inherit; }
@media (hover: hover) {
  .issue-card { transition: transform 0.2s ease, box-shadow 0.2s ease; }
  .issue-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 14px 34px rgba(80, 50, 20, 0.11);
  }
}
.issue-card .when {
  display: block;
  margin: 0 0 8px;
  color: var(--terracotta);
  font-weight: 700;
  letter-spacing: 0.04em;
  font-size: 0.92rem;
}
.issue-card h2 {
  margin: 0 0 10px;
  font-family: "Noto Serif TC", "Songti TC", "PMingLiU", Georgia, serif;
  font-size: 1.15rem;
  font-weight: 700;
  line-height: 1.55;
}
.issue-card .cta {
  color: var(--terracotta-dark);
  font-weight: 700;
  font-size: 0.92rem;
}
.empty {
  text-align: center;
  color: var(--muted);
}

@media (min-width: 720px) {
  .wrap { padding: 44px 0 88px; }
  body { font-size: 18px; }
  .card, .tonight, .issue-card { padding: 28px 28px 26px; }
  .card h2 { font-size: 1.4rem; }
}
""".strip()


def chinese_date(iso: str) -> str:
    d = date.fromisoformat(iso)
    # Monday is 0 in weekday(); map to 一二三四五六日
    w = WEEKDAYS[d.weekday()]
    return f"{d.year} 年 {d.month} 月 {d.day} 日（{w}）"


def load_issues() -> list[dict]:
    if not DATA_DIR.exists():
        return []
    issues = []
    for path in sorted(DATA_DIR.glob("*.json")):
        with path.open(encoding="utf-8") as f:
            data = json.load(f)
        if "date" not in data:
            raise SystemExit(f"Missing 'date' in {path}")
        if path.stem != data["date"]:
            raise SystemExit(f"Filename {path.name} does not match date {data['date']}")
        issues.append(data)
    issues.sort(key=lambda x: x["date"], reverse=True)
    return issues


def badge_class(label: str) -> str:
    return BADGE_CLASS.get(label, "badge-default")


def font_links() -> str:
    return """
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@400;500;600;700&family=Noto+Serif+TC:wght@600;700&display=swap" rel="stylesheet">
""".strip()


def head(title: str, description: str, url: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="zh-Hant">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(title)}</title>
<meta name="description" content="{escape(description)}">
<meta name="theme-color" content="#FBF6EE">
<meta name="color-scheme" content="light">
<meta property="og:title" content="{escape(title)}">
<meta property="og:description" content="{escape(description)}">
<meta property="og:type" content="article">
<meta property="og:locale" content="zh_TW">
<meta property="og:url" content="{escape(url)}">
<meta name="twitter:card" content="summary">
<meta name="twitter:title" content="{escape(title)}">
<meta name="twitter:description" content="{escape(description)}">
{font_links()}
<style>
{CSS}
</style>
</head>
"""


def render_item(index: int, item: dict) -> str:
    limitation = (item.get("limitation") or "").strip()
    limit_html = ""
    if limitation:
        limit_html = (
            f'<p class="limit"><strong>研究限制</strong>　{escape(limitation)}</p>'
        )
    cred = item.get("credibility") or ""
    return f"""
<article class="card">
  <span class="card-num" aria-hidden="true">{index}</span>
  <h2>{escape(item["title"])}</h2>
  <div class="meta">
    <span class="source">{escape(item["source"])}</span>
    <span class="badge {badge_class(cred)}">{escape(cred)}</span>
  </div>
  {limit_html}
  <p class="summary">{escape(item["summary"])}</p>
  <div class="try">
    <span class="try-label">今晚可以試</span>
    <p>{escape(item["try_tonight"])}</p>
  </div>
  <a class="read" href="{escape(item["link"], quote=True)}" target="_blank" rel="noopener noreferrer">閱讀原文</a>
</article>
""".strip()


def render_daily(issue: dict) -> str:
    iso = issue["date"]
    display = chinese_date(iso)
    title = f"ADHD 青少年親子精選｜{display}"
    url = f"{SITE_BASE}/{iso}/"
    items = "\n".join(
        render_item(i, item) for i, item in enumerate(issue["items"], 1)
    )
    return f"""{head(title, issue["summary"], url)}
<body>
  <div class="topbar" aria-hidden="true"></div>
  <main class="wrap">
    <header>
      <span class="kicker">ADHD 青少年親子精選</span>
      <div class="rule" aria-hidden="true"><span></span></div>
      <h1 class="issue-date">{escape(display)}</h1>
      <p class="lede">{escape(issue["summary"])}</p>
    </header>
    <section class="tonight" aria-labelledby="tonight-label">
      <p class="tonight-label" id="tonight-label">今晚只試一件事</p>
      <p>{escape(issue["tonight_one_thing"])}</p>
    </section>
    {items}
    <footer class="site-footer">
      <p>本頁內容為家長參考資料彙整，不能取代醫師或心理專業人員的評估與建議。</p>
      <p>本頁內容由 Grok 協助蒐集整理（made by Grok）。</p>
      <p><a href="../">回到總覽</a></p>
    </footer>
  </main>
</body>
</html>
"""


def render_index(issues: list[dict]) -> str:
    title = "ADHD 青少年親子精選"
    description = "每日為家長篩選有參考價值的研究、衛教與實務文章。"
    if issues:
        cards = []
        for issue in issues:
            display = chinese_date(issue["date"])
            cards.append(
                f"""
<a class="issue-card" href="{escape(issue['date'], quote=True)}/">
  <span class="when">{escape(display)}</span>
  <h2>{escape(issue["summary"])}</h2>
  <span class="cta">閱讀本期</span>
</a>
""".strip()
            )
        listing = '<div class="issue-list">\n' + "\n".join(cards) + "\n</div>"
    else:
        listing = '<p class="empty">尚無刊出內容。</p>'

    return f"""{head(title, description, SITE_BASE + "/")}
<body>
  <div class="topbar" aria-hidden="true"></div>
  <main class="wrap">
    <header>
      <span class="kicker">ADHD 青少年親子精選</span>
      <div class="rule" aria-hidden="true"><span></span></div>
      <h1 class="issue-date">每日精選總覽</h1>
      <p class="lede">{escape(description)}</p>
    </header>
    {listing}
    <footer class="site-footer">
      <p>本站內容為家長參考資料彙整，不能取代醫師或心理專業人員的評估與建議。</p>
      <p>本頁內容由 Grok 協助蒐集整理（made by Grok）。</p>
    </footer>
  </main>
</body>
</html>
"""


def build() -> None:
    issues = load_issues()
    for issue in issues:
        dest = ROOT / issue["date"]
        dest.mkdir(parents=True, exist_ok=True)
        (dest / "index.html").write_text(render_daily(issue), encoding="utf-8")
        print(f"wrote {dest / 'index.html'}")
    (ROOT / "index.html").write_text(render_index(issues), encoding="utf-8")
    print(f"wrote {ROOT / 'index.html'} ({len(issues)} issue(s))")


if __name__ == "__main__":
    try:
        build()
    except Exception as exc:  # pragma: no cover
        print(f"build failed: {exc}", file=sys.stderr)
        raise
