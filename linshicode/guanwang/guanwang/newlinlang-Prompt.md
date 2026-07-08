# ROLE

You are the Creative Director, Lead Brand Designer, Senior Frontend Engineer, Motion Designer, and Typography Expert for this project.

You are not decorating a pitch deck.

You are rebuilding the official website of LinknLatch — a flagship page for investors and brand partners that should feel like a bold print magazine that came alive in the browser.

The final result should make a visitor stop and think:

"This is the most creative, most engineering-driven MCN in cross-border commerce."

Everything must feel physical, playful, confident, handcrafted and expensive.

Never use generic layouts.

Never use template designs.

Never drift into dark-tech AI clichés — this brand lives on paper, not in space.

Always think before coding.

----------------------------------------------------

# DELIVERABLE

One single self-contained file: `newlinlang.html`

Located in the same folder as `linlang.html`.

No build step.

No frameworks.

No external JavaScript libraries.

Vanilla HTML + CSS + JavaScript only.

Sanctioned exception: three.js (r14x) may be embedded INLINE solely for the hero rubber-stamp. It must stay fx-gated (html.fx + WebGL detection), fall back to the 2D SVG stamp in every other state (no-fx, reduced motion, WebGL refused), and render token colors only with toon shading + inverted-hull outline — no gradients, glow, or sci-fi materials. No other library use is permitted.

Google Fonts allowed, exactly three families: Bebas Neue · DM Sans · Caveat.

Chinese text falls back to system fonts (PingFang SC / Microsoft YaHei) — do not load CJK webfonts.

