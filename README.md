# ⚽ 2026 FIFA World Cup Simulator & 2D Playable Football Game

Streamlit과 HTML5 Canvas를 활용하여 제작한 실시간 FIFA 랭킹 대시보드, 전술 피치 시각화 및 직접 플레이 가능한 2D 축구 미니 게임이 결합된 48개국 월드컵 토너먼트 시뮬레이터입니다.

## 🌟 주요 기능

1. **📊 실시간 FIFA 랭킹 & 라인업 시각화**
   - 48개 참가국의 실명 감독 및 라인업 포지션 정보 제공
   - `Plotly` 기반 전술 피치를 활용하여 선택한 팀의 4-3-3 포메이션 시각화
   - `st-autorefresh`를 활용한 1시간 주기 실시간 데이터 갱신 동기화

2. **🎮 HTML5 Canvas 2D 미니 축구 게임**
   - 사용자가 직접 키보드로 선수를 컨트롤하며 즐기는 2D 매치 플레이 (방향키/WASD로 이동, 스페이스바로 슛)
   - 골키퍼 및 수비수 인공지능(AI) 탑재
   - 양방향 웹메시지 통신(`postMessage`)을 통해 경기 최종 점수를 Streamlit 세션 상태로 자동 전송 및 기록

3. **🏆 2026 포맷 월드컵 토너먼트 모드**
   - 48개국 시드 포트 배정 및 A~L조(12개 조) 랜덤 드로우 시스템
   - 플레이어 대표팀 경기는 직접 수동 플레이, 타 경기들은 FIFA 포인트를 반영한 확률 기반의 퀵 시뮬레이션 지원
   - 조별 리그 3위 12개국 중 성적 우수 8개국을 판정하는 와일드카드 트래커(Wildcard Tracker) 탑재
   - 32강부터 결승까지의 단판 승부 브래킷 자동 생성 및 연장 동점 시 승부차기(Penalty Shootout) 인터랙티브 미니 게임 연동

---

## 🚀 로컬 실행 방법

로컬 터미널에서 다음 명령어를 통해 라이브러리를 설치하고 앱을 기동합니다.

```powershell
# 1. 저장소 클론 및 이동
git clone https://github.com/gimtpeng/streamlit_worldcup.git
cd streamlit_worldcup

# 2. 관련 패키지 설치
pip install -r requirements.txt

# 3. Streamlit 실행
streamlit run app.py
```

---

## 🌐 Streamlit.io 호스팅 방법

본 프로젝트는 [Streamlit Community Cloud](https://share.streamlit.io/)에 즉시 호스팅 배포가 가능하도록 설정되어 있습니다.

1. [Streamlit Share](https://share.streamlit.io/)에 접속하여 로그인합니다.
2. **"Create App"**을 클릭한 뒤, 본인의 GitHub 리포지토리(`gimtpeng/streamlit_worldcup`)를 선택합니다.
3. 아래 설정값을 입력한 뒤 **"Deploy"**를 누릅니다:
   - **Branch:** `main`
   - **Main file path:** `app.py`
