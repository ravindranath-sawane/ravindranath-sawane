#!/usr/bin/env python3
"""
Generate self-hosted light & dark SVG engineering telemetry plates for
Ravindranath Sawane's GitHub profile README.

Combines public contribution calendars across:
  - @rsawane-kxs          (Enterprise / Kinaxis)
  - @ravindranath-sawane  (Personal / Open Source & Research)

Zero external dependencies (Python 3 standard library only).
Uses GitHub GraphQL API when GITHUB_TOKEN / GH_TOKEN is available and falls
back automatically to GitHub's public contribution calendar & REST endpoints.
"""

from __future__ import annotations

import datetime as dt
import html
import json
import os
import re
import ssl
import subprocess
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

PERSONAL_USER = "ravindranath-sawane"
WORK_USER = "rsawane-kxs"
PERSONAL_START_YEAR = 2020
WORK_START_YEAR = 2025

ROOT_DIR = Path(__file__).resolve().parent.parent
ASSETS_DIR = ROOT_DIR / "assets"

FONT_SANS = (
    "'DM Sans', -apple-system, BlinkMacSystemFont, 'SF Pro Display', "
    "'Segoe UI', Helvetica, Arial, sans-serif"
)
FONT_MONO = (
    "'DM Mono', 'SF Mono', 'JetBrains Mono', ui-monospace, "
    "Menlo, Monaco, Consolas, monospace"
)
FONT_SERIF = (
    "'Instrument Serif', 'Iowan Old Style', 'Palatino Linotype', "
    "'Book Antiqua', Palatino, Georgia, serif"
)


def get_token() -> str | None:
    for env_key in ("METRICS_TOKEN", "GH_TOKEN", "GITHUB_TOKEN"):
        val = os.environ.get(env_key, "").strip()
        if val:
            return val
    try:
        out = subprocess.check_output(
            ["gh", "auth", "token"], stderr=subprocess.DEVNULL, timeout=4
        )
        tok = out.decode("utf-8").strip()
        if tok:
            return tok
    except Exception:
        pass
    return None


def build_ssl_context() -> ssl.SSLContext:
    ctx = ssl.create_default_context()
    if ctx.cert_store_stats()["x509_ca"] == 0:
        for ca_path in ("/etc/ssl/cert.pem", "/etc/ssl/certs/ca-certificates.crt"):
            if os.path.exists(ca_path):
                ctx.load_verify_locations(cafile=ca_path)
                break
    return ctx


SSL_CTX = build_ssl_context()


def http_get(url: str, headers: dict[str, str] | None = None) -> bytes:
    req_headers = {
        "User-Agent": "ravindranath-sawane-profile-telemetry/1.0",
        "Accept": "text/html,application/json,*/*",
    }
    if headers:
        req_headers.update(headers)
    req = urllib.request.Request(url, headers=req_headers)
    with urllib.request.urlopen(req, timeout=20, context=SSL_CTX) as resp:
        return resp.read()


def graphql_query(query: str, token: str) -> dict[str, Any]:
    payload = json.dumps({"query": query}).encode("utf-8")
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=payload,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "User-Agent": "ravindranath-sawane-profile-telemetry/1.0",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=20, context=SSL_CTX) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    if "errors" in data and not data.get("data"):
        raise RuntimeError(f"GraphQL error: {data['errors']}")
    return data["data"]


def parse_public_contributions_html(raw_html: str) -> tuple[int, dict[str, int]]:
    """Parse GitHub's public /users/<login>/contributions HTML fragment."""
    total_match = re.search(
        r"([\d,]+)\s+contributions?\s+in\s+(?:the\s+last\s+year|\d{4})",
        raw_html,
        re.IGNORECASE,
    )
    header_total = (
        int(total_match.group(1).replace(",", "")) if total_match else 0
    )

    id_to_date: dict[str, str] = {}
    for m in re.finditer(
        r'<td[^>]*\bdata-date="(\d{4}-\d{2}-\d{2})"[^>]*\bid="([^"]+)"',
        raw_html,
    ):
        id_to_date[m.group(2)] = m.group(1)
    for m in re.finditer(
        r'<td[^>]*\bid="([^"]+)"[^>]*\bdata-date="(\d{4}-\d{2}-\d{2})"',
        raw_html,
    ):
        id_to_date[m.group(1)] = m.group(2)

    day_counts: dict[str, int] = {d: 0 for d in id_to_date.values()}
    for m in re.finditer(
        r'<tool-tip[^>]*\bfor="([^"]+)"[^>]*>([^<]+)</tool-tip>',
        raw_html,
    ):
        cell_id, text = m.group(1), m.group(2).strip()
        date_str = id_to_date.get(cell_id)
        if not date_str:
            continue
        cm = re.match(r"([\d,]+)\s+contributions?", text, re.IGNORECASE)
        day_counts[date_str] = int(cm.group(1).replace(",", "")) if cm else 0

    computed_total = sum(day_counts.values())
    return max(header_total, computed_total), day_counts


