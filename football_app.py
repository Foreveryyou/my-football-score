import streamlit as st
import pandas as pd
from datetime import datetime

# 1. 페이지 설정
st.set_page_config(page_title="Football Scorer Pro", layout="centered", page_icon="🏈")

# 2. 데이터 저장소 및 단계 관리
if 'game_log' not in st.session_state:
    st.session_state.game_log = []
if 'step' not in st.session_state:
    st.session_state.step = 1
if 'current_play' not in st.session_state:
    st.session_state.current_play = {}

# --- [STEP 1: 경기 상황 입력] ---
if st.session_state.step == 1:
    st.header("1단계: 경기 상황")
    with st.form("step1"):
        c1, c2 = st.columns(2)
        with c1:
            qtr = st.selectbox("Quarter", ['1', '2', '3', '4', 'OT'])
            team = st.radio("공격팀", ['Home', 'Away'], horizontal=True)
        with c2:
            # 다운은 1~4까지 선택, 야드는 타이핑
            down = st.selectbox("Down", ['1st', '2nd', '3rd', '4th'])
            dist = st.text_input("Distance (야드)", value="10")
            ball_on = st.number_input("Ball On (야드라인)", value=25)
        
        if st.form_submit_button("전술 입력 단계로 ➡️"):
            st.session_state.current_play.update({
                'QTR': qtr, 'Team': team, 'DownDist': f"{down} & {dist}", 'BallOn': ball_on
            })
            st.session_state.step = 2
            st.rerun()

# --- [STEP 2: 전술 입력] ---
elif st.session_state.step == 2:
    st.header("2단계: 전술 입력")
    st.info(f"📍 {st.session_state.current_play['Team']} 공격 | {st.session_state.current_play['DownDist']}")
    
    with st.form("step2"):
        off_fm = st.text_input("OFF FM (포메이션)")
        off_play = st.text_input("OFF PLAY (작전명)")
        def_fm_play = st.text_input("DEF FM-PLAY (수비 작전)")
        
        c1, c2 = st.columns(2)
        with c1:
            if st.form_submit_button("⬅️ 이전 (상황)"):
                st.session_state.step = 1
                st.rerun()
        with c2:
            if st.form_submit_button("결과 입력 단계로 ➡️"):
                st.session_state.current_play.update({
                    'OffFM': off_fm, 'OffPlay': off_play, 'DefStrategy': def_fm_play
                })
                st.session_state.step = 3
                st.rerun()

# --- [STEP 3: 결과 입력] ---
elif st.session_state.step == 3:
    st.header("3단계: 플레이 결과")
    st.success(f"🏈 작전: {st.session_state.current_play['OffPlay']}")
    
    with st.form("step3"):
        c1, c2 = st.columns(2)
        with c1:
            play_type = st.selectbox("플레이 종류", ['RUS', 'PAS', 'PUN', 'FG', 'PAT'])
            qb = st.text_input("QB / KICKER (번호)")
            bc = st.text_input("B/C (러너/리시버 번호)")
        with c2:
            gain = st.number_input("전진 야드 (Gain)", value=0)
            tackle = st.text_input("Tackle By (수비수 번호)")
            score = st.number_input("득점 (Score)", value=0)
        
        st.divider()
        r1, r2, r3, r4 = st.columns(4)
        with r1: is_fd = st.checkbox("FD")
        with r2: is_int = st.checkbox("INT")
        with r3: is_fum = st.checkbox("FUM")
        with r4: rec_by = st.text_input("확보자")
        
        other = st.text_input("기타 (Penalty 등)")
        
        c_btn1, c_btn2 = st.columns(2)
        with c_btn1:
            if st.form_submit_button("⬅️ 이전 (전술)"):
                st.session_state.step = 2
                st.rerun()
        with c_btn2:
            if st.form_submit_button("📥 최종 저장 및 기록"):
                full_data = {**st.session_state.current_play, **{
                    'No': len(st.session_state.game_log) + 1,
                    'QB': qb, 'Type': play_type, 'BC': bc, 'Gain': gain,
                    'Tackle': tackle, 'Score': score,
                    'FD': 'O' if is_fd else '', 'INT': 'O' if is_int else '', 'FUM': 'O' if is_fum else '',
                    'RecBy': rec_by, 'Remarks': other, 'Time': datetime.now().strftime("%H:%M:%S")
                }}
                st.session_state.game_log.append(full_data)
                st.session_state.step = 1
                st.session_state.current_play = {}
                st.toast("플레이가 기록되었습니다!")
                st.rerun()

# --- [통계 섹션: 개인 기록 실시간 집계] ---
st.divider()
if st.session_state.game_log:
    df = pd.DataFrame(st.session_state.game_log)
    
    st.header("📊 팀별 개인 기록지")
    
    t_home, t_away = st.tabs(["🏠 HOME TEAM", "🚗 AWAY TEAM"])
    
    def render_player_stats(target_team):
        # 해당 팀이 공격일 때의 데이터 (Rushing, Passing, Receiving)
        off_df = df[df['Team'] == target_team]
        # 상대 팀이 공격일 때 우리 팀의 수비 데이터 (Tackle, INT/FUM Recovery)
        def_df = df[df['Team'] != target_team]
        
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("■ RUSHING")
            rush = off_df[off_df['Type'] == 'RUS'].groupby('BC').agg(Play=('No','count'), Gain=('Gain','sum')).reset_index()
            if not rush.empty: rush['Avg'] = (rush['Gain'] / rush['Play']).round(1)
            st.dataframe(rush, use_container_width=True, hide_index=True)

            st.subheader("■ RECEIVING")
            recv = off_df[off_df['Type'] == 'PAS'].groupby('BC').agg(Rec=('No','count'), Gain=('Gain','sum')).reset_index()
            if not recv.empty: recv['Avg'] = (recv['Gain'] / recv['Rec']).round(1)
            st.dataframe(recv, use_container_width=True, hide_index=True)

        with col2:
            st.subheader("■ PASSING (QB)")
            passing = off_df[off_df['Type'] == 'PAS'].groupby('QB').agg(Att=('No','count'), Yds=('Gain','sum'), INT=('INT', lambda x: (x=='O').sum())).reset_index()
            st.dataframe(passing, use_container_width=True, hide_index=True)

            st.subheader("■ DEFENSE (Tackle/Turnover)")
            tackles = def_df[def_df['Tackle'] != ""].groupby('Tackle').size().reset_index(name='Tackles')
            turns = def_df[def_df['RecBy'] != ""].groupby('RecBy').size().reset_index(name='Recoveries')
            st.dataframe(tackles, use_container_width=True, hide_index=True)
            st.dataframe(turns, use_container_width=True, hide_index=True)

    with t_home: render_player_stats("Home")
    with t_away: render_player_stats("Away")

    # 엑셀 다운로드 버튼
    csv = df.to_csv(index=False).encode('utf-8-sig')
    st.download_button("📊 전체 경기 기록지(엑셀) 받기", csv, f"game_{datetime.now().strftime('%m%d_%H%M')}.csv", use_container_width=True)
    st.subheader("📜 전체 플레이 로그")
    st.dataframe(df.iloc[::-1], use_container_width=True)