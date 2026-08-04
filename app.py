# -*- coding: utf-8 -*-
import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import plotly.graph_objects as go
import random
import os
import time

# FIFA 랭킹 및 스쿼드 데이터 임포트
from team_generator import ALL_TEAMS as TEAMS, ALL_CL_TEAMS as CL_TEAMS

# 페이지 기본 설정 및 다크 테마 주입
st.set_page_config(
    page_title="2026 FIFA World Cup Simulator",
    layout="wide",
    initial_sidebar_state="expanded"
)

# st-autorefresh 패키지 동적 로딩 (없으면 경고 표시 후 동작 생략)
try:
    from streamlit_autorefresh import st_autorefresh
    autorefresh_available = True
except ImportError:
    autorefresh_available = False

# 커스텀 테마 스타일링 (글래스모피즘 및 다크 모드)
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&family=Inter:wght@300;400;600;700&display=swap');
        
        /* 폰트 및 배경 설정 */
        html, body, [data-testid="stAppViewContainer"] {
            font-family: 'Inter', sans-serif;
            background-color: #f8fafc;
            color: #0f172a;
        }
        
        h1, h2, h3, h4, h5, h6 {
            font-family: 'Outfit', sans-serif;
            font-weight: 800;
            color: #0f172a;
        }
        
        /* 메인 배너 그래디언트 */
        .header-title {
            background: linear-gradient(135deg, #e11d48 0%, #ea580c 50%, #16a34a 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: 3rem;
            font-weight: 800;
            text-align: center;
            margin-bottom: 0.5rem;
        }
        .header-subtitle {
            font-size: 1.2rem;
            color: #475569;
            text-align: center;
            margin-bottom: 2rem;
        }
        
        /* 프리미엄 카드 디자인 */
        .glass-card {
            background: rgba(255, 255, 255, 0.7);
            border: 1px solid rgba(15, 23, 42, 0.08);
            border-radius: 16px;
            padding: 1.5rem;
            box-shadow: 0 8px 32px 0 rgba(15, 23, 42, 0.05);
            margin-bottom: 1.5rem;
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
        }
        
        .standing-card {
            background: rgba(241, 245, 249, 0.8);
            border: 1px solid rgba(15, 23, 42, 0.05);
            border-radius: 12px;
            padding: 1rem;
            margin-bottom: 0.8rem;
        }
        
        /* 배지 스타일 */
        .badge-primary {
            background: linear-gradient(90deg, #ff4b4b 0%, #ff7676 100%);
            color: white;
            padding: 4px 12px;
            border-radius: 20px;
            font-weight: 600;
            font-size: 0.85rem;
            display: inline-block;
        }
        
        .badge-secondary {
            background: rgba(15, 23, 42, 0.06);
            color: #475569;
            padding: 4px 12px;
            border-radius: 20px;
            font-weight: 600;
            font-size: 0.85rem;
            display: inline-block;
        }

        .badge-group {
            background: #475569;
            color: white;
            padding: 2px 8px;
            border-radius: 4px;
            font-weight: 700;
            font-size: 0.8rem;
            margin-right: 5px;
        }
        
        /* 승/무/패 스쿼드 라벨 */
        .win-label { color: #2ecc71; font-weight: bold; }
        .draw-label { color: #f1c40f; font-weight: bold; }
        .loss-label { color: #e74c3c; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# 1시간(3600초) 주기 오토 리프레시 실행 (FIFA 랭킹 실시간 동기화 데모용)
if autorefresh_available:
    st_autorefresh(interval=3600000, key="fifa_rankings_refresh")

# --- 데이터 도우미 함수 ---
@st.cache_data
def get_rankings_df():
    data = []
    for code, info in TEAMS.items():
        data.append({
            "코드": code,
            "국가": info["name"],
            "FIFA 랭킹": info["rank"],
            "포인트": info["points"],
            "대륙": info["continent"],
            "감독": info["manager"]
        })
    df = pd.DataFrame(data)
    return df.sort_values("FIFA 랭킹")

# --- 경기 시뮬레이션 엔진 ---
def simulate_match_score(team1_code, team2_code):
    teams_dict = TEAMS if st.session_state.get("tournament_mode", "worldcup") == "worldcup" else CL_TEAMS
    t1 = teams_dict[team1_code]
    t2 = teams_dict[team2_code]
    diff = t1["points"] - t2["points"]
    
    # 기본 골 범위 설정 (평균 1.3골 수준)
    g1 = random.randint(0, 2)
    g2 = random.randint(0, 2)
    
    # FIFA 랭킹 포인트 차이에 따른 가중치 부여
    if diff > 0:
        win_chance = min(0.8, 0.3 + (diff / 400.0))
        if random.random() < win_chance:
            g1 += random.randint(0, 2)
    else:
        win_chance = min(0.8, 0.3 - (diff / 400.0))
        if random.random() < win_chance:
            g2 += random.randint(0, 2)
            
    return g1, g2

# --- 세션 상태 초기화 ---
if "selected_nation" not in st.session_state:
    st.session_state.selected_nation = "KOR"

if "tournament_step" not in st.session_state:
    st.session_state.tournament_step = "not_started" # not_started, group_stage, wildcard, knockout, completed

if "user_team" not in st.session_state:
    st.session_state.user_team = None

if "groups" not in st.session_state:
    st.session_state.groups = {}

if "group_matches" not in st.session_state:
    st.session_state.group_matches = []

if "bracket_matches" not in st.session_state:
    st.session_state.bracket_matches = {} # { "32강": [...], "16강": [...], ... }

if "current_knockout_round" not in st.session_state:
    st.session_state.current_knockout_round = "32강"

if "last_processed_timestamp" not in st.session_state:
    st.session_state.last_processed_timestamp = 0

if "active_playable_match" not in st.session_state:
    st.session_state.active_playable_match = None

if "penalty_shootout" not in st.session_state:
    st.session_state.penalty_shootout = None

# --- 헤더 섹션 ---
st.markdown('<div class="header-title">2026 FIFA WORLD CUP</div>', unsafe_allow_html=True)
st.markdown('<div class="header-subtitle">Streamlit 대시보드 & 2D 플레이어블 축구 시뮬레이션</div>', unsafe_allow_html=True)

# 탭 메뉴 구성
tab1, tab2 = st.tabs(["📊 실시간 FIFA 랭킹 & 라인업 시각화", "🏆 토너먼트 모드 플레이 (월드컵 & UCL)"])

# ==========================================
# 탭 1: FIFA 랭킹 & 라인업 시각화
# ==========================================
with tab1:
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown('<div class="glass-card"><h4>🌍 FIFA 월드 랭킹</h4></div>', unsafe_allow_html=True)
        df_rankings = get_rankings_df()
        
        # 검색 필터
        search_query = st.text_input("🔍 국가명 검색", "", key="ranking_search")
        if search_query:
            df_filtered = df_rankings[df_rankings["국가"].str.contains(search_query)]
        else:
            df_filtered = df_rankings
            
        # 테이블 표시 (선택 가능한 라인업 연동을 위해 버튼으로 리스트화)
        st.write("아래 국가를 선택하여 전술 피치 라인업을 시각화하세요:")
        
        # 리스트 그리드 뷰 구성
        for idx, row in df_filtered.iterrows():
            btn_label = f"#{row['FIFA 랭킹']} {row['국가']} ({row['대륙']} - {row['포인트']}pts)"
            # 현재 선택된 국가면 하이라이트
            if row['코드'] == st.session_state.selected_nation:
                if st.button(f"👉 {btn_label}", key=f"btn_{row['코드']}", use_container_width=True):
                    pass
            else:
                if st.button(btn_label, key=f"btn_{row['코드']}", use_container_width=True):
                    st.session_state.selected_nation = row['코드']
                    st.rerun()

    with col2:
        selected_code = st.session_state.selected_nation
        team_info = TEAMS.get(selected_code)
        
        if team_info:
            st.markdown(f'<div class="glass-card"><h3>⚽ {team_info["name"]} 전술 피치 시각화</h3></div>', unsafe_allow_html=True)
            
            # Plotly 축구 전술 피치 그리기
            fig = go.Figure()
            
            # 피치 배경 (초록색 그라데이션 대신 단색에 경계라인)
            fig.add_shape(type="rect", x0=0, y0=0, x1=100, y1=100, fillcolor="#1b5e20", line=dict(color="white", width=2))
            # 센터라인
            fig.add_shape(type="line", x0=0, y0=50, x1=100, y1=50, line=dict(color="white", width=2))
            # 센터 서클
            fig.add_shape(type="circle", x0=35, y0=35, x1=65, y1=65, line=dict(color="white", width=2))
            # 하단 페널티 에어리어 (수비진)
            fig.add_shape(type="rect", x0=20, y0=0, x1=80, y1=18, line=dict(color="white", width=1.5))
            # 상단 페널티 에어리어 (공격진)
            fig.add_shape(type="rect", x0=20, y0=82, x1=80, y1=100, line=dict(color="white", width=1.5))
            # 골대 구조물 그리기
            fig.add_shape(type="rect", x0=40, y0=-2, x1=60, y1=0, line=dict(color="white", width=2))
            fig.add_shape(type="rect", x0=40, y0=100, x1=60, y1=102, line=dict(color="white", width=2))
            
            # 선수들 배치 플로팅
            xs = [p["x"] for p in team_info["lineup"]]
            ys = [p["y"] for p in team_info["lineup"]]
            names = [f"<b>{p['name']}</b><br>({p['pos']})" for p in team_info["lineup"]]
            
            fig.add_trace(go.Scatter(
                x=xs,
                y=ys,
                mode="markers+text",
                text=names,
                textposition="bottom center",
                textfont=dict(color="white", size=10),
                marker=dict(
                    size=16,
                    color=team_info["primary_color"],
                    line=dict(width=2, color=team_info["secondary_color"])
                ),
                hoverinfo="text"
            ))
            
            fig.update_layout(
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-5, 105]),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-5, 105]),
                width=500,
                height=550,
                margin=dict(l=10, r=10, t=10, b=10),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                showlegend=False
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # 감독 및 교체명단 디테일 카드
            st.markdown(f"""
                <div class="glass-card">
                    <h5>📋 스쿼드 디테일</h5>
                    <p><b>감독:</b> {team_info['manager']}</p>
                    <p><b>교체 명단:</b></p>
                    <div>
                        {' '.join([f'<span class="badge-secondary">{s}</span>' for s in team_info['subs']])}
                    </div>
                </div>
            """, unsafe_allow_html=True)

# ==========================================
# 탭 2: 월드컵 2026 모드 플레이
# ==========================================
with tab2:
    if "tournament_mode" not in st.session_state:
        st.session_state.tournament_mode = "worldcup"
    CURRENT_TEAMS = TEAMS if st.session_state.tournament_mode == "worldcup" else CL_TEAMS
    
    # ----------------------------------------
    # 2D 축구 경기 플레이용 Iframe 렌더러 함수
    # ----------------------------------------
    def render_active_game_iframe(user_code, opp_code, match_type="group", match_idx=None, bracket_round=None):
        u_team = CURRENT_TEAMS[user_code]
        o_team = CURRENT_TEAMS[opp_code]
        
        desc = "방향키(이동)와 S/W/A/D/E(패스, 슛, 달리기)를 활용해 경기를 지배하세요!" if st.session_state.tournament_mode == "champions" else "방향키(이동)와 스페이스바(슛)를 눌러 경기를 끝까지 직접 플레이하세요!"
        st.markdown(f'<div class="glass-card" style="text-align: center;"><h3>🎮 매치 시작: {u_team["name"]} vs {o_team["name"]}</h3><p>{desc}</p></div>', unsafe_allow_html=True)
        
        # 컴포넌트 선언 및 호출
        parent_dir = os.path.dirname(os.path.abspath(__file__))
        build_dir = os.path.join(parent_dir, "game_component")
        soccer_game = components.declare_component("soccer_game", path=build_dir)
        
        # 유저 팀 및 상대 팀 라인업 명단 추출 및 직렬화
        import json
        user_lineup_names = [p.get("name", "선수") for p in u_team.get("lineup", [])]
        user_lineup_json = json.dumps(user_lineup_names)
        
        opponent_lineup_names = [p.get("name", "선수") for p in o_team.get("lineup", [])]
        opponent_lineup_json = json.dumps(opponent_lineup_names)

        frame_height = 635 if st.session_state.tournament_mode == "champions" else 535
        game_result = soccer_game(
            user_team=u_team["name"],
            opponent_team=o_team["name"],
            user_color=u_team["primary_color"],
            opponent_color=o_team["primary_color"],
            user_text_color=u_team["secondary_color"],
            opponent_text_color=o_team["secondary_color"],
            match_type=match_type,
            user_points=u_team["points"],
            opponent_points=o_team["points"],
            tournament_mode=st.session_state.tournament_mode,
            user_lineup=user_lineup_json,
            opponent_lineup=opponent_lineup_json,
            height=frame_height,
            key=f"playable_match_{user_code}_{opp_code}_{match_idx}_{bracket_round}"
        )
        
        # 결과 처리 로직 (중복 업데이트 방지용 타임스탬프 체크 적용)
        if game_result and game_result.get("status") == "completed":
            completed_time = game_result.get("timestamp", 0)
            if completed_time > st.session_state.last_processed_timestamp:
                st.session_state.last_processed_timestamp = completed_time
                
                user_score = game_result["userScore"]
                opp_score = game_result["aiScore"]
                user_pk = game_result.get("userPKScore")
                opp_pk = game_result.get("aiPKScore")
                
                # 매치 결과 저장
                if match_type == "group" and match_idx is not None:
                    # 조별 리그 경기 결과 반영 (홈/어웨이에 따른 스코어 정렬)
                    match_data = st.session_state.group_matches[match_idx]
                    if match_data["team1"] == user_code:
                        match_data["score1"] = user_score
                        match_data["score2"] = opp_score
                    else:
                        match_data["score1"] = opp_score
                        match_data["score2"] = user_score
                    match_data["played"] = True
                    st.success(f"경기 종료! 최종 스코어: {u_team['name']} {user_score} - {opp_score} {o_team['name']}")
                
                elif match_type == "knockout" and bracket_round and match_idx is not None:
                    # 토너먼트 경기 결과 반영 (홈/어웨이에 따른 스코어 정렬)
                    match_data = st.session_state.bracket_matches[bracket_round][match_idx]
                    
                    if user_pk is not None and opp_pk is not None:
                        # 게임 컴포넌트 내부에서 승부차기까지 완료된 경우
                        u_tot = f"{user_score} ({user_pk})"
                        o_tot = f"{opp_score} ({opp_pk})"
                        
                        if match_data["team1"] == user_code:
                            match_data["score1"] = u_tot
                            match_data["score2"] = o_tot
                        else:
                            match_data["score1"] = o_tot
                            match_data["score2"] = u_tot
                            
                        match_data["played"] = True
                        winner = user_code if user_pk > opp_pk else opp_code
                        match_data["winner"] = winner
                        st.success(f"경기 종료 (승부차기)! 최종 스코어: {u_team['name']} {u_tot} - {o_tot} {o_team['name']}")
                    else:
                        # 게임 컴포넌트에서 PK를 안 거치고 온 경우 (동점 시 Streamlit 승부차기로 진입)
                        if user_score == opp_score:
                            st.session_state.penalty_shootout = {
                                "round": bracket_round,
                                "idx": match_idx,
                                "user_code": user_code,
                                "opp_code": opp_code,
                                "user_score": user_score,
                                "opp_score": opp_score,
                                "user_pk": [],
                                "opp_pk": [],
                                "step": 0
                            }
                        else:
                            if match_data["team1"] == user_code:
                                match_data["score1"] = user_score
                                match_data["score2"] = opp_score
                            else:
                                match_data["score1"] = opp_score
                                match_data["score2"] = user_score
                            match_data["played"] = True
                            winner = user_code if user_score > opp_score else opp_code
                            match_data["winner"] = winner
                            st.success(f"경기 종료! 최종 스코어: {u_team['name']} {user_score} - {opp_score} {o_team['name']}")
                
                # 플레이 경기 비활성화 및 리프레시
                st.session_state.active_playable_match = None
                time.sleep(1)
                st.rerun()

    # ----------------------------------------
    # 승부차기(Penalty Shootout) 인터랙티브 시뮬레이션
    # ----------------------------------------
    if st.session_state.penalty_shootout:
        pk = st.session_state.penalty_shootout
        st.markdown('<div class="glass-card"><h3>⚽ 연장 무승부! 승부차기 돌입 ⚽</h3></div>', unsafe_allow_html=True)
        st.write(f"**{TEAMS[pk['user_code']]['name']} (사용자)** vs **{TEAMS[pk['opp_code']]['name']} (AI)**")
        
        # 킥 히스토리 렌더링
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f"**{TEAMS[pk['user_code']]['name']}**: " + " ".join([f"🟢" if x else "🔴" for x in pk["user_pk"]]))
        with c2:
            st.markdown(f"**{TEAMS[pk['opp_code']]['name']}**: " + " ".join([f"🟢" if x else "🔴" for x in pk["opp_pk"]]))
            
        # 승부 판정 체크
        user_sc = sum(pk["user_pk"])
        opp_sc = sum(pk["opp_pk"])
        turns = len(pk["user_pk"])
        
        winner = None
        # 정규 5키커 판단
        if turns >= 5:
            if user_sc != opp_sc:
                winner = pk["user_code"] if user_sc > opp_sc else pk["opp_code"]
        else:
            # 5번 다 안 찼어도 수학적으로 승부 결정 시
            rem = 5 - turns
            if user_sc > opp_sc + rem:
                winner = pk["user_code"]
            elif opp_sc > user_sc + rem:
                winner = pk["opp_code"]
                
        # 서든데스 (5라운드 이후 동점 시)
        if turns >= 5 and winner is None:
            if len(pk["user_pk"]) == len(pk["opp_pk"]):
                # 양쪽 다 찼는데 점수가 다르면 결정
                if user_sc != opp_sc:
                    winner = pk["user_code"] if user_sc > opp_sc else pk["opp_code"]

        if winner:
            st.success(f"승부차기 종료! 최종 승자: {CURRENT_TEAMS[winner]['name']}")
            if st.button("토너먼트 대진 결과 등록"):
                # 토너먼트 매치 결과 업데이트
                round_name = pk["round"]
                m_idx = pk["idx"]
                
                # 표기용 스코어 지정
                u_tot = f"{pk['user_score']} ({user_sc})"
                o_tot = f"{pk['opp_score']} ({opp_sc})"
                
                st.session_state.bracket_matches[round_name][m_idx]["score1"] = u_tot
                st.session_state.bracket_matches[round_name][m_idx]["score2"] = o_tot
                st.session_state.bracket_matches[round_name][m_idx]["played"] = True
                st.session_state.bracket_matches[round_name][m_idx]["winner"] = winner
                
                st.session_state.penalty_shootout = None
                st.rerun()
        else:
            # 다음 키커 차기 진행
            if st.button("⚽ 키커 슛 하기"):
                user_success = random.random() < 0.75 # 75% 득점률
                opp_success = random.random() < 0.75
                
                pk["user_pk"].append(user_success)
                pk["opp_pk"].append(opp_success)
                pk["step"] += 1
                st.rerun()

    # 1. 월드컵/챔피언스리그 시작 전 (대회 선택, 국가/클럽 선택, 조 추첨 방식)
    if st.session_state.tournament_step == "not_started":
        st.markdown('<div class="glass-card"><h3>🏆 토너먼트 시뮬레이터 시작</h3><p>대회 모드와 조 추첨 방식을 선택하고 플레이를 시작해 보세요.</p></div>', unsafe_allow_html=True)
        
        # 대회 유형 선택
        tournament_mode = st.radio("🏆 대회 모드 선택", ["🏆 월드컵 2026 (48개국)", "🇪🇺 UEFA 챔피언스 리그 (32개 클럽)"], horizontal=True)
        st.session_state.tournament_mode = "worldcup" if "월드컵" in tournament_mode else "champions"
        
        CURRENT_TEAMS = TEAMS if st.session_state.tournament_mode == "worldcup" else CL_TEAMS
        
        # 참가 팀 선택
        user_choice = st.selectbox(
            "참가 팀 선택", 
            options=list(CURRENT_TEAMS.keys()), 
            format_func=lambda k: f"{CURRENT_TEAMS[k]['name']} (FIFA {CURRENT_TEAMS[k]['rank']}위 / OVR {CURRENT_TEAMS[k]['points']})" if st.session_state.tournament_mode == "worldcup" else f"{CURRENT_TEAMS[k]['name']} (OVR {CURRENT_TEAMS[k]['points']})"
        )
        
        # 조 추첨 방식
        draw_mode = st.radio("조 편성 방식 선택", ["🎲 자동 무작위 조 추첨", "🔮 조 추첨식 직접 진행"], horizontal=True)
        
        # 참가 팀 목록 구성 (사용자가 선택한 팀을 반드시 포함하고, 나머지는 랭킹 순으로 참가 채움)
        expected_size = 48 if st.session_state.tournament_mode == "worldcup" else 32
        all_codes = list(CURRENT_TEAMS.keys())
        
        participating = [user_choice]
        other_codes = [c for c in all_codes if c != user_choice]
        other_codes_sorted = sorted(other_codes, key=lambda k: CURRENT_TEAMS[k]["rank"])
        participating.extend(other_codes_sorted[:expected_size - 1])
        
        # 참가하는 팀들을 랭킹순 정렬하여 포트 분할
        sorted_codes = sorted(participating, key=lambda k: CURRENT_TEAMS[k]["rank"])
        
        pot_size = 12 if st.session_state.tournament_mode == "worldcup" else 8
        pot1 = sorted_codes[0:pot_size]
        pot2 = sorted_codes[pot_size:2*pot_size]
        pot3 = sorted_codes[2*pot_size:3*pot_size]
        pot4 = sorted_codes[3*pot_size:4*pot_size]
        
        group_letters = [chr(i) for i in range(ord('A'), ord('L')+1)] if st.session_state.tournament_mode == "worldcup" else [chr(i) for i in range(ord('A'), ord('H')+1)]
        
        if draw_mode == "🔮 조 추첨식 직접 진행":
            # 세션 상태 변수 초기화
            if "draw_idx" not in st.session_state or st.session_state.get("last_draw_mode") != st.session_state.tournament_mode:
                st.session_state.last_draw_mode = st.session_state.tournament_mode
                st.session_state.draw_idx = 0
                st.session_state.draw_pots = {
                    1: pot1.copy(),
                    2: pot2.copy(),
                    3: pot3.copy(),
                    4: pot4.copy()
                }
                st.session_state.draw_groups = {gn: [] for gn in group_letters}
                st.session_state.draw_history = []
                st.session_state.last_drawn_team = None
                st.session_state.last_drawn_group = None
            
            draw_idx = st.session_state.draw_idx
            draw_pots = st.session_state.draw_pots
            draw_groups = st.session_state.draw_groups
            
            total_teams = 48 if st.session_state.tournament_mode == "worldcup" else 32
            group_count = 12 if st.session_state.tournament_mode == "worldcup" else 8
            
            # 상단 현황판 및 조작부
            st.write("---")
            st.markdown("### 🔮 실시간 대화형 조 추첨식")
            
            # 방금 추첨된 팀 효과 카드
            if st.session_state.last_drawn_team:
                team_info = CURRENT_TEAMS[st.session_state.last_drawn_team]
                team_name = team_info["name"]
                team_group = st.session_state.last_drawn_group
                team_color = team_info.get("primary_color", "#38bdf8")
                
                st.markdown(f"""
                    <div style="text-align:center; padding: 1.5rem; background: rgba(255,255,255,0.05); border-radius: 12px; margin-bottom: 1.5rem; border: 2px solid {team_color}; box-shadow: 0 0 15px {team_color}33;">
                        <span style="font-size:1.1rem; color:#94a3b8; font-weight:bold;">🔥 방금 추첨된 팀</span>
                        <h2 style="margin: 0.5rem 0; color:#FFFFFF; font-size:2.2rem; font-weight:800; text-shadow: 0 0 10px {team_color};">⚽ {team_name}</h2>
                        <span style="font-size:1.4rem; font-weight:900; color:#10b981;">👉 Group {team_group}조 배치!</span>
                    </div>
                """, unsafe_allow_html=True)
            
            # 버튼 조작부
            col_btn1, col_btn2 = st.columns(2)
            
            if draw_idx < total_teams:
                # 활성 포트
                active_pot_num = (draw_idx // group_count) + 1
                active_group_letter = group_letters[draw_idx % group_count]
                
                with col_btn1:
                    if st.button(f"🔮 포트 {active_pot_num}에서 다음 팀 추첨하기", type="primary", use_container_width=True):
                        # 랜덤 추첨
                        pot_list = draw_pots[active_pot_num]
                        drawn_code = random.choice(pot_list)
                        
                        # 상태 업데이트
                        pot_list.remove(drawn_code)
                        draw_groups[active_group_letter].append(drawn_code)
                        st.session_state.draw_history.append(f"🗳️ [Port {active_pot_num}] {CURRENT_TEAMS[drawn_code]['name']} -> Group {active_group_letter}")
                        
                        st.session_state.last_drawn_team = drawn_code
                        st.session_state.last_drawn_group = active_group_letter
                        st.session_state.draw_idx += 1
                        st.rerun()
                
                with col_btn2:
                    if st.button("⚡ 남은 모든 팀 일괄 추첨", use_container_width=True):
                        # 남은 과정 자동 일괄 진행
                        while st.session_state.draw_idx < total_teams:
                            d_idx = st.session_state.draw_idx
                            p_num = (d_idx // group_count) + 1
                            g_let = group_letters[d_idx % group_count]
                            
                            pot_list = draw_pots[p_num]
                            drawn_code = random.choice(pot_list)
                            
                            pot_list.remove(drawn_code)
                            draw_groups[g_let].append(drawn_code)
                            st.session_state.draw_history.append(f"🗳️ [Port {p_num}] {CURRENT_TEAMS[drawn_code]['name']} -> Group {g_let}")
                            
                            st.session_state.last_drawn_team = drawn_code
                            st.session_state.last_drawn_group = g_let
                            st.session_state.draw_idx += 1
                        st.rerun()
            else:
                # 추첨 완료
                st.success("✅ 모든 팀의 조 추첨식이 성공적으로 완료되었습니다!")
                
                if st.button("🏆 대회 개막 및 조별리그 시작", type="primary", use_container_width=True):
                    st.session_state.user_team = user_choice
                    st.session_state.groups = draw_groups.copy()
                    
                    # 경기 일정 구성
                    group_matches = []
                    for gn, teams in st.session_state.groups.items():
                        match_indices = [(0,1), (2,3), (0,2), (1,3), (0,3), (1,2)]
                        for m_i, (t1_idx, t2_idx) in enumerate(match_indices):
                            group_matches.append({
                                "group": gn,
                                "round": (m_i // 2) + 1,
                                "team1": teams[t1_idx],
                                "team2": teams[t2_idx],
                                "score1": None,
                                "score2": None,
                                "played": False
                            })
                    st.session_state.group_matches = group_matches
                    st.session_state.tournament_step = "group_stage"
                    
                    # 추첨 세션 상태들 청소
                    if "draw_idx" in st.session_state: del st.session_state.draw_idx
                    if "draw_pots" in st.session_state: del st.session_state.draw_pots
                    if "draw_groups" in st.session_state: del st.session_state.draw_groups
                    if "draw_history" in st.session_state: del st.session_state.draw_history
                    if "last_drawn_team" in st.session_state: del st.session_state.last_drawn_team
                    if "last_drawn_group" in st.session_state: del st.session_state.last_drawn_group
                    st.rerun()
            
            # 포트 잔여 팀 상황판 시각화
            st.markdown("#### 📦 포트별 미추첨 리스트")
            col_p1, col_p2, col_p3, col_p4 = st.columns(4)
            with col_p1:
                st.write("**Pot 1**")
                p1_names = [CURRENT_TEAMS[c]["name"] for c in draw_pots[1]]
                st.caption(", ".join(p1_names) if p1_names else "추첨 완료")
            with col_p2:
                st.write("**Pot 2**")
                p2_names = [CURRENT_TEAMS[c]["name"] for c in draw_pots[2]]
                st.caption(", ".join(p2_names) if p2_names else "추첨 완료")
            with col_p3:
                st.write("**Pot 3**")
                p3_names = [CURRENT_TEAMS[c]["name"] for c in draw_pots[3]]
                st.caption(", ".join(p3_names) if p3_names else "추첨 완료")
            with col_p4:
                st.write("**Pot 4**")
                p4_names = [CURRENT_TEAMS[c]["name"] for c in draw_pots[4]]
                st.caption(", ".join(p4_names) if p4_names else "추첨 완료")
            
            # 실시간 조별 채우기 현황 시각화
            st.markdown("#### 📋 실시간 조별 배치 현황")
            cols_g = st.columns(3 if st.session_state.tournament_mode == "worldcup" else 4)
            for idx, gn in enumerate(group_letters):
                col_idx = idx % (3 if st.session_state.tournament_mode == "worldcup" else 4)
                with cols_g[col_idx]:
                    st.markdown(f"**Group {gn}**")
                    teams_in_group = draw_groups[gn]
                    for slot_idx in range(4):
                        if slot_idx < len(teams_in_group):
                            team_code = teams_in_group[slot_idx]
                            st.write(f"Slot {slot_idx+1}: **{CURRENT_TEAMS[team_code]['name']}**")
                        else:
                            st.write(f"Slot {slot_idx+1}: *대기 중*")
            
            # 최근 조 추첨 로그 5개 노출
            if st.session_state.draw_history:
                st.write("---")
                st.markdown("##### 📜 최근 조 추첨 역사")
                for log in reversed(st.session_state.draw_history[-5:]):
                    st.caption(log)
                    
        else:
            # 자동 무작위 조 추첨
            if st.button("🎲 조 추첨 및 대회 개막", type="primary", use_container_width=True):
                st.session_state.user_team = user_choice
                
                p1_shuf = pot1.copy()
                p2_shuf = pot2.copy()
                p3_shuf = pot3.copy()
                p4_shuf = pot4.copy()
                random.shuffle(p1_shuf)
                random.shuffle(p2_shuf)
                random.shuffle(p3_shuf)
                random.shuffle(p4_shuf)
                
                groups = {gn: [p1_shuf[i], p2_shuf[i], p3_shuf[i], p4_shuf[i]] for i, gn in enumerate(group_letters)}
                st.session_state.groups = groups
                
                group_matches = []
                for gn, teams in groups.items():
                    match_indices = [(0,1), (2,3), (0,2), (1,3), (0,3), (1,2)]
                    for m_i, (t1_idx, t2_idx) in enumerate(match_indices):
                        group_matches.append({
                            "group": gn,
                            "round": (m_i // 2) + 1,
                            "team1": teams[t1_idx],
                            "team2": teams[t2_idx],
                            "score1": None,
                            "score2": None,
                            "played": False
                        })
                st.session_state.group_matches = group_matches
                st.session_state.tournament_step = "group_stage"
                st.rerun()

    # 2. 조별 리그 진행 중
    elif st.session_state.tournament_step == "group_stage":
        st.markdown(f'<div class="glass-card"><h3>⚽ 조별 리그 진행 중 (선택 팀: {CURRENT_TEAMS[st.session_state.user_team]["name"]})</h3></div>', unsafe_allow_html=True)
        
        # 조별 리그 경기 수동 플레이 모드 실행 중인 경우
        if st.session_state.active_playable_match:
            apm = st.session_state.active_playable_match
            render_active_game_iframe(apm["user_code"], apm["opp_code"], "group", apm["match_idx"])
            
        else:
            # 조별 리그 매치 상황판 및 시뮬레이션 버튼들
            c1, c2 = st.columns([1.5, 2])
            
            # --- 조별 스탠딩 현황 연산 ---
            group_standings = {}
            for gn, teams in st.session_state.groups.items():
                stands = {t: {"points": 0, "gd": 0, "gs": 0, "w": 0, "d": 0, "l": 0, "mp": 0} for t in teams}
                
                # 매치 결과 집계
                for m in st.session_state.group_matches:
                    if m["group"] == gn and m["played"]:
                        t1, t2 = m["team1"], m["team2"]
                        s1, s2 = m["score1"], m["score2"]
                        
                        stands[t1]["mp"] += 1
                        stands[t2]["mp"] += 1
                        stands[t1]["gs"] += s1
                        stands[t2]["gs"] += s2
                        stands[t1]["gd"] += (s1 - s2)
                        stands[t2]["gd"] += (s2 - s1)
                        
                        if s1 > s2:
                            stands[t1]["points"] += 3
                            stands[t1]["w"] += 1
                            stands[t2]["l"] += 1
                        elif s1 < s2:
                            stands[t2]["points"] += 3
                            stands[t2]["w"] += 1
                            stands[t1]["l"] += 1
                        else:
                            stands[t1]["points"] += 1
                            stands[t2]["points"] += 1
                            stands[t1]["d"] += 1
                            stands[t2]["d"] += 1
                            
                # 정렬 규칙: 승점 -> 골득실 -> 다득점
                sorted_stands = sorted(stands.items(), key=lambda x: (x[1]["points"], x[1]["gd"], x[1]["gs"]), reverse=True)
                group_standings[gn] = sorted_stands

            with c1:
                st.subheader("📋 조별 리그 순위표")
                
                # 조별 순위 아코디언 형태로 이쁘게 보기
                for gn in sorted(list(st.session_state.groups.keys())):
                    with st.expander(f"Group {gn} 순위", expanded=(gn == 'A')):
                        data_rows = []
                        for rank, (team_code, stats) in enumerate(group_standings[gn]):
                            prefix = "✅" if rank < 2 else "⏳"
                            data_rows.append({
                                "순위": f"{prefix} {rank+1}",
                                "팀": CURRENT_TEAMS[team_code]["name"],
                                "경기": stats["mp"],
                                "승": stats["w"],
                                "무": stats["d"],
                                "패": stats["l"],
                                "득실": stats["gd"],
                                "득점": stats["gs"],
                                "승점": stats["points"]
                            })
                        st.table(pd.DataFrame(data_rows).set_index("순위"))

            with c2:
                st.subheader("📅 경기 목록 및 시뮬레이션")
                
                # 아직 진행 안 된 경기 개수 계산
                unplayed_count = sum(1 for m in st.session_state.group_matches if not m["played"])
                
                # 시뮬레이션 컨트롤
                col_sim1, col_sim2 = st.columns(2)
                with col_sim1:
                    if st.button("⚡ 타국가 경기 전부 시뮬레이션", use_container_width=True):
                        # 사용자가 속하지 않은 모든 경기를 바로 랜덤 결과로 채우기
                        for idx, m in enumerate(st.session_state.group_matches):
                            if not m["played"]:
                                if m["team1"] != st.session_state.user_team and m["team2"] != st.session_state.user_team:
                                    s1, s2 = simulate_match_score(m["team1"], m["team2"])
                                    st.session_state.group_matches[idx]["score1"] = s1
                                    st.session_state.group_matches[idx]["score2"] = s2
                                    st.session_state.group_matches[idx]["played"] = True
                        st.success("타 국가들의 경기 시뮬레이션이 모두 완료되었습니다!")
                        st.rerun()
                
                with col_sim2:
                    # 모든 조별 예선 종료 시 다음으로 버튼 활성화
                    if unplayed_count == 0:
                        if st.session_state.tournament_mode == "worldcup":
                            if st.button("⏩ 조별 예선 종료 (와일드카드 단계로)", type="primary", use_container_width=True):
                                st.session_state.tournament_step = "wildcard"
                                st.rerun()
                        else:
                            if st.button("⏩ 조별 예선 종료 (16강 결선 토너먼트로)", type="primary", use_container_width=True):
                                group_winners = []
                                group_runners_up = []
                                for gn in sorted(list(st.session_state.groups.keys())):
                                    stands = {t: {"points": 0, "gd": 0, "gs": 0} for t in st.session_state.groups[gn]}
                                    for m in st.session_state.group_matches:
                                        if m["group"] == gn and m["played"]:
                                            t1, t2 = m["team1"], m["team2"]
                                            s1, s2 = m["score1"], m["score2"]
                                            if s1 > s2:
                                                stands[t1]["points"] += 3
                                                stands[t1]["gd"] += (s1 - s2)
                                                stands[t2]["gd"] += (s2 - s1)
                                                stands[t1]["gs"] += s1
                                                stands[t2]["gs"] += s2
                                            elif s1 < s2:
                                                stands[t2]["points"] += 3
                                                stands[t2]["gd"] += (s2 - s1)
                                                stands[t1]["gd"] += (s1 - s2)
                                                stands[t2]["gs"] += s2
                                                stands[t1]["gs"] += s1
                                            else:
                                                stands[t1]["points"] += 1
                                                stands[t2]["points"] += 1
                                                stands[t1]["gd"] += (s1 - s2)
                                                stands[t2]["gd"] += (s2 - s1)
                                                stands[t1]["gs"] += s1
                                                stands[t2]["gs"] += s2
                                    sorted_stands = sorted(stands.items(), key=lambda x: (x[1]["points"], x[1]["gd"], x[1]["gs"]), reverse=True)
                                    group_winners.append(sorted_stands[0][0])
                                    group_runners_up.append(sorted_stands[1][0])
                                
                                # A1 vs B2, B1 vs A2, C1 vs D2, D1 vs C2, E1 vs F2, F1 vs E2, G1 vs H2, H1 vs G2
                                bracket_16 = []
                                pairing = [(0, 1), (1, 0), (2, 3), (3, 2), (4, 5), (5, 4), (6, 7), (7, 6)]
                                for w_idx, r_idx in pairing:
                                    bracket_16.append({
                                        "team1": group_winners[w_idx],
                                        "team2": group_runners_up[r_idx],
                                        "score1": None,
                                        "score2": None,
                                        "winner": None,
                                        "played": False
                                    })
                                
                                st.session_state.bracket_matches = {
                                    "16강": bracket_16,
                                    "8강": [],
                                    "4강": [],
                                    "결승": []
                                }
                                st.session_state.current_knockout_round = "16강"
                                st.session_state.tournament_step = "knockout"
                                st.rerun()
                
                # 경기 목록 표시
                st.write("---")
                user_matches = []
                other_matches = []
                
                for idx, m in enumerate(st.session_state.group_matches):
                    item = {"idx": idx, "data": m}
                    if m["team1"] == st.session_state.user_team or m["team2"] == st.session_state.user_team:
                        user_matches.append(item)
                    else:
                        other_matches.append(item)
                
                st.markdown("##### 🔴 우리 팀 경기 (직접 플레이 필수)")
                for item in user_matches:
                    m = item["data"]
                    idx = item["idx"]
                    t1_name = CURRENT_TEAMS[m["team1"]]["name"]
                    t2_name = CURRENT_TEAMS[m["team2"]]["name"]
                    
                    if m["played"]:
                        st.markdown(f'<div class="standing-card">🏆 <b>[R{m["round"]}]</b> {t1_name} <b>{m["score1"]} : {m["score2"]}</b> {t2_name} (완료)</div>', unsafe_allow_html=True)
                    else:
                        st.write(f"🏆 **[R{m['round']}]** {t1_name} vs {t2_name}")
                        if st.button(f"🎮 {t1_name} 경기 플레이하기", key=f"play_group_{idx}"):
                            # 2D 축구게임 실행을 위해 세션 셋팅
                            user_side = m["team1"] if m["team1"] == st.session_state.user_team else m["team2"]
                            opp_side = m["team2"] if m["team1"] == st.session_state.user_team else m["team1"]
                            st.session_state.active_playable_match = {
                                "user_code": user_side,
                                "opp_code": opp_side,
                                "match_idx": idx
                            }
                            st.rerun()
                
                st.markdown("##### 🌐 다른 그룹 경기 일정 요약 (일부 미완료 건 퀵 롤 시뮬 가능)")
                for item in other_matches[:10]: # 10개만 리스트에 표시
                    m = item["data"]
                    idx = item["idx"]
                    t1_name = CURRENT_TEAMS[m["team1"]]["name"]
                    t2_name = CURRENT_TEAMS[m["team2"]]["name"]
                    
                    if m["played"]:
                        st.markdown(f'<div style="font-size:0.9rem; margin-bottom:4px;">Group {m["group"]} R{m["round"]}: {t1_name} {m["score1"]} - {m["score2"]} {t2_name}</div>', unsafe_allow_html=True)
                    else:
                        col_m1, col_m2 = st.columns([3, 1])
                        with col_m1:
                            st.markdown(f'<div style="font-size:0.9rem; margin-top:5px;">Group {m["group"]} R{m["round"]}: {t1_name} vs {t2_name}</div>', unsafe_allow_html=True)
                        with col_m2:
                            if st.button("⚡시뮬", key=f"quick_sim_{idx}"):
                                s1, s2 = simulate_match_score(m["team1"], m["team2"])
                                st.session_state.group_matches[idx]["score1"] = s1
                                st.session_state.group_matches[idx]["score2"] = s2
                                st.session_state.group_matches[idx]["played"] = True
                                st.rerun()

    # 3. 와일드카드 판정 단계 (3위 팀들 중 8개국 선발)
    elif st.session_state.tournament_step == "wildcard":
        st.markdown('<div class="glass-card"><h3>📊 조별 3위 와일드카드 트래커 (Wildcard Tracker)</h3><p>각 조 3위 12개 국가를 비교 평가하여, 상위 8개 국가가 32강에 마지막으로 합류합니다.</p></div>', unsafe_allow_html=True)
        
        # 각 조 3위 데이터 수집
        third_place_teams = []
        for gn in sorted(list(st.session_state.groups.keys())):
            # 각 조 3위 팀 추출
            stands = {t: {"points": 0, "gd": 0, "gs": 0} for t in st.session_state.groups[gn]}
            for m in st.session_state.group_matches:
                if m["group"] == gn and m["played"]:
                    t1, t2 = m["team1"], m["team2"]
                    s1, s2 = m["score1"], m["score2"]
                    if s1 > s2:
                        stands[t1]["points"] += 3
                        stands[t1]["gd"] += (s1 - s2)
                        stands[t2]["gd"] += (s2 - s1)
                        stands[t1]["gs"] += s1
                        stands[t2]["gs"] += s2
                    elif s1 < s2:
                        stands[t2]["points"] += 3
                        stands[t2]["gd"] += (s2 - s1)
                        stands[t1]["gd"] += (s1 - s2)
                        stands[t2]["gs"] += s2
                        stands[t1]["gs"] += s1
                    else:
                        stands[t1]["points"] += 1
                        stands[t2]["points"] += 1
                        stands[t1]["gd"] += (s1 - s2)
                        stands[t2]["gd"] += (s2 - s1)
                        stands[t1]["gs"] += s1
                        stands[t2]["gs"] += s2
            
            sorted_stands = sorted(stands.items(), key=lambda x: (x[1]["points"], x[1]["gd"], x[1]["gs"]), reverse=True)
            # 3위 팀 추가
            third_place_teams.append({
                "group": gn,
                "team_code": sorted_stands[2][0],
                "points": sorted_stands[2][1]["points"],
                "gd": sorted_stands[2][1]["gd"],
                "gs": sorted_stands[2][1]["gs"]
            })
            
        # 모든 3위 팀 순위 정렬
        sorted_third_places = sorted(third_place_teams, key=lambda x: (x["points"], x["gd"], x["gs"]), reverse=True)
        
        # 표 구성
        wildcard_rows = []
        advancing_third_codes = []
        for i, item in enumerate(sorted_third_places):
            is_advanced = i < 8
            prefix = "✅ 32강 진출" if is_advanced else "❌ 탈락"
            if is_advanced:
                advancing_third_codes.append(item["team_code"])
                
            wildcard_rows.append({
                "순위": i + 1,
                "결과": prefix,
                "조": f"Group {item['group']}",
                "팀": TEAMS[item["team_code"]]["name"],
                "승점": item["points"],
                "득실차": item["gd"],
                "득점": item["gs"]
            })
            
        st.table(pd.DataFrame(wildcard_rows).set_index("순위"))
        
        # 32강 대진 생성 버튼
        if st.button("🏆 32강 토너먼트 대진 생성하기", type="primary", use_container_width=True):
            # 1, 2위 진출자 취합
            group_winners = []
            group_runners_up = []
            
            for gn in sorted(list(st.session_state.groups.keys())):
                stands = {t: {"points": 0, "gd": 0, "gs": 0} for t in st.session_state.groups[gn]}
                for m in st.session_state.group_matches:
                    if m["group"] == gn and m["played"]:
                        t1, t2 = m["team1"], m["team2"]
                        s1, s2 = m["score1"], m["score2"]
                        if s1 > s2:
                            stands[t1]["points"] += 3
                            stands[t1]["gd"] += (s1 - s2)
                            stands[t2]["gd"] += (s2 - s1)
                            stands[t1]["gs"] += s1
                            stands[t2]["gs"] += s2
                        elif s1 < s2:
                            stands[t2]["points"] += 3
                            stands[t2]["gd"] += (s2 - s1)
                            stands[t1]["gd"] += (s1 - s2)
                            stands[t2]["gs"] += s2
                            stands[t1]["gs"] += s1
                        else:
                            stands[t1]["points"] += 1
                            stands[t2]["points"] += 1
                            stands[t1]["gd"] += (s1 - s2)
                            stands[t2]["gd"] += (s2 - s1)
                            stands[t1]["gs"] += s1
                            stands[t2]["gs"] += s2
                
                sorted_stands = sorted(stands.items(), key=lambda x: (x[1]["points"], x[1]["gd"], x[1]["gs"]), reverse=True)
                group_winners.append(sorted_stands[0][0])
                group_runners_up.append(sorted_stands[1][0])
                
            # 대진 매칭 로직 구성 (32개팀)
            # A1 vs W1, B1 vs W2, C1 vs W3, D1 vs W4, E1 vs W5, F1 vs W6, G1 vs W7, H1 vs W8
            # I1 vs A2, J1 vs B2, K1 vs C2, L1 vs D2
            # E2 vs F2, G2 vs H2, I2 vs J2, K2 vs L2
            bracket_32 = []
            
            # 3위 진출팀 매핑 (최대 8개)
            for i in range(8):
                w_code = advancing_third_codes[i] if i < len(advancing_third_codes) else group_runners_up[11-i]
                bracket_32.append({
                    "team1": group_winners[i],
                    "team2": w_code,
                    "score1": None,
                    "score2": None,
                    "winner": None,
                    "played": False
                })
                
            # 다른 Winners vs Runners-up
            bracket_32.append({"team1": group_winners[8], "team2": group_runners_up[0], "score1": None, "score2": None, "winner": None, "played": False}) # I1 vs A2
            bracket_32.append({"team1": group_winners[9], "team2": group_runners_up[1], "score1": None, "score2": None, "winner": None, "played": False}) # J1 vs B2
            bracket_32.append({"team1": group_winners[10], "team2": group_runners_up[2], "score1": None, "score2": None, "winner": None, "played": False}) # K1 vs C2
            bracket_32.append({"team1": group_winners[11], "team2": group_runners_up[3], "score1": None, "score2": None, "winner": None, "played": False}) # L1 vs D2
            
            # 남은 Runners-up 대진
            bracket_32.append({"team1": group_runners_up[4], "team2": group_runners_up[5], "score1": None, "score2": None, "winner": None, "played": False}) # E2 vs F2
            bracket_32.append({"team1": group_runners_up[6], "team2": group_runners_up[7], "score1": None, "score2": None, "winner": None, "played": False}) # G2 vs H2
            bracket_32.append({"team1": group_runners_up[8], "team2": group_runners_up[9], "score1": None, "score2": None, "winner": None, "played": False}) # I2 vs J2
            bracket_32.append({"team1": group_runners_up[10], "team2": group_runners_up[11], "score1": None, "score2": None, "winner": None, "played": False}) # K2 vs L2
            
            st.session_state.bracket_matches = {
                "32강": bracket_32,
                "16강": [],
                "8강": [],
                "4강": [],
                "결승": []
            }
            st.session_state.current_knockout_round = "32강"
            st.session_state.tournament_step = "knockout"
            st.rerun()

    # 4. 토너먼트 라운드 진행 중 (32강 ~ 결승)
    elif st.session_state.tournament_step == "knockout":
        cur_round = st.session_state.current_knockout_round
        st.markdown(f'<div class="glass-card"><h3>🏆 {cur_round} 토너먼트 진행 중</h3></div>', unsafe_allow_html=True)
        
        # 현재 라운드 매치 리스트
        matches = st.session_state.bracket_matches[cur_round]
        
        # 사용자 팀의 생존 여부 체크
        user_alive = False
        user_match_idx = None
        user_opp_code = None
        
        for idx, m in enumerate(matches):
            if m["team1"] == st.session_state.user_team or m["team2"] == st.session_state.user_team:
                user_alive = True
                if not m["played"]:
                    user_match_idx = idx
                    user_opp_code = m["team2"] if m["team1"] == st.session_state.user_team else m["team1"]
                break
                
        # 활성 매치 수동 플레이 모드 동작 시
        if st.session_state.active_playable_match:
            apm = st.session_state.active_playable_match
            render_active_game_iframe(apm["user_code"], apm["opp_code"], "knockout", apm["match_idx"], cur_round)
            
        else:
            col_b1, col_b2 = st.columns([1, 1])
            
            with col_b1:
                st.subheader(f"📅 {cur_round} 매치 리스트")
                
                # 모든 매치 정보 루프 돌며 그리기
                for idx, m in enumerate(matches):
                    t1_name = CURRENT_TEAMS[m["team1"]]["name"]
                    t2_name = CURRENT_TEAMS[m["team2"]]["name"]
                    
                    is_user_match = m["team1"] == st.session_state.user_team or m["team2"] == st.session_state.user_team
                    card_border = "border: 2px solid #ff4b4b;" if is_user_match else ""
                    
                    if m["played"]:
                        st.markdown(f"""
                            <div class="standing-card" style="{card_border}">
                                <b>Match {idx+1}:</b> {t1_name} <b>{m["score1"]} : {m["score2"]}</b> {t2_name} (완료)
                            </div>
                        """, unsafe_allow_html=True)
                    else:
                        col_m1, col_m2 = st.columns([3, 1])
                        with col_m1:
                            st.markdown(f'<div style="margin-top:8px; font-weight:bold;">Match {idx+1}: {t1_name} vs {t2_name}</div>', unsafe_allow_html=True)
                        with col_m2:
                            if is_user_match:
                                if st.button("🎮 플레이", key=f"play_ko_{idx}", type="primary"):
                                    st.session_state.active_playable_match = {
                                        "user_code": st.session_state.user_team,
                                        "opp_code": user_opp_code,
                                        "match_idx": idx
                                    }
                                    st.rerun()
                            else:
                                if st.button("⚡시뮬", key=f"sim_ko_{idx}"):
                                    s1, s2 = simulate_match_score(m["team1"], m["team2"])
                                    # 무승부인 경우 토너먼트이므로 승부차기 처리
                                    if s1 == s2:
                                        p1, p2 = 0, 0
                                        while p1 == p2:
                                            p1 = sum(1 for _ in range(5) if random.random() < 0.75)
                                            p2 = sum(1 for _ in range(5) if random.random() < 0.75)
                                        s1_str = f"{s1} ({p1})"
                                        s2_str = f"{s2} ({p2})"
                                        winner = m["team1"] if p1 > p2 else m["team2"]
                                    else:
                                        s1_str, s2_str = s1, s2
                                        winner = m["team1"] if s1 > s2 else m["team2"]
                                        
                                    st.session_state.bracket_matches[cur_round][idx]["score1"] = s1_str
                                    st.session_state.bracket_matches[cur_round][idx]["score2"] = s2_str
                                    st.session_state.bracket_matches[cur_round][idx]["played"] = True
                                    st.session_state.bracket_matches[cur_round][idx]["winner"] = winner
                                    st.rerun()

            with col_b2:
                st.subheader("⚙️ 라운드 제어판")
                
                # 라운드 진행도 판정
                unplayed_count = sum(1 for m in matches if not m["played"])
                st.write(f"미진행 경기 수: {unplayed_count}개")
                
                # 타경기 일괄 시뮬레이션 버튼
                if unplayed_count > 0:
                    if st.button("⚡ 남은 모든 매치 시뮬레이션", use_container_width=True):
                        for idx, m in enumerate(matches):
                            if not m["played"]:
                                if m["team1"] == st.session_state.user_team or m["team2"] == st.session_state.user_team:
                                    # 사용자 팀은 시뮬레이션 불가 (직접 플레이 해야 함)
                                    continue
                                else:
                                    s1, s2 = simulate_match_score(m["team1"], m["team2"])
                                    if s1 == s2:
                                        p1, p2 = 0, 0
                                        while p1 == p2:
                                            p1 = sum(1 for _ in range(5) if random.random() < 0.75)
                                            p2 = sum(1 for _ in range(5) if random.random() < 0.75)
                                        s1_str = f"{s1} ({p1})"
                                        s2_str = f"{s2} ({p2})"
                                        winner = m["team1"] if p1 > p2 else m["team2"]
                                    else:
                                        s1_str, s2_str = s1, s2
                                        winner = m["team1"] if s1 > s2 else m["team2"]
                                    
                                    st.session_state.bracket_matches[cur_round][idx]["score1"] = s1_str
                                    st.session_state.bracket_matches[cur_round][idx]["score2"] = s2_str
                                    st.session_state.bracket_matches[cur_round][idx]["played"] = True
                                    st.session_state.bracket_matches[cur_round][idx]["winner"] = winner
                        st.success("남은 다른 매치들의 시뮬레이션이 모두 끝났습니다.")
                        st.rerun()
                
                # 다음 라운드 진출 버튼 활성화 조건
                if unplayed_count == 0:
                    # 결승전 종료 시
                    if cur_round == "결승":
                        closing_label = "🏆 결승 결과 발표 및 월드컵 폐막" if st.session_state.tournament_mode == "worldcup" else "🏆 결승 결과 발표 및 대회 종료"
                        if st.button(closing_label, type="primary", use_container_width=True):
                            st.session_state.tournament_step = "completed"
                            st.rerun()
                    else:
                        # 32강 -> 16강 -> 8강 -> 4강 -> 결승
                        round_order = ["32강", "16강", "8강", "4강", "결승"]
                        next_round = round_order[round_order.index(cur_round) + 1]
                        
                        if st.button(f"⏩ {next_round} 대진 생성 및 진행", type="primary", use_container_width=True):
                            # 이전 라운드 승자들 모으기
                            winners = [m["winner"] for m in matches]
                            
                            # 다음 라운드 매치 구성
                            next_matches = []
                            for i in range(0, len(winners), 2):
                                next_matches.append({
                                    "team1": winners[i],
                                    "team2": winners[i+1],
                                    "score1": None,
                                    "score2": None,
                                    "winner": None,
                                    "played": False
                                })
                            st.session_state.bracket_matches[next_round] = next_matches
                            st.session_state.current_knockout_round = next_round
                            st.rerun()

                # 사용자 생존 여부 메시지
                team_suffix = "대표팀" if st.session_state.tournament_mode == "worldcup" else "클럽팀"
                other_suffix = "다른 국가들의" if st.session_state.tournament_mode == "worldcup" else "다른 클럽들의"
                if user_alive:
                    st.info(f"👍 {CURRENT_TEAMS[st.session_state.user_team]['name']} {team_suffix}이 아직 토너먼트에 생존해 있습니다!")
                else:
                    st.warning(f"❌ {CURRENT_TEAMS[st.session_state.user_team]['name']} {team_suffix}은 아쉽게도 탈락했습니다. {other_suffix} 토너먼트 시뮬레이션을 끝까지 확인하세요!")

    # 5. 토너먼트 종료
    elif st.session_state.tournament_step == "completed":
        mode_title = "월드컵" if st.session_state.tournament_mode == "worldcup" else "챔피언스 리그"
        st.markdown(f'<div class="glass-card" style="text-align:center;"><h2>🏆 {mode_title} 최종 우승팀 탄생 🏆</h2></div>', unsafe_allow_html=True)
        
        final_match = st.session_state.bracket_matches["결승"][0]
        champion_code = final_match["winner"]
        champion_name = CURRENT_TEAMS[champion_code]["name"]
        
        champion_prefix = "2026 FIFA World Cup" if st.session_state.tournament_mode == "worldcup" else "UEFA Champions League"
        
        # 화려한 챔피언 배너 및 모달 효과 연출용 카드
        st.markdown(f"""
            <div style="text-align: center; margin-top: 1.5rem;">
                <h1 style="color: #FFD700; font-size: 3.5rem; font-weight: 800; text-shadow: 0 0 20px rgba(255,215,0,0.5);">{champion_name}</h1>
                <p style="font-size: 1.4rem; color: #94A3B8; font-weight: 500;">{champion_prefix} 우승을 축하합니다!</p>
            </div>
        """, unsafe_allow_html=True)

        # 실제 우승 트로피 이미지 연출
        trophy_filename = "worldcup_trophy.png" if st.session_state.tournament_mode == "worldcup" else "ucl_trophy.png"
        trophy_path = os.path.join("assets", trophy_filename)
        if os.path.exists(trophy_path):
            col_left, col_mid, col_right = st.columns([1.2, 1, 1.2])
            with col_mid:
                st.image(trophy_path, use_container_width=True, caption=f"{champion_name} 우승 기념 트로피")
        
        # 다시 시작 버튼
        btn_label = "🔄 새로운 월드컵 시뮬레이션 시작" if st.session_state.tournament_mode == "worldcup" else "🔄 새로운 챔피언스 리그 시뮬레이션 시작"
        if st.button(btn_label, type="primary", use_container_width=True):
            st.session_state.tournament_step = "not_started"
            st.session_state.user_team = None
            st.session_state.groups = {}
            st.session_state.group_matches = []
            st.session_state.bracket_matches = {}
            st.session_state.current_knockout_round = "32강" if st.session_state.tournament_mode == "worldcup" else "16강"
            st.session_state.active_playable_match = None
            st.session_state.penalty_shootout = None
            st.rerun()