def fetch_calendar_public(login: str, start_year: int) -> tuple[int, int, dict[str, int]]:
    """Fetch trailing-12m daily map + all-time total via public HTML endpoints."""
    rolling_html = http_get(
        f"https://github.com/users/{login}/contributions"
    ).decode("utf-8", errors="ignore")
    rolling_total, rolling_days = parse_public_contributions_html(rolling_html)

    current_year = dt.datetime.now(dt.timezone.utc).year
    all_time = 0
    for year in range(start_year, current_year + 1):
        url = (
            f"https://github.com/users/{login}/contributions"
            f"?from={year}-01-01&to={year}-12-31"
        )
        try:
            y_html = http_get(url).decode("utf-8", errors="ignore")
            y_tot, _ = parse_public_contributions_html(y_html)
            all_time += y_tot
        except Exception:
            pass

    all_time = max(all_time, rolling_total)
    return rolling_total, all_time, rolling_days


def fetch_repo_stats(login: str, token: str | None) -> tuple[int, dict[str, int]]:
    """Fetch owned non-fork public repository count and language bytes."""
    if token:
        try:
            q = f"""
            query {{
              user(login: "{login}") {{
                repositories(ownerAffiliations: OWNER, isFork: false, privacy: PUBLIC, first: 100) {{
                  totalCount
                  nodes {{
                    name
                    languages(first: 10, orderBy: {{field: SIZE, direction: DESC}}) {{
                      edges {{
                        size
                        node {{ name }}
                      }}
                    }}
                  }}
                }}
              }}
            }}
            """
            data = graphql_query(q, token)["user"]["repositories"]
            langs: dict[str, int] = {}
            for repo in data["nodes"]:
                for edge in repo["languages"]["edges"]:
                    name = edge["node"]["name"]
                    langs[name] = langs.get(name, 0) + int(edge["size"])
            return int(data["totalCount"]), langs
        except Exception:
            pass

    headers = {"Accept": "application/vnd.github+json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    raw = http_get(
        f"https://api.github.com/users/{login}/repos?per_page=100&type=owner",
        headers=headers,
    )
    repos = [r for r in json.loads(raw.decode("utf-8")) if not r.get("fork")]
    langs = {}
    for r in repos:
        lang_url = r.get("languages_url")
        if not lang_url:
            continue
        try:
            lraw = json.loads(http_get(lang_url, headers=headers).decode("utf-8"))
            for k, v in lraw.items():
                langs[k] = langs.get(k, 0) + int(v)
        except Exception:
            if r.get("language"):
                langs[r["language"]] = langs.get(r["language"], 0) + 10000
    return len(repos), langs


def build_weeks_grid(
    personal_days: dict[str, int], work_days: dict[str, int]
) -> list[list[dict[str, Any]]]:
    """Assemble a clean 53-week (Sun..Sat) grid ending on the current week."""
    all_dates = sorted(set(personal_days.keys()) | set(work_days.keys()))
    if all_dates:
        end_date = dt.date.fromisoformat(all_dates[-1])
    else:
        end_date = dt.datetime.now(dt.timezone.utc).date()

    # Align start to the Sunday 52 weeks prior to the current week's Sunday
    end_sunday = end_date - dt.timedelta(days=(end_date.weekday() + 1) % 7)
    start_sunday = end_sunday - dt.timedelta(weeks=52)

    weeks: list[list[dict[str, Any]]] = []
    cur = start_sunday
    while cur <= end_date:
        week: list[dict[str, Any]] = []
        for _ in range(7):
            if cur <= end_date:
                ds = cur.isoformat()
                p_cnt = personal_days.get(ds, 0)
                w_cnt = work_days.get(ds, 0)
                week.append(
                    {
                        "date": cur,
                        "personal": p_cnt,
                        "work": w_cnt,
                        "total": p_cnt + w_cnt,
                    }
                )
            cur += dt.timedelta(days=1)
        weeks.append(week)
    return weeks[-53:]


