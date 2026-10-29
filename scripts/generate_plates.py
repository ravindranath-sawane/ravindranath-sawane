#!/usr/bin/env python3
"""
Generate self-hosted light & dark editorial SVG plates for Ravindranath Sawane's
GitHub profile README, aligned with the visual language of ravindranath-sawane.github.io:
  - assets/hero-light.svg  & assets/hero-dark.svg   (FIG. 01)
  - assets/stack-light.svg & assets/stack-dark.svg  (FIG. 02)
"""

from __future__ import annotations

import html
from pathlib import Path

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
FONT_SERIF = "Georgia, Times, serif"


def palette(mode: str) -> dict[str, str]:
    is_dark = mode == "dark"
    return {
        "bg": "#121512" if is_dark else "#F1EEE6",
        "surface": "#181C18" if is_dark else "#F8F6F0",
        "surface_alt": "#1F241F" if is_dark else "#EAE6DC",
        "terminal": "#101310" if is_dark else "#EDE9DF",
        "ink": "#F1EEE6" if is_dark else "#20221E",
        "ink_inv": "#121512" if is_dark else "#F1EEE6",
        "ink_soft": "#B9B7AE" if is_dark else "#51534E",
        "muted": "#85877F" if is_dark else "#70716B",
        "rule": "#2E332D" if is_dark else "#C8C6BB",
        "blue": "#8CA0FF" if is_dark else "#334ED7",
        "blue_solid": "#3B56E0" if is_dark else "#334ED7",
        "tomato": "#EE7857" if is_dark else "#E76A47",
        "citron": "#D8E766",
        "citron_op": "0.28" if is_dark else "0.95",
        "live_green": "#86B372" if is_dark else "#729561",
    }


