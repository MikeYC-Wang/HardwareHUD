<div align="center">

# ⚡ HardwareHUD

### フルスタックアーキテクトのための黒金チップコンソール

サードパーティのグラフ描画ライブラリを一切使わず、手作業で描いた SVG による GitHub プロフィールダッシュボード

<img src="profile-hud.svg" width="800" alt="HardwareHUD preview" />

**Language：** [繁體中文](README.md) ・ [English](README.en.md) ・ [日本語](README.ja.md) ・ [한국어](README.ko.md)

[![License: MIT](https://img.shields.io/badge/License-MIT-d4af37.svg)](LICENSE)

</div>

---

## プロジェクト概要

**HardwareHUD** は GitHub GraphQL API v4 を使って過去1年分のコントリビューションカレンダーと
使用言語トップ5を取得し、サードパーティのグラフ描画ライブラリを一切使わず、
Python の文字列だけでネイティブな SVG タグ（`<polygon>`、`<circle>`、`<path>`、`<text>`）を
組み立て、ダークモード（`#0d1117` / `#050508`）とゴールド／アンバーのネオン
（`#d4af37`、`#ffb703`）を纏った「精密ハードウェアコンソール」を生成します。
GitHub Actions が毎日自動で再生成します。

コンソールは3つの主要インストゥルメントで構成されています。

| コンポーネント | 説明 |
| --- | --- |
| 🧊 アイソメトリック3Dチップマトリクス | 52週×7日分のコントリビューションを等角投影で立体的なキューブとして描画。コミットが多いほど高く、より輝くアンバー色になります |
| 📡 ソナー・レーダースキャナー | Commit / Issue / PR / Repo / Review の5軸をクロスヘア付きのSF風レーダーとして再構築 |
| 💍 同心円エネルギーリング | 使用言語トップ5をスポーツカーのデジタルダッシュボードのような多層円弧ゲージで表示 |

## プレビュー

<img src="profile-hud.svg" width="800" alt="preview" />

> 上の画像は `profile-hud.svg` で、GitHub Actions によって毎日更新されます。初回は
> ワークフローを手動実行するまで生成されません。

## 使い方

1. **このリポジトリを Fork（またはそのまま使用）**し、`main` ブランチに
   [`src/generate_hud.py`](src/generate_hud.py) と [`.github/workflows/hud-updater.yml`](.github/workflows/hud-updater.yml) が含まれていることを確認してください。
2. **Personal Access Token (PAT) を作成**：GitHub → Settings → Developer settings →
   Personal access tokens で、`read:user` スコープを持つトークンを作成します（自分自身の
   contributions とリポジトリを読み取れれば十分です）。
3. **リポジトリシークレットに追加**：Settings → Secrets and variables → Actions →
   New repository secret から、名前を `GH_PAT` として登録します。
4. **ユーザー名を設定**：[`.github/workflows/hud-updater.yml`](.github/workflows/hud-updater.yml) 内の
   `HUD_USERNAME: MikeYC-Wang` を自分の GitHub ユーザー名に書き換えます。
5. **初回を手動実行**：Actions タブから `Hardware HUD Updater` → `Run workflow` を実行すると、
   リポジトリ直下に `profile-hud.svg` が生成されます。以降は毎日 UTC 16:00 に自動実行・自動コミットされます。
6. **プロフィール README に埋め込む**（特別な `<username>/<username>` リポジトリ内）：

   ```markdown
   ![Hardware HUD](https://raw.githubusercontent.com/<あなたのユーザー名>/HardwareHUD/main/profile-hud.svg)
   ```

## ローカルテスト

```bash
pip install -r src/requirements.txt
export GH_PAT=あなたのPersonalAccessToken   # PowerShell: $env:GH_PAT="..."
python src/generate_hud.py
```

実行すると、カレントディレクトリに `profile-hud.svg` が出力されます。

## カスタマイズ

- 色やキャンバスサイズは [`src/generate_hud.py`](src/generate_hud.py) 冒頭の定数（`COLOR_*`、`WIDTH`、`HEIGHT`）で調整できます。
- 更新スケジュールは [`hud-updater.yml`](.github/workflows/hud-updater.yml) の `cron` 式で変更できます。

---

<div align="center">

Made with ⚡ and hand-rolled SVG · MODEL: UTCHEN-FSTK-2026

</div>
