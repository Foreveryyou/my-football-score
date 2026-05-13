import streamlit as st
import pandas as pd
from datetime import datetime

# 1. 페이지 설정
st.set_page_config(page_title="Football Scorer - Dual Stats", layout="wide", page_icon="🏈")

st.title("🏈 Football Scorer (Independent Team Stats)")

# 2. 데이터 저장소
if 'game_log' not in st.session_state:
    st.session_state.game_log = []

# --- [상단] 입력 UI ---
c1, c2, c3, c4 = st.columns([1, 2, 1, 1])
with c1:
    qtr = st.selectbox("Quarter", ['1', '2', '3', '4', 'OT'])
with c2:
    team = st.radio("CURRENT OFFENSE TEAM", ['Home', 'Away'], horizontal=True)
with c3:
    ball_on = st.number_input("BALL-ON", value=25)
with c4:
    down_dist = st.text_input("DOWN-DIST", value="1-10")

st.divider()

col_left, col_right = st.columns(2)
with col_left:
    st.subheader("📋 Strategy")
    off_fm = st.text_input("OFF FM")
    off_play = st.text_input("OFF PLAY")
    def_fm_play = st.text_input("DEF FM-PLAY")

with col_right:
    st.subheader("🏃 Play Result")
    sub_c1, sub_c2 = st.columns(2)
    with sub_c1:
        qb = st.text_input("QB / KICKER", placeholder="번호")
        play_type = st.selectbox("TYPE", ['RUS', 'PAS', 'PUN', 'FG', 'PAT'])
    with sub_c2:
        bc = st.text_input("B/C (Runner/Receiver)", placeholder="번호")
        gain = st.number_input("GAIN YARDS", value=0)
    tackle = st.text_input("Tackle By (수비팀)", placeholder="번호")
    score = st.number_input("SCORE", value=0)

t1, t2, t3, t4 = st.columns([1, 1, 1, 2])
with t1: is_fd = st.checkbox("FD")
with t2: is_int = st.checkbox("INT")
with t3: is_fum = st.checkbox("FUM")
with t4: rec_by = st.text_input("REC BY (확보자)")
other = st.text_input("Other Remarks")

if st.button("📥 RECORD PLAY", type="primary", use_container_width=True):
    play_num = len(st.session_state.game_log) + 1
    new_play = {
        'No': play_num, 'QTR': qtr, 'Team': team, 'BallOn': ball_on, 'DownDist': down_dist,
        'OffFM': off_fm, 'OffPlay': off_play, 'DefStrategy': def_fm_play,
        'QB': qb, 'Type': play_type, 'BC': bc, 'Gain': gain, 'Tackle': tackle, 'Score': score,
        'FD': 'O' if is_fd else '', 'INT': 'O' if is_int else '', 'FUM': 'O' if is_fum else '',
        'RecBy': rec_by, 'Remarks': other, 'Time': datetime.now().strftime("%H:%M:%S")
    }
    st.session_state.game_log.append(new_play)
    st.toast(f"Play #{play_num} 저장 완료!")

# --- [중단] 팀별 개인 통계 (Home / Away 각각 출력) ---
st.divider()

def get_stats(data, target_team):
    # 공격 데이터 (해당 팀) / 수비 데이터 (상대 팀이 공격할 때 우리 팀이 한 것)
    off_data = data[data['Team'] == target_team]
    def_data = data[data['Team'] != target_team]
    
    # Rushing
    rush = off_data[off_data['Type'] == 'RUS'].groupby('BC').agg(Att=('No','count'), Yds=('Gain','sum'), Avg=('Gain','mean')).reset_index()
    # Passing
    pass_qb = off_data[off_data['Type'] == 'PAS'].groupby('QB').agg(Att=('No','count'), Yds=('Gain','sum'), INT=('INT', lambda x: (x=='O').sum())).reset_index()
    # Receiving
    recv = off_data[off_data['Type'] == 'PAS'].groupby('BC').agg(Rec=('No','count'), Yds=('Gain','sum'), Avg=('Gain','mean')).reset_index()
    # Defense
    def_stats = def_data[def_data['Tackle'] != ""].groupby('Tackle').size().reset_index(name='Tackles')
    
    return rush, pass_qb, recv, def_stats

if st.session_state.game_log:
    df_main = pd.DataFrame(st.session_state.game_log)
    
    # 화면을 반으로 나누어 왼쪽은 Home, 오른쪽은 Away 통계 고정 출력
    col_home, col_away = st.columns(2)
    
    with col_home:
        st.header("🏠 HOME STATS")
        h_rush, h_pass, h_recv, h_def = get_stats(df_main, "Home")
        st.subheader("Rushing")
        st.dataframe(h_rush, use_container_width=True, hide_index=True)
        st.subheader("Passing / Receiving")
        st.dataframe(h_pass, use_container_width=True, hide_index=True)
        st.dataframe(h_recv, use_container_width=True, hide_index=True)
        st.subheader("Defense")
        st.dataframe(h_def, use_container_width=True, hide_index=True)

    with col_away:
        st.header("🚗 AWAY STATS")
        a_rush, a_pass, a_recv, a_def = get_stats(df_main, "Away")
        st.subheader("Rushing")
        st.dataframe(a_rush, use_container_width=True, hide_index=True)
        st.subheader("Passing / Receiving")
        st.dataframe(a_pass, use_container_width=True, hide_index=True)
        st.dataframe(a_recv, use_container_width=True, hide_index=True)
        st.subheader("Defense")
        st.dataframe(a_def, use_container_width=True, hide_index=True)

# --- [하단] 전체 로그 및 내보내기 ---
st.divider()
if st.session_state.game_log:
    c_down1, c_down2 = st.columns([4, 1])
    with c_down2:
        csv_data = pd.DataFrame(st.session_state.game_log).to_csv(index=False).encode('utf-8-sig')
        st.download_button("📊 EXCEL DOWNLOAD", csv_data, "game_record.csv", use_container_width=True)
    st.subheader("📜 Full Play Log")
    st.dataframe(pd.DataFrame(st.session_state.game_log).iloc[::-1], use_container_width=True)