def render_hero(mode: str) -> str:
    c = palette(mode)

    stages = [
        ("01", "Intake", "intent", False),
        ("02", "Design", "plan · route", False),
        ("03", "Build", "MCP · tools", False),
        ("04", "Review", "human gate", True),
    ]

    stage_cards: list[str] = []
    xs = [512, 607, 702, 797]
    for idx, (num, title, sub, highlighted) in enumerate(stages):
        x = xs[idx]
        border = c["blue"] if highlighted else c["rule"]
        bw = "1.4" if highlighted else "1"
        badge_fill = c["blue_solid"] if highlighted else c["surface_alt"]
        badge_txt = "#FFFFFF" if highlighted else c["muted"]

        if idx == 0:
            glyph = (
                f'<line x1="{x + 14}" y1="138" x2="{x + 34}" y2="138" stroke="{c["ink"]}" stroke-width="1.6" stroke-linecap="round"/>'
                f'<line x1="{x + 14}" y1="144" x2="{x + 28}" y2="144" stroke="{c["muted"]}" stroke-width="1.6" stroke-linecap="round"/>'
                f'<line x1="{x + 14}" y1="150" x2="{x + 23}" y2="150" stroke="{c["tomato"]}" stroke-width="1.6" stroke-linecap="round"/>'
            )
        elif idx == 1:
            glyph = (
                f'<circle cx="{x + 17}" cy="144" r="2.5" fill="{c["blue"]}"/>'
                f'<circle cx="{x + 31}" cy="138" r="2.3" fill="{c["ink"]}"/>'
                f'<circle cx="{x + 31}" cy="150" r="2.3" fill="{c["tomato"]}"/>'
                f'<path d="M{x + 19} 143 L{x + 29} 138.5 M{x + 19} 145 L{x + 29} 149.5" stroke="{c["muted"]}" stroke-width="1.2"/>'
            )
        elif idx == 2:
            glyph = (
                f'<rect x="{x + 14}" y="136" width="20" height="15" rx="2.5" fill="none" stroke="{c["ink"]}" stroke-width="1.3"/>'
                f'<path d="M{x + 20} 143.5 H{x + 28} M{x + 24} 139.5 V147.5" stroke="{c["blue"]}" stroke-width="1.4" stroke-linecap="round"/>'
            )
        else:
            glyph = (
                f'<circle cx="{x + 23}" cy="143.5" r="8" fill="none" stroke="{c["blue"]}" stroke-width="1.4"/>'
                f'<path d="M{x + 19.5} 143.8 L{x + 22.2} 146.5 L{x + 27} 140.8" fill="none" stroke="{c["live_green"]}" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"/>'
            )

        stage_cards.append(
            f"""
    <g>
      <rect x="{x}" y="108" width="79" height="86" rx="4" fill="{c['bg']}" stroke="{border}" stroke-width="{bw}" />
      <rect x="{x + 10}" y="116" width="24" height="13" rx="2" fill="{badge_fill}" />
      <text x="{x + 22}" y="125.5" text-anchor="middle" fill="{badge_txt}" font-family="{FONT_MONO}" font-size="8.2" font-weight="500">{num}</text>
      {glyph}
      <text x="{x + 12}" y="171" fill="{c['ink']}" font-family="{FONT_SANS}" font-size="12.5" font-weight="700" letter-spacing="-0.2">{title}</text>
      <text x="{x + 12}" y="184" fill="{c['muted']}" font-family="{FONT_MONO}" font-size="8.3">{sub}</text>
    </g>"""
        )

    connectors: list[str] = []
    for gx in (591, 686, 781):
        connectors.append(
            f'<line x1="{gx + 2}" y1="151" x2="{gx + 14}" y2="151" stroke="{c["rule"]}" stroke-width="1.3" />'
            f'<path d="M{gx + 10.5} 147.8 L{gx + 14.2} 151 L{gx + 10.5} 154.2" fill="none" stroke="{c["muted"]}" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round" />'
        )

    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 920 384" width="920" height="384" role="img" aria-label="Ravindranath Sawane — Software Developer I, AI Innovation at Kinaxis. I build AI for the messy middle.">
  <defs>
    <pattern id="dots-hero" width="20" height="20" patternUnits="userSpaceOnUse">
      <circle cx="2" cy="2" r="0.85" fill="{c['muted']}" opacity="0.2" />
    </pattern>
  </defs>

  <!-- Outer Architectural Frame -->
  <rect x="2" y="2" width="916" height="380" rx="6" fill="{c['bg']}" stroke="{c['rule']}" stroke-width="1.2" />
  <rect x="14" y="14" width="892" height="356" fill="url(#dots-hero)" />
  <rect x="14" y="14" width="892" height="356" fill="none" stroke="{c['rule']}" stroke-width="0.8" opacity="0.55" />

  <!-- Signature Tomato Corner Registration Marks -->
  <path d="M14 25 V14 H25 M895 14 H906 V25 M906 359 V370 H895 M25 370 H14 V359" fill="none" stroke="{c['tomato']}" stroke-width="2" />

  <!-- Top Metadata Bar -->
  <line x1="14" y1="46" x2="906" y2="46" stroke="{c['rule']}" stroke-width="1" />
  <circle cx="34" cy="30" r="6.5" fill="{c['live_green']}" opacity="0.22">
    <animate attributeName="r" values="3.5;7.5;3.5" dur="2.8s" repeatCount="indefinite" />
    <animate attributeName="opacity" values="0.35;0.06;0.35" dur="2.8s" repeatCount="indefinite" />
  </circle>
  <circle cx="34" cy="30" r="3.5" fill="{c['live_green']}" />
  <text x="47" y="33.5" fill="{c['muted']}" font-family="{FONT_MONO}" font-size="9.5" letter-spacing="1.1">TORONTO, CANADA   ·   43° 39′ N  /  79° 23′ W</text>
  <text x="888" y="33.5" text-anchor="end" fill="{c['ink']}" font-family="{FONT_MONO}" font-size="9.5" font-weight="500" letter-spacing="0.9">KINAXIS  ·  SOFTWARE DEVELOPER I, AI INNOVATION</text>

  <!-- Center Vertical Divider -->
  <line x1="478" y1="46" x2="478" y2="338" stroke="{c['rule']}" stroke-width="1" />

  <!-- LEFT COLUMN: Editorial Copy -->
  <rect x="36" y="75" width="20" height="1.8" fill="{c['tomato']}" />
  <text x="66" y="79" fill="{c['muted']}" font-family="{FONT_MONO}" font-size="9.8" letter-spacing="1.3">AI ENGINEER  ·  SYSTEMS THINKER</text>

  <!-- Author Monogram & Name -->
  <circle cx="49" cy="109" r="13" fill="{c['ink']}" />
  <text x="47.5" y="113.5" text-anchor="middle" fill="{c['ink_inv']}" font-family="{FONT_SERIF}" font-style="italic" style="font-style: italic" font-size="14.5">rs</text>
  <circle cx="57" cy="101" r="2.2" fill="{c['tomato']}" />
  <text x="70" y="114" fill="{c['ink']}" font-family="{FONT_SANS}" font-size="14.5" font-weight="600" letter-spacing="-0.2">Ravindranath Sawane</text>

  <!-- Display Headline -->
  <text x="36" y="164" fill="{c['ink']}" font-family="{FONT_SANS}" font-size="42" font-weight="700" letter-spacing="-1.4">I build AI for</text>
  <rect x="106" y="201" width="266" height="9.5" rx="1.5" fill="{c['citron']}" opacity="{c['citron_op']}" transform="rotate(-1.2 239 205)" />
  <text x="36" y="208" fill="{c['ink']}" font-family="{FONT_SANS}" font-size="42" font-weight="700" letter-spacing="-1.4">the</text>
  <text x="108" y="208" fill="{c['blue']}" font-family="{FONT_SERIF}" font-style="italic" style="font-style: italic" font-size="46" letter-spacing="-0.4">messy middle.</text>

  <!-- Editorial Deck -->
  <text x="36" y="244" fill="{c['ink_soft']}" font-family="{FONT_SANS}" font-size="13.2">When a good idea meets real work—tools, context, handoffs,</text>
  <text x="36" y="264" fill="{c['ink_soft']}" font-family="{FONT_SANS}" font-size="13.2">edge cases—I build the system that gets it through.</text>

  <!-- Portfolio Pill & Degree -->
  <rect x="36" y="288" width="234" height="32" rx="16" fill="{c['blue_solid']}" />
  <text x="54" y="308" fill="#FFFFFF" font-family="{FONT_MONO}" font-size="10.2" letter-spacing="0.3">ravindranath-sawane.github.io</text>
  <text x="247" y="308.5" fill="{c['citron']}" font-family="{FONT_SANS}" font-size="13" font-weight="700">↗</text>
  <text x="284" y="308" fill="{c['muted']}" font-family="{FONT_MONO}" font-size="9.2" letter-spacing="0.6">M.Sc. CS (AI) · WESTERN</text>

  <!-- RIGHT COLUMN: Field Study 001 Diagram -->
  <rect x="498" y="62" width="390" height="260" rx="5" fill="{c['surface']}" stroke="{c['rule']}" stroke-width="1" />
  <text x="514" y="82" fill="{c['muted']}" font-family="{FONT_MONO}" font-size="9" letter-spacing="1.0">FIELD STUDY  001</text>
  <text x="872" y="82" text-anchor="end" fill="{c['tomato']}" font-family="{FONT_MONO}" font-size="9" letter-spacing="0.9">FROM INTENT TO SOFTWARE</text>
  <line x1="498" y1="93" x2="888" y2="93" stroke="{c['rule']}" stroke-width="1" />

  <!-- Connectors & Stage Cards -->
  {''.join(connectors)}
  {''.join(stage_cards)}

  <!-- Animated Signal Runner Packet across Pipeline -->
  <circle r="4" fill="{c['blue']}" opacity="0.9">
    <animateMotion dur="4.6s" repeatCount="indefinite" path="M 551 151 L 646 151 L 741 151 L 836 151" />
    <animate attributeName="opacity" values="0;1;1;1;0" keyTimes="0;0.08;0.5;0.9;1" dur="4.6s" repeatCount="indefinite" />
  </circle>

  <!-- Human Approval Gate Strip -->
  <rect x="512" y="206" width="364" height="26" rx="3" fill="{c['surface_alt']}" stroke="{c['rule']}" stroke-width="0.8" />
  <text x="524" y="222.5" fill="{c['ink']}" font-family="{FONT_MONO}" font-size="8.8" font-weight="500" letter-spacing="0.6">↳ HUMAN APPROVAL CHECKPOINT</text>
  <text x="864" y="222.5" text-anchor="end" fill="{c['muted']}" font-family="{FONT_MONO}" font-size="8.5" letter-spacing="0.6">A2A · MCP · OTEL</text>

  <!-- Console Status Readout -->
  <rect x="512" y="240" width="364" height="28" rx="3" fill="{c['terminal']}" stroke="{c['rule']}" stroke-width="0.8" />
  <text x="524" y="257.5" fill="{c['live_green']}" font-family="{FONT_MONO}" font-size="8.8" font-weight="600">✓</text>
  <text x="536" y="257.5" fill="{c['ink_soft']}" font-family="{FONT_MONO}" font-size="8.6" letter-spacing="0.5">CONTEXT GROUNDED   ·   ↗ PLAN &amp; DIFF READY</text>
  <rect x="854" y="249" width="5.5" height="11" fill="{c['tomato']}">
    <animate attributeName="opacity" values="1;0.15;1" dur="1.15s" repeatCount="indefinite" />
  </rect>

  <!-- Diagram Caption Footer -->
  <line x1="498" y1="282" x2="888" y2="282" stroke="{c['rule']}" stroke-width="0.8" />
  <text x="514" y="304" fill="{c['muted']}" font-family="{FONT_MONO}" font-size="8.4" letter-spacing="0.6">THE PROMPT IS THE STARTING POINT. NOT THE PRODUCT.</text>
  <text x="872" y="304" text-anchor="end" fill="{c['ink']}" font-family="{FONT_MONO}" font-size="8.8" font-weight="600" letter-spacing="0.8">FIG. 01</text>

  <!-- Bottom Strip -->
  <line x1="14" y1="338" x2="906" y2="338" stroke="{c['rule']}" stroke-width="1" />
  <text x="36" y="358" fill="{c['muted']}" font-family="{FONT_MONO}" font-size="9" letter-spacing="0.9">AGENTIC SYSTEMS  /  ENTERPRISE RAG  /  APPLIED ML</text>
  <text x="498" y="358" fill="{c['ink_soft']}" font-family="{FONT_MONO}" font-size="9" letter-spacing="0.5">−30% DEV LIFECYCLE  ·  84% NL→MQL ACCURACY</text>
  <text x="888" y="358" text-anchor="end" fill="{c['tomato']}" font-family="{FONT_MONO}" font-size="9" font-weight="500" letter-spacing="0.8">INBOX OPEN ↗</text>
