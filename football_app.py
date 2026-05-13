import streamlit as st
import pandas as pd
from datetime import datetime

# 1. 페이지 설정
st.set_page_config(page_title="Football Scorer", layout="wide", page_icon="🏈")

st.title("🏈 Football Strategic Live Scorer")

# 2. 데이터 저장소 (세션 유지)
if 'game_log' not in st.session_state:
    st.session_state.game_log = []

# --- 메인 UI 입력창 ---
c1, c2, c3, c4 = st.columns([1, 2, 1, 1])
with c1:
    qtr = st.selectbox("Quarter", ['1', '2', '3', '4', 'OT'])
with c2:
    team = st.radio("공격팀", ['Home', 'Away'], horizontal=True)
with c3:
    ball_on = st.number_input("BALL-ON", value=25)
with c4:
    down_dist = st.text_input("DOWN-DIST", value="1-10")

st.subheader("📋 Strategy & Formation")
s1, s2 = st.columns(2)
with s1:
    off_fm = st.text_input("OFF FM", placeholder="예: ACE, PRO")
    off_play = st.text_input("OFF PLAY", placeholder="공격 작전명")
with s2:
    def_fm_play = st.text_input("DEF FM-PLAY", placeholder="수비 작전명")

st.subheader("🏃 Play Result")
r1, r2, r3 = st.columns(3)
with r1:
    qb = st.text_input("QB / KICKER")
    play_type = st.selectbox("TYPE", ['RUS', 'PAS', 'PUN', 'FG', 'PAT'])
with r2:
    bc = st.text_input("B/C")
    gain = st.slider("GAIN YARDS", -50, 99, 0)
with r3:
    tackle = st.text_input("Tackle By")
    score = st.number_input("SCORE", value=0)

st.subheader("🚩 Remarks & Turnovers")
t1, t2, t3, t4 = st.columns([1, 1, 1, 2])
with t1: is_fd = st.checkbox("FD")
with t2: is_int = st.checkbox("INT")
with t3: is_fum = st.checkbox("FUM")
with t4: rec_by = st.text_input("REC BY")

other = st.text_input("기타 (Penalty 등)")

st.divider()

# --- 버튼 배치 (중요!) ---
# 기록 버튼과 다운로드 버튼을 나란히 배치합니다.
btn_col1, btn_col2 = st.columns(2)

with btn_col1:
    if st.button("📥 RECORD PLAY (저장)", type="primary", use_container_width=True):
        play_num = len(st.session_state.game_log) + 1
        new_play = {
            'No': play_num, 'QTR': qtr, 'Team': team, 'BallOn': ball_on, 'DownDist': down_dist,
            'OffFM': off_fm, 'OffPlay': off_play, 'DefStrategy': def_fm_play,
            'QB': qb, 'Type': play_type, 'BC': bc, 'Gain': gain, 'Tackle': tackle, 'Score': score,
            'FD': 'O' if is_fd else '', 'INT': 'O' if is_int else '', 'FUM': 'O' if is_fum else '',
            'RecBy': rec_by, 'Remarks': other, 'Time': datetime.now().strftime("%H:%M:%S")
        }
        st.session_state.game_log.append(new_play)
        st.toast(f"Play #{play_num} 저장되었습니다!")

with btn_col2:
    # 데이터가 있을 때만 다운로드 버튼이 활성화됩니다.
    if st.session_state.game_log:
        df_all = pd.DataFrame(st.session_state.game_log)
        csv = df_all.to_csv(index=False).encode('utf-8-sig') # 한글 깨짐 방지 utf-8-sig
        st.download_button(
            label="📊 EXPORT TO EXCEL (다운로드)",
            data=csv,
            file_name=f"game_record_{datetime.now().strftime('%m%d_%H%M')}.csv",
            mime="text/csv",
            use_container_width=True
        )
    else:
        st.button("📊 EXPORT (기록 후 활성화)", disabled=True, use_container_width=True)

# --- 데이터 표 표시 ---
st.divider()
if st.session_state.game_log:
    st.subheader("📊 최근 기록 목록")
    st.dataframe(pd.DataFrame(st.session_state.game_log).iloc[::-1], use_container_width=True)
