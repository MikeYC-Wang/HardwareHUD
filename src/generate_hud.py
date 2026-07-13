#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Hardware HUD - GitHub Profile Dynamic Dashboard Generator
===========================================================
"全端架構師的黑金晶片控制台" (Full-Stack Architect's Black-Gold Chip Console)

This script queries the GitHub GraphQL API v4 for a full year of contribution
data and top programming languages, then hand-rolls a single self-contained
SVG "hardware console" — no matplotlib, no charting libraries, just raw
<polygon>/<circle>/<path>/<text> tags assembled through string formatting.

The console is composed of three signature instruments:
  A. An isometric (2.5D) 3D chip matrix of the yearly contribution calendar
  B. A sonar-style radar scanner summarising five activity dimensions
  C. A set of concentric "energy ring" arcs for the top 5 languages

Output: profile-hud.svg (written to the current working directory)
"""

from __future__ import annotations

import math
import os
import sys
from datetime import datetime, timedelta, timezone

import requests

# --------------------------------------------------------------------------
# Configuration
# --------------------------------------------------------------------------

GITHUB_USERNAME = os.environ.get("HUD_USERNAME", "MikeYC-Wang")
GITHUB_TOKEN = os.environ.get("GH_PAT") or os.environ.get("GITHUB_TOKEN")
GRAPHQL_ENDPOINT = "https://api.github.com/graphql"
OUTPUT_FILE = "profile-hud.svg"

# Palette --------------------------------------------------------------
COLOR_BG_OUTER = "#050508"
COLOR_BG_INNER = "#0d1117"
COLOR_PANEL = "#0f1420"
COLOR_GRID_DARK = "#161b22"
COLOR_GOLD = "#d4af37"
COLOR_AMBER = "#ffb703"
COLOR_AMBER_DIM = "#8a6d1f"
COLOR_TEXT_MUTED = "#6e7681"
COLOR_TEXT_GOLD = "#f2d585"
COLOR_LINE = "#2a2f3a"
COLOR_OK_GREEN = "#3fb950"

# Canvas -----------------------------------------------------------------
WIDTH = 800
HEIGHT = 350

# --------------------------------------------------------------------------
# GraphQL query
# --------------------------------------------------------------------------
# NOTE: extended beyond the minimal calendar/language spec with the extra
# aggregate counters already exposed on `contributionsCollection` (commits,
# issues, PRs, reviews, repos-with-contributions) so the sonar radar (B) can
# be populated from the *same* single request instead of firing four more.
GRAPHQL_QUERY = """
query ($username: String!) {
  user(login: $username) {
    contributionsCollection {
      totalCommitContributions
      totalIssueContributions
      totalPullRequestContributions
      totalPullRequestReviewContributions
      totalRepositoriesWithContributedCommits
      contributionCalendar {
        totalContributions
        weeks {
          contributionDays {
            date
            contributionCount
            color
          }
        }
      }
    }
    repositories(first: 100, ownerAffiliations: OWNER, isFork: false) {
      nodes {
        languages(first: 5, orderBy: {field: SIZE, direction: DESC}) {
          edges {
            size
            node {
              name
              color
            }
          }
        }
      }
    }
  }
}
"""


# --------------------------------------------------------------------------
# Data fetching
# --------------------------------------------------------------------------

def fetch_github_data(username: str, token: str) -> dict:
    """Fire a single GraphQL request and return the raw `data.user` payload."""
    if not token:
        raise RuntimeError(
            "Missing GitHub token. Set the GH_PAT (or GITHUB_TOKEN) environment "
            "variable with a Personal Access Token that has 'read:user' scope."
        )

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "User-Agent": "HardwareHUD-Generator",
    }
    payload = {"query": GRAPHQL_QUERY, "variables": {"username": username}}

    response = requests.post(GRAPHQL_ENDPOINT, json=payload, headers=headers, timeout=30)
    response.raise_for_status()
    result = response.json()

    if "errors" in result:
        raise RuntimeError(f"GitHub GraphQL API returned errors: {result['errors']}")

    user = result.get("data", {}).get("user")
    if not user:
        raise RuntimeError("GitHub GraphQL API returned no user data.")

    return user


# --------------------------------------------------------------------------
# Data processing
# --------------------------------------------------------------------------

def process_contributions(user: dict):
    """Return (weeks_matrix, total_contributions, max_daily_count)."""
    calendar = user["contributionsCollection"]["contributionCalendar"]
    total = calendar["totalContributions"]
    weeks = calendar["weeks"]

    max_count = 1
    for week in weeks:
        for day in week["contributionDays"]:
            if day["contributionCount"] > max_count:
                max_count = day["contributionCount"]

    return weeks, total, max_count


def process_languages(user: dict, top_n: int = 5):
    """Aggregate language byte-size across all owned repos -> top N (name, color, pct)."""
    totals: dict[str, dict] = {}
    for repo in user["repositories"]["nodes"]:
        for edge in repo["languages"]["edges"]:
            name = edge["node"]["name"]
            color = edge["node"]["color"] or "#8b949e"
            size = edge["size"]
            if name not in totals:
                totals[name] = {"size": 0, "color": color}
            totals[name]["size"] += size

    grand_total = sum(v["size"] for v in totals.values()) or 1
    ranked = sorted(totals.items(), key=lambda kv: kv[1]["size"], reverse=True)[:top_n]

    result = []
    for name, info in ranked:
        pct = (info["size"] / grand_total) * 100.0
        result.append({"name": name, "color": info["color"], "pct": pct})
    return result


def process_radar_stats(user: dict) -> dict:
    cc = user["contributionsCollection"]
    return {
        "COMMIT": cc["totalCommitContributions"],
        "ISSUE": cc["totalIssueContributions"],
        "PR": cc["totalPullRequestContributions"],
        "REPO": cc["totalRepositoriesWithContributedCommits"],
        "REVIEW": cc["totalPullRequestReviewContributions"],
    }


# --------------------------------------------------------------------------
# Color helpers
# --------------------------------------------------------------------------

def hex_to_rgb(h: str):
    h = h.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def rgb_to_hex(rgb) -> str:
    r, g, b = (max(0, min(255, int(round(c)))) for c in rgb)
    return f"#{r:02x}{g:02x}{b:02x}"


def lerp_color(c1: str, c2: str, t: float) -> str:
    t = max(0.0, min(1.0, t))
    r1, g1, b1 = hex_to_rgb(c1)
    r2, g2, b2 = hex_to_rgb(c2)
    return rgb_to_hex((r1 + (r2 - r1) * t, g1 + (g2 - g1) * t, b1 + (b2 - b1) * t))


def shade(color_hex: str, factor: float) -> str:
    """factor < 1 darkens, factor > 1 lightens (clamped)."""
    r, g, b = hex_to_rgb(color_hex)
    return rgb_to_hex((r * factor, g * factor, b * factor))


def intensity_color(t: float) -> str:
    """0 -> dark grid slab, mid -> gold, high -> glowing amber."""
    if t <= 0:
        return COLOR_GRID_DARK
    if t < 0.55:
        return lerp_color(COLOR_GRID_DARK, COLOR_GOLD, t / 0.55)
    return lerp_color(COLOR_GOLD, COLOR_AMBER, (t - 0.55) / 0.45)


# --------------------------------------------------------------------------
# Component A: Isometric 3D contribution chip-matrix
# --------------------------------------------------------------------------

def build_chip_matrix_svg(weeks, max_count, origin_x, origin_y) -> str:
    parts = [f'<g id="chip-matrix" transform="translate({origin_x},{origin_y})">']

    tile_size = 6.4
    cos30 = math.cos(math.radians(30))
    sin30 = math.sin(math.radians(30))
    dx = tile_size * cos30
    dy = tile_size * sin30
    max_h = 22.0
    min_h = 2.0

    # collect cubes with a painter's-algorithm draw order (back-to-front)
    cubes = []
    for x, week in enumerate(weeks):
        for y, day in enumerate(week["contributionDays"]):
            count = day["contributionCount"]
            t = math.sqrt(count / max_count) if count > 0 else 0.0
            h = 0.0 if count == 0 else min_h + (max_h - min_h) * t
            base_x = (x - y) * dx
            base_y = (x + y) * dy
            depth_key = x + y  # draw farthest (small x+y) first
            cubes.append((depth_key, base_x, base_y, h, t, count))

    cubes.sort(key=lambda c: c[0])

    for _, bx, by, h, t, count in cubes:
        top_col = intensity_color(t)
        right_col = shade(top_col, 0.72)
        left_col = shade(top_col, 0.5)

        ty = by - h
        # top diamond
        n = (bx, ty - dy)
        e = (bx + dx, ty)
        s = (bx, ty + dy)
        w = (bx - dx, ty)
        # bottom counterparts (h below)
        s_bot = (bx, by + dy)
        w_bot = (bx - dx, by)
        e_bot = (bx + dx, by)

        glow_class = ' class="glow-cube"' if t > 0.75 else ""

        if h > 0:
            parts.append(
                f'<polygon points="{w[0]:.2f},{w[1]:.2f} {s[0]:.2f},{s[1]:.2f} '
                f'{s_bot[0]:.2f},{s_bot[1]:.2f} {w_bot[0]:.2f},{w_bot[1]:.2f}" '
                f'fill="{left_col}" stroke="#000000" stroke-opacity="0.25" stroke-width="0.3"/>'
            )
            parts.append(
                f'<polygon points="{s[0]:.2f},{s[1]:.2f} {e[0]:.2f},{e[1]:.2f} '
                f'{e_bot[0]:.2f},{e_bot[1]:.2f} {s_bot[0]:.2f},{s_bot[1]:.2f}" '
                f'fill="{right_col}" stroke="#000000" stroke-opacity="0.25" stroke-width="0.3"/>'
            )
            parts.append(
                f'<polygon points="{n[0]:.2f},{n[1]:.2f} {e[0]:.2f},{e[1]:.2f} '
                f'{s[0]:.2f},{s[1]:.2f} {w[0]:.2f},{w[1]:.2f}" '
                f'fill="{top_col}" stroke="#000000" stroke-opacity="0.2" stroke-width="0.3"{glow_class}/>'
            )
        else:
            parts.append(
                f'<polygon points="{n[0]:.2f},{n[1]:.2f} {e[0]:.2f},{e[1]:.2f} '
                f'{s[0]:.2f},{s[1]:.2f} {w[0]:.2f},{w[1]:.2f}" '
                f'fill="{top_col}" fill-opacity="0.6" stroke="#000000" stroke-opacity="0.15" stroke-width="0.3"/>'
            )

    parts.append("</g>")
    return "".join(parts)


# --------------------------------------------------------------------------
# Component B: Sonar radar scanner (5-axis capability analysis)
# --------------------------------------------------------------------------

def build_radar_svg(stats: dict, cx: float, cy: float, r_max: float) -> str:
    axes = list(stats.keys())
    n = len(axes)
    caps = {"COMMIT": 1200, "ISSUE": 120, "PR": 200, "REPO": 40, "REVIEW": 200}

    parts = [f'<g id="radar-scanner" transform="translate({cx},{cy})">']

    # outer dial rings
    for i, frac in enumerate((1.0, 0.75, 0.5, 0.25)):
        opacity = 0.55 if i == 0 else 0.22
        dash = "" if i == 0 else ' stroke-dasharray="2,3"'
        parts.append(
            f'<circle cx="0" cy="0" r="{r_max * frac:.2f}" fill="none" '
            f'stroke="{COLOR_GOLD}" stroke-opacity="{opacity}" stroke-width="1"{dash}/>'
        )

    # crosshair
    parts.append(
        f'<line x1="{-r_max:.2f}" y1="0" x2="{r_max:.2f}" y2="0" '
        f'stroke="{COLOR_GOLD}" stroke-opacity="0.3" stroke-width="0.75"/>'
    )
    parts.append(
        f'<line x1="0" y1="{-r_max:.2f}" x2="0" y2="{r_max:.2f}" '
        f'stroke="{COLOR_GOLD}" stroke-opacity="0.3" stroke-width="0.75"/>'
    )

    # axis spokes + labels
    points = []
    for i, key in enumerate(axes):
        angle = -math.pi / 2 + i * (2 * math.pi / n)
        ax_x, ax_y = math.cos(angle) * r_max, math.sin(angle) * r_max
        parts.append(
            f'<line x1="0" y1="0" x2="{ax_x:.2f}" y2="{ax_y:.2f}" '
            f'stroke="{COLOR_LINE}" stroke-width="0.75"/>'
        )

        raw = stats[key]
        norm = max(0.06, min(1.0, raw / caps.get(key, max(raw, 1))))
        r = r_max * norm
        px, py = math.cos(angle) * r, math.sin(angle) * r
        points.append((px, py))

        label_x, label_y = math.cos(angle) * (r_max + 16), math.sin(angle) * (r_max + 16)
        anchor = "middle"
        if label_x > 6:
            anchor = "start"
        elif label_x < -6:
            anchor = "end"
        parts.append(
            f'<text x="{label_x:.1f}" y="{label_y:.1f}" text-anchor="{anchor}" '
            f'font-family="Consolas, \'Courier New\', monospace" font-size="8" '
            f'fill="{COLOR_TEXT_GOLD}" dominant-baseline="middle">{key}</text>'
        )
        parts.append(
            f'<text x="{label_x:.1f}" y="{label_y + 10:.1f}" text-anchor="{anchor}" '
            f'font-family="Consolas, \'Courier New\', monospace" font-size="7" '
            f'fill="{COLOR_TEXT_MUTED}" dominant-baseline="middle">{raw}</text>'
        )

    # data polygon
    poly_pts = " ".join(f"{px:.2f},{py:.2f}" for px, py in points)
    parts.append(
        f'<polygon points="{poly_pts}" fill="url(#radarFill)" '
        f'stroke="{COLOR_AMBER}" stroke-width="1.4" stroke-linejoin="round" filter="url(#goldGlow)"/>'
    )
    for px, py in points:
        parts.append(f'<circle cx="{px:.2f}" cy="{py:.2f}" r="2" fill="{COLOR_AMBER}"/>')

    parts.append(
        f'<circle cx="0" cy="0" r="2.4" fill="{COLOR_AMBER}"/>'
    )
    parts.append("</g>")
    return "".join(parts)


# --------------------------------------------------------------------------
# Component C: Concentric ring "energy" gauges for top languages
# --------------------------------------------------------------------------

def build_language_rings_svg(langs, cx: float, cy: float, r_base: float) -> str:
    parts = [f'<g id="lang-rings" transform="translate({cx},{cy})">']
    ring_gap = 8.5
    stroke_w = 5.5
    legend_x = r_base + 26
    row_h = 18
    legend_y0 = -((len(langs) - 1) * row_h) / 2

    for i, lang in enumerate(langs):
        r = r_base - i * ring_gap
        circumference = 2 * math.pi * r
        pct = lang["pct"] / 100.0
        dash = circumference * pct
        gap = circumference - dash
        color = lang["color"]

        # background track
        parts.append(
            f'<circle cx="0" cy="0" r="{r:.2f}" fill="none" stroke="{COLOR_GRID_DARK}" '
            f'stroke-width="{stroke_w}"/>'
        )
        # active arc
        parts.append(
            f'<circle cx="0" cy="0" r="{r:.2f}" fill="none" stroke="{color}" '
            f'stroke-width="{stroke_w}" stroke-linecap="round" '
            f'stroke-dasharray="{dash:.2f},{gap:.2f}" stroke-dashoffset="0" '
            f'transform="rotate(-90)" filter="url(#goldGlow)"/>'
        )

        ly = legend_y0 + i * row_h
        parts.append(f'<circle cx="{legend_x:.1f}" cy="{ly - 3:.1f}" r="3" fill="{color}"/>')
        parts.append(
            f'<text x="{legend_x + 8:.1f}" y="{ly:.1f}" font-family="Consolas, \'Courier New\', monospace" '
            f'font-size="8.5" fill="{COLOR_TEXT_GOLD}">'
            f'{lang["name"]} <tspan fill="{COLOR_TEXT_MUTED}" font-size="7.5">{lang["pct"]:.1f}%</tspan></text>'
        )

    parts.append(
        f'<text x="0" y="4" text-anchor="middle" font-family="Consolas, \'Courier New\', monospace" '
        f'font-size="9" fill="{COLOR_AMBER}" filter="url(#goldGlow)">LANG</text>'
    )
    parts.append("</g>")
    return "".join(parts)


# --------------------------------------------------------------------------
# Component D: Chassis, border, chip-style decorations & status strip
# --------------------------------------------------------------------------

def build_frame_svg(total_contributions: int, username: str) -> str:
    parts = []

    # outer chamfered chassis (cut corners like a chip package)
    c = 14  # chamfer size
    m = 3  # margin
    w, h = WIDTH - 2 * m, HEIGHT - 2 * m
    chassis_path = (
        f"M {m + c},{m} L {m + w - c},{m} L {m + w},{m + c} L {m + w},{m + h - c} "
        f"L {m + w - c},{m + h} L {m + c},{m + h} L {m},{m + h - c} L {m},{m + c} Z"
    )
    parts.append(
        f'<path d="{chassis_path}" fill="url(#bgGrad)" stroke="{COLOR_GOLD}" '
        f'stroke-width="1.4" stroke-opacity="0.85"/>'
    )
    parts.append(
        f'<path d="{chassis_path}" fill="none" stroke="{COLOR_AMBER}" '
        f'stroke-width="0.6" stroke-opacity="0.35" transform="translate(4,4) scale(0.985)"/>'
    )

    # corner rivets
    for rx, ry in ((16, 16), (WIDTH - 16, 16), (16, HEIGHT - 16), (WIDTH - 16, HEIGHT - 16)):
        parts.append(f'<circle cx="{rx}" cy="{ry}" r="2.4" fill="{COLOR_GOLD}" fill-opacity="0.7"/>')
        parts.append(f'<circle cx="{rx}" cy="{ry}" r="1" fill="{COLOR_BG_INNER}"/>')

    # top ticks strip
    for tx in range(40, WIDTH - 40, 14):
        parts.append(
            f'<line x1="{tx}" y1="6" x2="{tx}" y2="10" stroke="{COLOR_GOLD}" stroke-opacity="0.25" stroke-width="1"/>'
        )

    # header
    parts.append(
        f'<text x="26" y="30" font-family="Consolas, \'Courier New\', monospace" font-weight="bold" '
        f'font-size="17" fill="{COLOR_TEXT_GOLD}" filter="url(#goldGlow)">HARDWARE HUD</text>'
    )
    parts.append(
        f'<text x="26" y="45" font-family="Consolas, \'Courier New\', monospace" font-size="9" '
        f'fill="{COLOR_TEXT_MUTED}" letter-spacing="1.5">// FULL-STACK ARCHITECT CONSOLE :: @{username.upper()}</text>'
    )

    # top-right glowing headline counter
    parts.append(
        f'<text x="{WIDTH - 26}" y="30" text-anchor="end" font-family="Consolas, \'Courier New\', monospace" '
        f'font-weight="bold" font-size="17" fill="{COLOR_AMBER}" filter="url(#goldGlow)">{total_contributions:,}</text>'
    )
    parts.append(
        f'<text x="{WIDTH - 26}" y="45" text-anchor="end" font-family="Consolas, \'Courier New\', monospace" '
        f'font-size="9" fill="{COLOR_TEXT_MUTED}" letter-spacing="1">CONTRIBUTIONS / YEAR</text>'
    )

    # divider under header
    parts.append(
        f'<line x1="20" y1="52" x2="{WIDTH - 20}" y2="52" stroke="{COLOR_LINE}" stroke-width="1"/>'
    )

    # footer status strip
    parts.append(
        f'<line x1="20" y1="{HEIGHT - 30}" x2="{WIDTH - 20}" y2="{HEIGHT - 30}" stroke="{COLOR_LINE}" stroke-width="1"/>'
    )
    parts.append(f'<circle cx="30" cy="{HEIGHT - 16}" r="3.2" fill="{COLOR_OK_GREEN}" filter="url(#goldGlow)"/>')
    parts.append(
        f'<text x="40" y="{HEIGHT - 12}" font-family="Consolas, \'Courier New\', monospace" font-size="9" '
        f'fill="{COLOR_TEXT_GOLD}" letter-spacing="1">SYSTEM STATUS: ACTIVE</text>'
    )
    tz_utc8 = timezone(timedelta(hours=8))
    now_str = datetime.now(tz_utc8).strftime("%Y-%m-%d %H:%M UTC+8")
    parts.append(
        f'<text x="{WIDTH / 2:.0f}" y="{HEIGHT - 12}" text-anchor="middle" '
        f'font-family="Consolas, \'Courier New\', monospace" font-size="8" '
        f'fill="{COLOR_TEXT_MUTED}">LAST SYNC: {now_str}</text>'
    )
    parts.append(
        f'<text x="{WIDTH - 20}" y="{HEIGHT - 12}" text-anchor="end" '
        f'font-family="Consolas, \'Courier New\', monospace" font-size="9" '
        f'fill="{COLOR_TEXT_GOLD}" letter-spacing="1">MODEL: UTCHEN-FSTK-2026</text>'
    )

    return "".join(parts)


# --------------------------------------------------------------------------
# Assembly
# --------------------------------------------------------------------------

def build_svg(user: dict) -> str:
    weeks, total_contributions, max_count = process_contributions(user)
    languages = process_languages(user)
    radar_stats = process_radar_stats(user)

    defs = f"""
    <defs>
      <linearGradient id="bgGrad" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" stop-color="{COLOR_BG_OUTER}"/>
        <stop offset="55%" stop-color="{COLOR_BG_INNER}"/>
        <stop offset="100%" stop-color="{COLOR_PANEL}"/>
      </linearGradient>
      <radialGradient id="radarFill" cx="50%" cy="50%" r="60%">
        <stop offset="0%" stop-color="{COLOR_AMBER}" stop-opacity="0.55"/>
        <stop offset="100%" stop-color="{COLOR_GOLD}" stop-opacity="0.08"/>
      </radialGradient>
      <filter id="goldGlow" x="-60%" y="-60%" width="220%" height="220%">
        <feGaussianBlur stdDeviation="1.6" result="blur"/>
        <feMerge>
          <feMergeNode in="blur"/>
          <feMergeNode in="SourceGraphic"/>
        </feMerge>
      </filter>
    </defs>
    """

    chip_matrix = build_chip_matrix_svg(weeks, max_count, origin_x=80, origin_y=112)
    radar = build_radar_svg(radar_stats, cx=610, cy=135, r_max=52)
    rings = build_language_rings_svg(languages, cx=520, cy=255, r_base=42)
    frame = build_frame_svg(total_contributions, GITHUB_USERNAME)

    svg = f"""<svg width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}" \
xmlns="http://www.w3.org/2000/svg" font-family="Consolas, 'Courier New', monospace">
  <style>
    .glow-cube {{ filter: url(#goldGlow); }}
    text {{ user-select: none; }}
  </style>
  {defs}
  <rect x="0" y="0" width="{WIDTH}" height="{HEIGHT}" fill="{COLOR_BG_OUTER}"/>
  {frame}
  {chip_matrix}
  {radar}
  {rings}
</svg>"""
    return svg


def main() -> int:
    try:
        user = fetch_github_data(GITHUB_USERNAME, GITHUB_TOKEN)
        svg = build_svg(user)
    except Exception as exc:  # noqa: BLE001
        print(f"[generate_hud] Failed to generate HUD: {exc}", file=sys.stderr)
        return 1

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(svg)

    print(f"[generate_hud] Wrote {OUTPUT_FILE} ({len(svg)} bytes) for user '{GITHUB_USERNAME}'.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