</svg>
"""


def render_stack(mode: str) -> str:
    c = palette(mode)

    columns = [
        (
            32,
            "01 / AGENTIC & LLM",
            "Orchestration",
            c["tomato"],
            [
                "MCP & A2A Protocols",
                "Google Cloud ADK",
                "LangChain · LangGraph",
                "Gemini · OpenAI · Vertex AI",
                "Self-Correction Loops",
            ],
        ),
        (
            248,
            "02 / RETRIEVAL & ML",
            "Intelligence",
            c["blue"],
            [
                "Parent-Document RAG",
                "PyTorch · TensorFlow",
                "LSTM · GRU · TCN · YOLO",
                "ChromaDB · Vector Search",
                "NL-to-MQL Translation",
            ],
        ),
        (
            464,
            "03 / CLOUD & RUNTIME",
            "Infrastructure",
            c["tomato"],
            [
                "Kubernetes (AKS · GKE)",
                "Google Cloud & Azure AI",
                "Databricks · BigQuery",
                "Docker · Helm · Argo",
                "GitHub Actions CI/CD",
            ],
        ),
        (
            680,
            "04 / SYSTEMS & OPS",
            "Reliability",
            c["blue"],
            [
                "Python · SQL · C++",
                "FastAPI · PostgreSQL",
                "OpenTelemetry Tracing",
                "Human Approval Gates",
                "Eval & Regression Suites",
            ],
        ),
    ]

    col_svg: list[str] = []
    for cx, kicker, heading, accent, items in columns:
        rows = []
        for r_idx, item in enumerate(items):
            ry = 110 + r_idx * 22
            rows.append(
                f'<rect x="{cx}" y="{ry - 11}" width="196" height="18" rx="2.5" fill="{c["surface"]}" stroke="{c["rule"]}" stroke-width="0.7" />'
                f'<circle cx="{cx + 10}" cy="{ry - 2}" r="2" fill="{accent}" />'
                f'<text x="{cx + 19}" y="{ry + 1.5}" fill="{c["ink_soft"]}" font-family="{FONT_MONO}" font-size="9.2" letter-spacing="0.2">{html.escape(item)}</text>'
            )
        col_svg.append(
            f"""
    <g>
      <text x="{cx}" y="68" fill="{accent}" font-family="{FONT_MONO}" font-size="8.8" font-weight="500" letter-spacing="0.9">{html.escape(kicker)}</text>
      <text x="{cx}" y="88" fill="{c['ink']}" font-family="{FONT_SANS}" font-size="15.5" font-weight="700" letter-spacing="-0.3">{html.escape(heading)}</text>
      {''.join(rows)}
    </g>"""
        )

    principles = [
        (
            32,
            "A",
            c["blue_solid"],
            "#FFFFFF",
            "Give it context",
            "Ground answers in traceable source docs.",
        ),
        (
            322,
            "B",
            c["tomato"],
            "#FFFFFF",
            "Let it do useful work",
            "Scoped tools & state—not infinite freedom.",
        ),
        (
            612,
            "C",
            c["ink"],
            c["ink_inv"],
            "Make it reviewable",
            "Keep humans in control of key decisions.",
        ),
    ]

    prin_svg: list[str] = []
    for px, letter, bfill, btxt, ptitle, pdesc in principles:
        prin_svg.append(
            f"""
    <g>
      <rect x="{px}" y="242" width="22" height="22" rx="4" fill="{bfill}" />
      <text x="{px + 11}" y="256.8" text-anchor="middle" fill="{btxt}" font-family="{FONT_MONO}" font-size="10.5" font-weight="700">{letter}</text>
      <text x="{px + 32}" y="252" fill="{c['ink']}" font-family="{FONT_SANS}" font-size="12.5" font-weight="700" letter-spacing="-0.2">{html.escape(ptitle)}</text>
      <text x="{px + 32}" y="267" fill="{c['muted']}" font-family="{FONT_SANS}" font-size="11">{html.escape(pdesc)}</text>
    </g>"""
        )

    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 920 302" width="920" height="302" role="img" aria-label="Systems Architecture and Engineering Design Principles">
  <defs>
    <pattern id="dots-stack" width="20" height="20" patternUnits="userSpaceOnUse">
      <circle cx="2" cy="2" r="0.85" fill="{c['muted']}" opacity="0.2" />
    </pattern>
  </defs>

  <!-- Outer Card -->
  <rect x="2" y="2" width="916" height="298" rx="6" fill="{c['bg']}" stroke="{c['rule']}" stroke-width="1.2" />
  <rect x="14" y="14" width="892" height="274" fill="url(#dots-stack)" />

  <!-- Recessed Bottom Design Principles Band -->
  <rect x="14" y="224" width="892" height="64" fill="{c['surface_alt']}" />
  <rect x="14" y="14" width="892" height="274" fill="none" stroke="{c['rule']}" stroke-width="0.8" opacity="0.55" />

  <!-- Corner Registration Marks -->
  <path d="M14 25 V14 H25 M895 14 H906 V25 M906 277 V288 H895 M25 288 H14 V277" fill="none" stroke="{c['tomato']}" stroke-width="2" />

  <!-- Header Bar -->
  <line x1="14" y1="45" x2="906" y2="45" stroke="{c['rule']}" stroke-width="1" />
  <rect x="32" y="28.5" width="16" height="1.8" fill="{c['tomato']}" />
  <text x="56" y="33.5" fill="{c['ink']}" font-family="{FONT_MONO}" font-size="9.8" font-weight="500" letter-spacing="1.1">01  //  ARCHITECTURE &amp; WORKING STACK</text>
  <text x="888" y="33.5" text-anchor="end" fill="{c['muted']}" font-family="{FONT_MONO}" font-size="9.2" letter-spacing="0.9">WHAT HAPPENS AFTER THE DEMO?  ·  FIG. 02</text>

  <!-- Column Dividers -->
  <line x1="238" y1="54" x2="238" y2="216" stroke="{c['rule']}" stroke-width="0.8" opacity="0.7" />
  <line x1="454" y1="54" x2="454" y2="216" stroke="{c['rule']}" stroke-width="0.8" opacity="0.7" />
  <line x1="670" y1="54" x2="670" y2="216" stroke="{c['rule']}" stroke-width="0.8" opacity="0.7" />

  <!-- 4 Capability Columns -->
  {''.join(col_svg)}

  <!-- Principles Divider & Three Pillars -->
  <line x1="14" y1="224" x2="906" y2="224" stroke="{c['rule']}" stroke-width="1" />
  {''.join(prin_svg)}
</svg>
"""


def main() -> None:
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    for mode in ("light", "dark"):
        hero_path = ASSETS_DIR / f"hero-{mode}.svg"
        stack_path = ASSETS_DIR / f"stack-{mode}.svg"
        hero_svg = render_hero(mode)
        stack_svg = render_stack(mode)
        hero_path.write_text(hero_svg, encoding="utf-8")
        stack_path.write_text(stack_svg, encoding="utf-8")
        print(f"Wrote {hero_path} ({len(hero_svg):,} bytes)")
        print(f"Wrote {stack_path} ({len(stack_svg):,} bytes)")


if __name__ == "__main__":
    main()