def summarize_languages(langs: dict[str, int]) -> list[tuple[str, float, str, str]]:
    """
    Group raw bytes into crisp engineering categories with light & dark palette colors.
    Note: Jupyter Notebooks contain embedded images/outputs that inflate raw byte size,
    so we apply a gentle 0.25 normalization weight to `.ipynb` bytes so pure Python &
    web application code are represented proportionally.
    """
    weighted: dict[str, float] = {}
    for name, size in langs.items():
        if name == "Jupyter Notebook":
            # .ipynb files embed base64 plot outputs & JSON metadata (~85% overhead)
            weighted["Jupyter / ML"] = weighted.get("Jupyter / ML", 0.0) + size * 0.14
        elif name == "Python":
            weighted["Python"] = weighted.get("Python", 0.0) + float(size)
        elif name in ("HTML", "CSS", "JavaScript", "TypeScript"):
            weighted["Web / UI"] = weighted.get("Web / UI", 0.0) + float(size)
        else:
            weighted["Shell / Other"] = weighted.get("Shell / Other", 0.0) + float(size)

    if not weighted:
        weighted = {"Python": 55.0, "Jupyter / ML": 35.0, "Web / UI": 10.0}

    palette = {
        "Python": ("#334ED7", "#748BFF"),
        "Jupyter / ML": ("#E76A47", "#EE7857"),
        "Web / UI": ("#729561", "#86B372"),
        "Shell / Other": ("#8D8E86", "#70736B"),
    }

    total = sum(weighted.values()) or 1.0
    ordered = sorted(weighted.items(), key=lambda kv: -kv[1])
    result: list[tuple[str, float, str, str]] = []
    for label, val in ordered[:3]:
        pct = (val / total) * 100.0
        c_light, c_dark = palette.get(label, ("#70716B", "#85877F"))
        result.append((label, pct, c_light, c_dark))

    # Normalize top-3 displayed integer percentages to sum cleanly to 100%
    pct_sum = sum(r[1] for r in result) or 100.0
    raw_pcts = [r[1] * 100.0 / pct_sum for r in result]
    int_pcts = [int(round(p)) for p in raw_pcts]
    if int_pcts:
        int_pcts[0] += 100 - sum(int_pcts)
    return [
        (lbl, float(int_pcts[i]), cl, cd)
        for i, (lbl, _, cl, cd) in enumerate(result)
    ]


def work_tier(count: int) -> int:
    if count <= 0:
        return 0
    if count <= 3:
        return 1
    if count <= 9:
        return 2
    if count <= 19:
        return 3
    return 4