The file must open perfectly from the local filesystem (file://) with zero console errors.

----------------------------------------------------

# COMPANY

中文名

淋浪 LinknLatch · 杭州淋浪信息技术有限公司

English

LinknLatch Inc.

Positioning

在中国企业出海领域最 AI-NATIVE 的一家 MCN

The Most AI-Native MCN for Chinese Brands Going Global

Core Thesis

AIGC + Agent 双引擎 = AIUGC 服务

Agent solves "who sells" · AIGC solves "what content sells"

HQ

Hangzhou / Los Angeles

CEO

李西 Lisy Li

Page Purpose

公司介绍 · 投资合作 (formerly BP v3.0 — now the flagship official site)

----------------------------------------------------

# AUDIENCE

Primary: investors and brand partners, Chinese-first.

Secondary: English-speaking partners and platform contacts.

The site is fully bilingual: 中文 + English.

Language is switchable in the nav and persisted in localStorage.

Default language: 中文.

----------------------------------------------------

# CONTENT SOURCE — SINGLE SOURCE OF TRUTH

All copy, numbers, names and claims come from `linlang.html` in the same folder.

Content parity is a HARD requirement. The new site must contain ALL of the following, in both languages:

1. Hero positioning — 最 AI-NATIVE MCN · AIGC + Agent 双引擎 · 6 license pills (ISV / TSP / CAP / TTO / TAP / ADS) · CEO byline
2. Marquee value props — $25M+ 月 GMV 峰值 · 100,000+ 美区达人池 · 5,000+ AI 形象授权 · 6 张牌照全家桶
3. Key metrics — $25M+ monthly GMV peak · $1M AI-driven monthly volume · $2-3M monthly revenue · US Top 3 TSP
4. Talent network — 10w+ 合作达人池 · 1w+ 签约达人 (TTO 北美第一) · 5,000 真人形象授权
5. Six licenses, each explained — TSP · ISV · TAP · CAP · TTO · US ADS (周受资亲签 / signed by Shou Zi Chew)
6. 200+ brand partner wall — keep the full brand list (Kind Patches, GNC, POP MART, DREAME, Coca-Cola, The Ordinary, tarte, MINISO, Halara, eufy by Anker, Alibaba.com … through "+ 100 more")
7. AI e-commerce category results — all 8 category cards (SPRINGORIGIN 10,000 · DREAME $70K · GNC $770K · KATCH ME $2.15M · GEOOROOD $22K · AMOS $45K · MINISO $48K · SONGMICS $30K)
8. Ad agency cases — GNC $2M+ · DREAME $6M+ · AMOS $409K+ · GEOOROOD $79K+
9. StockX case study — 4-step test rig + data backflow note ("一周测评 > 三个月空想")
10. Dual engine — Engine ① Agent (智能建联, 日触达 10 万+, 95% 自动化) · Engine ② AIGC (5,000+ 形象池, 日产 1,000+ 条, 单条验证 $10K GMV) · "why both engines" note
11. Linsey — the AI talent agent outer layer + 5-step pipeline (Route → Negotiate → Consolidate → Fulfill → Retain)
12. 5-layer Self-Evolving stack — L5 Optimization · L4 Strategy · L3 Purpose (5 agents) · L2 Channel · L1 Data
13. AIGC methodology — 1→100 爆款复刻 thesis · "物归原主" 3-step flow · 3 edges · technical thesis note
14. Three-tier pricing — $5 Basic (300 min) · $20 Standard (200 min, recommended) · $35 Premium (100 min)
15. Revenue model — Layer 1 Marketing ($1M-2M/mo) · Layer 2 Commission TAP (10-15% take rate) · Layer 3 Financial Arbitrage · margin honesty card · use-of-funds card
16. Team — LISY LI · CHI ZHANG · MR. K · MR. A, full bios and strategic-value sidebars
17. The Deal — Structure A ($2M · 10% equity, $20M post-money) · Structure B ($2M · 8% APR debt) · 3 investor benefits · use of funds 40% / 35% / 25%
18. Closing — AIGC + AGENT 双引擎驱动出海 · 一万达人 · 五千形象
19. Footer — © 2026 LinknLatch · Confidential — For Authorized Investors Only

Rules:

Never invent numbers, brands, quotes or logos.

Never drop a zh/en pair — every visible string exists in both languages.

You may tighten and re-typeset copy for impact, but facts are immutable.

----------------------------------------------------

# DESIGN SYSTEM — LOCKED (from LinknLatch_DesignSystem.docx)

## Colors (CSS custom properties on :root)

--cream: #F0EBE0 — primary page background (never pure white)

--cream2: #E8E3D5 — alternate band background

--black: #111111 — borders, text, shadows, dark bands (never pure #000)

--white: #FFFFFF — card fills, inputs

--green: #1DBA6A — primary CTA / accent

--green-dark: #0FA355 — headline highlights, hovers, checks

--green-light: #D4F5E2 — band backgrounds, success

--purple: #E8DFFF — pastel card fill

--peach: #FFE8D4 — pastel card fill

--yellow: #FEFFC2 — pastel card fill, stickers

--muted: #666666 — secondary text

--accent3: #7B61FF — stat-number purple

--orange-dark: #C0510A — stat-number orange

No new colors. No gradients as section backgrounds. Pastels are always solid fills.

## Typography

Bebas Neue — ALL display text: hero, section titles, stats, card titles. Always naturally ALL-CAPS.

DM Sans (300-700) — all body, labels, buttons, nav.

Caveat (600-700) — handwritten stickers, annotations, margin notes.

Hero H1: clamp(3.2rem, 7.5vw, 5.8rem) · line-height ≤ 1.02

Section H2: clamp(2.2rem, 5vw, 3.6rem) · line-height ~1.05

Highlighted words inside headlines use --green-dark (span.hl).

Body max-width capped for readable measure.

## Borders · Shadows · Radius — the "lifted paper" system

All shadows are FLAT OFFSET, solid #111111, ZERO blur.

Scale: 2px / 3px / 4px / 5px / 6px / 8px offsets.

Borders: 2px small elements · 3px cards and boxes, always #111111.

Radius scale: 8px stickers · 10-12px inputs · 14-18px small cards · 18-20px cards · 24px hero boxes · 100px pills.

Hover: element translates(-2px to -3px, -2px to -3px) AND shadow offset grows +2-3px, simultaneously.

Active/press: translate back to (0,0), shadow shrinks to 1-2px.

## Motion tokens

Scroll reveal: IntersectionObserver, threshold ~0.1, 0.6-0.7s ease.

Marquee: translateX 0 → -50%, ~30s linear infinite, duplicated content.

Transitions: 0.15-0.25s for hovers. Physical easing (cubic-bezier), never linear for entrances.

Respect prefers-reduced-motion: disable entrances and marquee drift.

----------------------------------------------------

# WEBSITE STRUCTURE (narrative order)

1. Sticky Nav — logo, section links, language toggle, thin green scroll-progress bar
2. Hero — the typographic monument
3. Marquee ticker — full-bleed green band
4. Proof / Validation — metrics, talent network, six licenses, brand wall, category results, ad cases, StockX rig
5. AIUGC Core — the dual engine
6. Agent Stack — Linsey + the 5-layer architecture
7. AIGC Method — 1→100 thesis, 物归原主 flow, edges, pricing
8. Revenue Model — three layers + honesty card
9. Team — four character cards
10. The Deal — dark band, two structures, benefits, use of funds
11. Closing CTA
12. Footer

Every section must have a UNIQUE composition. See the Anti-AI prompt.

----------------------------------------------------

# SECTION EXPECTATIONS

## HERO

The hero is a typographic monument, not a picture.

Stacked Bebas Neue display lines at maximum scale — "最 AI-NATIVE" as the green punch word.

Caveat handwritten annotations orbit the headline like margin notes on a founder's desk ("AIGC + Agent 双引擎", arrows, underlines).

The 6 license pills feel like collectible stamps — slightly rotated, hover straightens them.

A rotating sticker or stamp badge ("EST. 2023 · HZ / LA") adds print-shop energy.

Staggered entrance: each display line slides/rotates in with physical easing; pills pop in one by one.

## MARQUEE

Full-bleed green band with black borders, scrolling value props, ★ separators.

Pause on hover.

## PROOF

This is the densest section — choreograph density, don't dump grids.

Key metrics: oversized Bebas numbers that COUNT UP on first reveal.

Talent network: the black card with green stats stays a black "drop" moment.

Six licenses: six collectible cards, each pastel-coded, the US ADS card black with green text ("周受资亲签" is a highlight moment — give it a Caveat annotation or seal).

Brand wall: keep the black box, but let brand cells drift in as a subtle masonry or dual-row marquee — 90 names should feel like abundance, not a spreadsheet.

Category results and ad cases: vary the composition (offset grid, mixed card sizes) — not four identical rows.

StockX: numbered rig steps as a connected sequence, note-box punchline in black.

## AIUGC CORE

Two engine cards (purple / peach) presented as a true PAIR — visually interlocking or facing each other, "=" typography between them (AIGC + Agent = AIUGC).

The "why both engines" note-box is the section's mic-drop: black box, green shadow.

## AGENT STACK

Linsey gets a personality moment — signature "— Linsey" in Caveat.

5-step pipeline: horizontally connected steps with numbered stamps.

The 5-layer stack (L5→L1): a physical stack of colored layers, slightly offset like a pile of paper — scroll reveals it layer by layer. This diagram is the engineering centerpiece; make it feel architectural.

## AIGC METHOD

1→100 thesis headline treatment.

物归原主 3 steps: three cards where step 03 is the green payoff.

Pricing: three tilted price cards (±1-2deg), the recommended $20 card black with green shadow and a floating "★ RECOMMEND" badge, straightening on hover.

## REVENUE

Three horizontal layer bars (peach / purple / green) with big data-pills — each layer visually wider or more prominent than the last is NOT required; instead give each a distinct left column with huge Bebas labels.

Margin honesty card ("坦诚表达：还不算特别高") keeps its candid tone — candor is a brand asset.

## TEAM

Four large character cards — think trading cards / baseball cards.

Tag chips (CO-FOUNDER & CEO etc.) float above the card edge.

MR. K and MR. A keep their mystery: consider a subtle "?" watermark or redacted-style flourish, NDA note in Caveat italic.

## THE DEAL

Full black band — the emotional drop before the close.

Structure A (green-bordered) vs Structure B (white-bordered) as a true side-by-side decision.

Three benefit cards + 40/35/25 use-of-funds bars (animated width on reveal).

## CLOSING

Return to cream. Huge Bebas closing statement, Caveat sign-off from the CEO, single green CTA feeling (mailto link acceptable).

----------------------------------------------------

# INTERACTIONS

Language toggle — zh/en pill in nav, persisted via localStorage, updates <html lang>.

Scroll progress — 3px green bar under the nav border.

Scroll reveal — VARIED choreography per section: slide-up, slide-from-side, rotate-settle, stagger. Never one uniform fade.

Count-up numbers — animate once when metrics enter viewport (respect reduced motion: show final values).

Marquee — pause on hover.

Hovers — every interactive element obeys the lift physics (translate + shadow delta). Buttons press down on :active.

Nav links — smooth scroll to anchors; current section highlighted.

All interactions keyboard-accessible; visible :focus-visible states using the green focus ring (3px 3px 0 #0FA355).

----------------------------------------------------

# PERFORMANCE

No external JS. No images required — everything is CSS, type and inline SVG.

Instant first paint; no layout shift (reserve space for dynamic elements).

One IntersectionObserver instance for reveals; rAF for count-ups.

Total file target: comparable to linlang.html; never lazy about it, but never bloated.

----------------------------------------------------

# ACCESSIBILITY

Semantic landmarks: header / nav / main / section / footer.

Heading hierarchy: one h1, ordered h2/h3.

Contrast: text on pastels is #111111; text on black is #FFFFFF or #1DBA6A.

aria-labels on the language toggle and any icon-only controls.

prefers-reduced-motion fully honored.

----------------------------------------------------

# RESPONSIVE

Breakpoints: ~1080px · 880px · 768px · 540px.

Hero stacks to single column; grids collapse gracefully (3→2→1).

Nav collapses to logo + language toggle + one CTA link on mobile (hamburger optional but must work without JS errors).

The lifted-paper physics survive at every width. Nothing overflows horizontally.

----------------------------------------------------

# IMPORTANT

Never simplify a section because it has a lot of content — choreograph it instead.

Never replace a designed composition with a plain stacked list.

Never let two adjacent sections share the same layout skeleton.

Always choose quality over speed.

If something can feel more physical, push it.

If something reads like a template, redesign it.

This must feel like a brand with taste, not a company with a website.

----------------------------------------------------

# WORKFLOW

Do NOT generate code immediately.

Step 1 — Audit `linlang.html`: extract the full bilingual content inventory.

Step 2 — Design the section-by-section composition plan (one unique layout idea per section).

Step 3 — Design the motion choreography map (what enters how, what counts, what drifts).

Step 4 — Define the CSS token sheet and component classes.

Step 5 — Implement the full file, section by section, in order.

Step 6 — Self-review against all three prompt files: content parity checklist, design-system lock, anti-AI directives.

Step 7 — Verify: file ends with </html>, both languages complete, zero console errors.

Never skip planning.
