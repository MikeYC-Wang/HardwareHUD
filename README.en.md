<div align="center">

# ⚡ HardwareHUD

### Black-Gold Chip Console for Full-Stack Architects

A hand-drawn, zero-charting-library SVG dashboard for your GitHub profile README

<img src="profile-hud.svg" width="800" alt="HardwareHUD preview" />

**Language：** [繁體中文](README.md) ・ [English](README.en.md) ・ [日本語](README.ja.md) ・ [한국어](README.ko.md)

[![License: MIT](https://img.shields.io/badge/License-MIT-d4af37.svg)](LICENSE)

</div>

---

## Overview

**HardwareHUD** fetches your last year of GitHub contribution calendar data and top-5 language
usage via the GraphQL API v4, then hand-assembles a native SVG string (`<polygon>`, `<circle>`,
`<path>`, `<text>` — no charting libraries at all) into a dark-mode-friendly
(`#0d1117` / `#050508`) "precision hardware console" with gold/amber (`#d4af37`, `#ffb703`) neon
accents. It's regenerated automatically every day by GitHub Actions.

The console has three signature instruments:

| Component | Description |
| --- | --- |
| 🧊 Isometric 3D chip matrix | 52 weeks × 7 days of contributions rendered as glowing extruded cubes using isometric projection — the more commits, the taller and more amber the block |
| 📡 Sonar radar scanner | Commit / Issue / PR / Repo / Review reimagined as a 5-axis sci-fi radar with crosshairs |
| 💍 Concentric energy rings | Top-5 languages shown as multi-layer arc gauges, similar to a sports car's digital dashboard |

## Preview

<img src="profile-hud.svg" width="800" alt="preview" />

> The image above is `profile-hud.svg`, refreshed daily by GitHub Actions. It won't exist until
> you trigger the workflow for the first time.

## How to Use

1. **Fork (or use) this repo** so `main` contains [`src/generate_hud.py`](src/generate_hud.py) and [`.github/workflows/hud-updater.yml`](.github/workflows/hud-updater.yml).
2. **Create a Personal Access Token (PAT)** under GitHub → Settings → Developer settings →
   Personal access tokens, with `read:user` scope (enough to read your own contributions and
   repositories).
3. **Add it as a repository secret**: Settings → Secrets and variables → Actions → New repository
   secret, name it `GH_PAT`.
4. **Set your username**: edit `HUD_USERNAME: MikeYC-Wang` in
   [`.github/workflows/hud-updater.yml`](.github/workflows/hud-updater.yml) to your own GitHub handle.
5. **Trigger the first run** manually from the Actions tab → `Hardware HUD Updater` →
   `Run workflow`. Afterwards it runs daily at 16:00 UTC and auto-commits `profile-hud.svg`.
6. **Embed it in your profile README** (the special `<username>/<username>` repo):

   ```markdown
   ![Hardware HUD](https://raw.githubusercontent.com/<your-username>/HardwareHUD/main/profile-hud.svg)
   ```

## Local Testing

```bash
pip install -r src/requirements.txt
export GH_PAT=your_personal_access_token   # PowerShell: $env:GH_PAT="..."
python src/generate_hud.py
```

This writes `profile-hud.svg` to the current directory.

## Customization

- Colors and canvas size live as constants at the top of [`src/generate_hud.py`](src/generate_hud.py) (`COLOR_*`, `WIDTH`, `HEIGHT`).
- Change the update schedule via the `cron` expression in [`hud-updater.yml`](.github/workflows/hud-updater.yml).

---

<div align="center">

Made with ⚡ and hand-rolled SVG · MODEL: UTCHEN-FSTK-2026

</div>