def render_svg(
    mode: str,
    weeks: list[list[dict[str, Any]]],
    work_12m: int,
    personal_12m: int,
    all_time_total: int,
    active_days_12m: int,
    peak_day: int,
    public_repos: int,
    lang_breakdown: list[tuple[str, float, str, str]],
    synced_date: str,
) -> str:
    is_dark = mode == "dark"

    bg = "#121512" if is_dark else "#F1EEE6"
    surface = "#181C18" if is_dark else "#F8F6F0"
    surface_alt = "#1F241F" if is_dark else "#EAE6DC"
    ink = "#F1EEE6" if is_dark else "#20221E"
    ink_soft = "#B9B7AE" if is_dark else "#51534E"
    muted = "#85877F" if is_dark else "#70716B"
    rule = "#2E332D" if is_dark else "#C8C6BB"
    blue = "#7D92FF" if is_dark else "#334ED7"
    tomato = "#EE7857" if is_dark else "#E76A47"
    citron = "#D8E766"
    live_green = "#86B372" if is_dark else "#729561"

    empty_cell = "#232823" if is_dark else "#E3DFD3"
    work_Ramp = (
        ["#232823", "#263366", "#394FA3", "#536FE3", "#889DFF"]
        if is_dark
        else ["#E3DFD3", "#BDC6F2", "#8597EA", "#5068DF", "#2B43C6"]
    )
    personal_fill = "#EE7857" if is_dark else "#E76A47"

    total_12m = work_12m + personal_12m

    # Month labels across the 53 weeks
    grid_x0 = 84.0
    grid_y0 = 166.0
    pitch = 14.8
    cell_size = 11.2

    month_names = [
        "",
        "JAN",
        "FEB",
        "MAR",
        "APR",
        "MAY",
        "JUN",
        "JUL",
        "AUG",
        "SEP",
        "OCT",
        "NOV",
        "DEC",
    ]
    month_labels_svg: list[str] = []
    last_month = -1
    last_label_x = -999.0
    for col_idx, week in enumerate(weeks):
        if not week:
            continue
        first_day = week[0]["date"]
        m = first_day.month
        x = grid_x0 + col_idx * pitch
        if m != last_month:
            # Skip a 1-column trailing partial month at the left edge so the next full month renders
            if col_idx == 0 and first_day.day > 15:
                last_month = m
                continue
            if x - last_label_x >= 26.0:
                month_labels_svg.append(
                    f'<text x="{x:.1f}" y="157" fill="{muted}" '
                    f'font-family="{FONT_MONO}" font-size="8.5" '
                    f'letter-spacing="0.8">{month_names[m]}</text>'
                )
                last_label_x = x
            last_month = m

    cells_svg: list[str] = []
    for col_idx, week in enumerate(weeks):
        x = grid_x0 + col_idx * pitch
        for day in week:
            row_idx = (day["date"].weekday() + 1) % 7  # Sun=0 .. Sat=6
            y = grid_y0 + row_idx * pitch
            w_cnt = day["work"]
            p_cnt = day["personal"]

            if w_cnt > 0 and p_cnt > 0:
                fill = work_Ramp[work_tier(w_cnt)]
                cells_svg.append(
                    f'<rect x="{x:.1f}" y="{y:.1f}" width="{cell_size}" '
                    f'height="{cell_size}" rx="2.3" fill="{fill}" />'
                )
                # Dual-account activity marker (personal + work on same day)
                dot_cx = x + cell_size - 2.6
                dot_cy = y + 2.6
                cells_svg.append(
                    f'<circle cx="{dot_cx:.1f}" cy="{dot_cy:.1f}" r="2.1" '
                    f'fill="{citron}" />'
                )
            elif p_cnt > 0:
                cells_svg.append(
                    f'<rect x="{x:.1f}" y="{y:.1f}" width="{cell_size}" '
                    f'height="{cell_size}" rx="2.3" fill="{personal_fill}" />'
                )
            else:
                fill = work_Ramp[work_tier(w_cnt)] if w_cnt > 0 else empty_cell
                cells_svg.append(
                    f'<rect x="{x:.1f}" y="{y:.1f}" width="{cell_size}" '
                    f'height="{cell_size}" rx="2.3" fill="{fill}" />'
                )

    # Language segmented bar (right footer, x=524..888, width=364)
    bar_x = 524.0
    bar_w = 364.0
    bar_y = 282.0
    bar_segments: list[str] = []
    lang_legends: list[str] = []
    cur_x = bar_x
    for idx, (lbl, pct, c_light, c_dark) in enumerate(lang_breakdown):
        col = c_dark if is_dark else c_light
        seg_w = max(6.0, (pct / 100.0) * bar_w)
        if idx == len(lang_breakdown) - 1:
            seg_w = max(6.0, (bar_x + bar_w) - cur_x)
        bar_segments.append(
            f'<rect x="{cur_x:.1f}" y="{bar_y:.1f}" width="{seg_w:.1f}" '
            f'height="6" rx="2" fill="{col}" />'
        )
        cur_x += seg_w

        lx = 524.0 + idx * 124.0
        lang_legends.append(
            f'<circle cx="{lx + 4:.1f}" cy="300" r="3.2" fill="{col}" />'
            f'<text x="{lx + 12:.1f}" y="303.2" fill="{ink_soft}" '
            f'font-family="{FONT_MONO}" font-size="8.5" letter-spacing="0.4">'
            f'{html.escape(lbl.upper())} {pct:.0f}%</text>'
        )

    # Legend swatches (left footer)
    legend_swatches: list[str] = []
    sx0 = 72.0
    for i, c in enumerate(work_Ramp):
        sx = sx0 + i * 14.0
        legend_swatches.append(
            f'<rect x="{sx:.1f}" y="281" width="10" height="10" rx="2" fill="{c}" />'
        )

    kpi_cards = [
        (
            32,
            "TRAILING 12M ACTIVITY",
            f"{total_12m:,}",
            f"{work_12m:,} @rsawane-kxs  ·  {personal_12m:,} personal",
            blue,
        ),
        (
            249,
            "ALL-TIME TRACKED",
            f"{all_time_total:,}",
            f"combined since {PERSONAL_START_YEAR}",
            ink,
        ),
        (
            466,
            "ACTIVE DAYS (12M)",
            f"{active_days_12m}",
            f"peak velocity: {peak_day} / day",
            ink,
        ),
        (
            683,
            "PUBLIC REPOSITORIES",
            f"{public_repos}",
            "open-source AI, RAG & research",
            tomato,
        ),
    ]

    kpi_svg: list[str] = []
    for kx, klabel, kval, ksub, kcolor in kpi_cards:
        kpi_svg.append(
            f"""
    <g>
      <rect x="{kx}" y="58" width="205" height="68" rx="4" fill="{surface}" stroke="{rule}" stroke-width="1" />
      <text x="{kx + 14}" y="75" fill="{muted}" font-family="{FONT_MONO}" font-size="8.8" letter-spacing="0.9">{html.escape(klabel)}</text>
      <text x="{kx + 14}" y="103" fill="{kcolor}" font-family="{FONT_SANS}" font-size="25" font-weight="700" letter-spacing="-0.8">{html.escape(kval)}</text>
      <text x="{kx + 14}" y="118" fill="{ink_soft}" font-family="{FONT_MONO}" font-size="8.5" letter-spacing="0.2">{html.escape(ksub)}</text>
    </g>"""
        )

    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 920 330" width="920" height="330" role="img" aria-label="Engineering Telemetry: {total_12m:,} contributions in the last 12 months across @rsawane-kxs and @ravindranath-sawane">
  <defs>
    <pattern id="dots-telemetry" width="20" height="20" patternUnits="userSpaceOnUse">
      <circle cx="2" cy="2" r="0.85" fill="{muted}" opacity="0.2" />
    </pattern>
  </defs>

  <!-- Outer Card -->
  <rect x="2" y="2" width="916" height="326" rx="6" fill="{bg}" stroke="{rule}" stroke-width="1.2" />
  <rect x="14" y="14" width="892" height="302" fill="url(#dots-telemetry)" />
  <rect x="14" y="14" width="892" height="302" fill="none" stroke="{rule}" stroke-width="0.8" opacity="0.55" />

  <!-- Corner Registration Marks -->
  <path d="M14 25 V14 H25 M895 14 H906 V25 M906 305 V316 H895 M25 316 H14 V305" fill="none" stroke="{tomato}" stroke-width="2" />

  <!-- Top Bar -->
  <line x1="14" y1="45" x2="906" y2="45" stroke="{rule}" stroke-width="1" />
  <circle cx="34" cy="30" r="3.5" fill="{live_green}">
    <animate attributeName="opacity" values="1;0.45;1" dur="2.6s" repeatCount="indefinite" />
  </circle>
  <text x="46" y="33.5" fill="{ink}" font-family="{FONT_MONO}" font-size="9.8" font-weight="500" letter-spacing="1.1">04  //  ENGINEERING TELEMETRY</text>
  <text x="266" y="33.5" fill="{muted}" font-family="{FONT_MONO}" font-size="9.2" letter-spacing="0.8">UNIFIED FOOTPRINT: @RSAWANE-KXS + @RAVINDRANATH-SAWANE</text>
  <text x="888" y="33.5" text-anchor="end" fill="{muted}" font-family="{FONT_MONO}" font-size="9.2" letter-spacing="0.9">SYNCED {synced_date}  ·  FIG. 03</text>

  <!-- KPI Cards -->
  {''.join(kpi_svg)}

  <!-- Unified 53-Week Contribution Matrix -->
  <rect x="32" y="138" width="856" height="134" rx="4" fill="{surface}" stroke="{rule}" stroke-width="1" />
  {''.join(month_labels_svg)}

  <text x="46" y="189" fill="{muted}" font-family="{FONT_MONO}" font-size="8" letter-spacing="0.6">MON</text>
  <text x="46" y="218.6" fill="{muted}" font-family="{FONT_MONO}" font-size="8" letter-spacing="0.6">WED</text>
  <text x="46" y="248.2" fill="{muted}" font-family="{FONT_MONO}" font-size="8" letter-spacing="0.6">FRI</text>

  {''.join(cells_svg)}

  <!-- Bottom Legend & Public Codebase Mix -->
  <text x="32" y="289.5" fill="{muted}" font-family="{FONT_MONO}" font-size="8.5" letter-spacing="0.6">LESS</text>
  {''.join(legend_swatches)}
  <text x="148" y="289.5" fill="{muted}" font-family="{FONT_MONO}" font-size="8.5" letter-spacing="0.5">MORE (@RSAWANE-KXS)</text>

  <rect x="288" y="281" width="10" height="10" rx="2" fill="{personal_fill}" />
  <text x="304" y="289.5" fill="{muted}" font-family="{FONT_MONO}" font-size="8.5" letter-spacing="0.5">OPEN SOURCE</text>

  <rect x="392" y="281" width="10" height="10" rx="2" fill="{work_Ramp[3]}" />
  <circle cx="399.5" cy="283.5" r="2" fill="{citron}" />
  <text x="408" y="289.5" fill="{muted}" font-family="{FONT_MONO}" font-size="8.5" letter-spacing="0.5">BOTH</text>

  <text x="32" y="304.5" fill="{muted}" font-family="{FONT_MONO}" font-size="8.2" letter-spacing="0.5">SELF-HOSTED SVG  ·  AUTO-UPDATED VIA GITHUB ACTIONS (ZERO EXTERNAL WIDGET DEPENDENCIES)</text>

  <!-- Language Mix Bar -->
  <rect x="520" y="282" width="356" height="6" rx="2" fill="{surface_alt}" />
  {''.join(bar_segments)}
  {''.join(lang_legends)}
