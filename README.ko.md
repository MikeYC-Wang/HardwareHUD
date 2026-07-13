<div align="center">

# ⚡ HardwareHUD

### 풀스택 아키텍트를 위한 블랙-골드 칩 콘솔

서드파티 차트 라이브러리 없이 손수 그린 SVG로 만든 GitHub 프로필 대시보드

<img src="profile-hud.svg" width="800" alt="HardwareHUD preview" />

**Language：** [繁體中文](README.md) ・ [English](README.en.md) ・ [日本語](README.ja.md) ・ [한국어](README.ko.md)

[![License: MIT](https://img.shields.io/badge/License-MIT-d4af37.svg)](LICENSE)

</div>

---

## 프로젝트 소개

**HardwareHUD**는 GitHub GraphQL API v4를 통해 지난 1년간의 컨트리뷰션 캘린더와
상위 5개 프로그래밍 언어 사용 비율을 가져온 뒤, 서드파티 차트 라이브러리 없이
순수 Python 문자열 포매팅만으로 네이티브 SVG 태그(`<polygon>`, `<circle>`, `<path>`, `<text>`)를
조립하여, 다크 모드(`#0d1117` / `#050508`)와 골드/앰버 네온(`#d4af37`, `#ffb703`) 감성의
"정밀 하드웨어 콘솔"을 만듭니다. GitHub Actions가 매일 자동으로 다시 생성합니다.

콘솔은 세 가지 핵심 계기판으로 구성됩니다.

| 구성 요소 | 설명 |
| --- | --- |
| 🧊 아이소메트릭 3D 칩 매트릭스 | 52주 × 7일치 컨트리뷰션을 등각 투영(Isometric Projection)으로 입체 큐브로 표현. 커밋이 많을수록 블록이 높아지고 앰버 골드빛이 강해집니다 |
| 📡 소나 레이더 스캐너 | Commit / Issue / PR / Repo / Review 다섯 가지 지표를 십자선이 있는 SF풍 레이더로 재구성 |
| 💍 동심원 에너지 링 | 상위 5개 언어 비율을 스포츠카 디지털 계기판 같은 다층 원호 게이지로 표시 |

## 미리보기

<img src="profile-hud.svg" width="800" alt="preview" />

> 위 이미지는 `profile-hud.svg`이며, GitHub Actions가 매일 갱신합니다. 워크플로를 처음 한 번
> 수동으로 실행하기 전까지는 파일이 존재하지 않습니다.

## 사용 방법

1. **이 저장소를 Fork(또는 그대로 사용)**하여 `main` 브랜치에
   [`src/generate_hud.py`](src/generate_hud.py)와 [`.github/workflows/hud-updater.yml`](.github/workflows/hud-updater.yml)이 포함되어 있는지 확인합니다.
2. **Personal Access Token(PAT) 생성**: GitHub → Settings → Developer settings →
   Personal access tokens에서 `read:user` 권한을 가진 토큰을 생성합니다(자신의 컨트리뷰션과
   저장소를 읽을 수 있으면 충분합니다).
3. **저장소 시크릿으로 추가**: Settings → Secrets and variables → Actions →
   New repository secret에서 이름을 `GH_PAT`로 등록합니다.
4. **사용자 이름 설정**: [`.github/workflows/hud-updater.yml`](.github/workflows/hud-updater.yml) 파일의
   `HUD_USERNAME: MikeYC-Wang`을 본인의 GitHub 아이디로 변경합니다.
5. **첫 실행을 수동으로 트리거**: Actions 탭에서 `Hardware HUD Updater` → `Run workflow`를
   실행하면 저장소 루트에 `profile-hud.svg`가 생성됩니다. 이후에는 매일 UTC 16:00에 자동 실행
   및 자동 커밋됩니다.
6. **프로필 README에 삽입**(특수 `<username>/<username>` 저장소):

   ```markdown
   ![Hardware HUD](https://raw.githubusercontent.com/<사용자명>/HardwareHUD/main/profile-hud.svg)
   ```

## 로컬 테스트

```bash
pip install -r src/requirements.txt
export GH_PAT=본인의PersonalAccessToken   # PowerShell: $env:GH_PAT="..."
python src/generate_hud.py
```

실행하면 현재 디렉터리에 `profile-hud.svg`가 생성됩니다.

## 커스터마이징

- 색상과 캔버스 크기는 [`src/generate_hud.py`](src/generate_hud.py) 상단의 상수(`COLOR_*`, `WIDTH`, `HEIGHT`)에서 조정할 수 있습니다.
- 갱신 주기는 [`hud-updater.yml`](.github/workflows/hud-updater.yml)의 `cron` 표현식을 수정하여 변경할 수 있습니다.

---

<div align="center">

Made with ⚡ and hand-rolled SVG · MODEL: UTCHEN-FSTK-2026

</div>