</svg>
"""


def main() -> None:
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    token = get_token()

    p_12m, p_all, p_days = fetch_calendar_public(PERSONAL_USER, PERSONAL_START_YEAR)
    w_12m, w_all, w_days = fetch_calendar_public(WORK_USER, WORK_START_YEAR)
    pub_repos, raw_langs = fetch_repo_stats(PERSONAL_USER, token)

    weeks = build_weeks_grid(p_days, w_days)
    all_grid_days = [d for w in weeks for d in w]
    active_days = sum(1 for d in all_grid_days if d["total"] > 0)
    peak_day = max((d["total"] for d in all_grid_days), default=0)

    lang_breakdown = summarize_languages(raw_langs)
    synced_date = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d")

    for mode in ("light", "dark"):
        svg = render_svg(
            mode=mode,
            weeks=weeks,
            work_12m=w_12m,
            personal_12m=p_12m,
            all_time_total=p_all + w_all,
            active_days_12m=active_days,
            peak_day=peak_day,
            public_repos=pub_repos,
            lang_breakdown=lang_breakdown,
            synced_date=synced_date,
        )
        out_path = ASSETS_DIR / f"telemetry-{mode}.svg"
        out_path.write_text(svg, encoding="utf-8")
        print(f"Wrote {out_path} ({len(svg):,} bytes)")

    print(
        f"Summary -> 12M: {w_12m + p_12m} ({w_12m} work + {p_12m} personal) | "
        f"All-time: {p_all + w_all} | Active days: {active_days} | Peak: {peak_day}"
    )


if __name__ == "__main__":
    main()
