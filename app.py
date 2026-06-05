import streamlit as st
from supabase import create_client
import pandas as pd
import altair as alt

# --- [주차별 데이터 관리] ---
@st.cache_data
def get_all_lecture_data():
    return {
        # (이전 주차 데이터들은 교수님 기존 코드 그대로 유지하시면 됩니다)
        
        11: [ 
            {"type": "balance", "id": 1101, "q": "현재 하락 중인 두 종목 중, 내가 더 끝까지 매도하지 못하고 버틸 것 같은 종목은?", 
             "opt": ["A: 사업 모델이 명확하고 내가 적정 가치를 계산할 수 있는 종목", "B: 장밋빛 미래가 기대되지만 구체적인 가치 산정은 어려운 복잡한 기술주"],
             "bias_ans": "B", "weight": 10},
            
            {"type": "balance", "id": 1102, "q": "주가가 20% 폭락했을 때, 심리적으로 손절매(Stop-loss)가 더 힘든 상황은?", 
             "opt": ["A: 내가 직접 재무제표를 분석하고 확신하여 매수한 종목이 하락했을 때", "B: 유명 전문가의 추천을 믿고 그대로 따라서 매수한 종목이 하락했을 때"],
             "bias_ans": "A", "weight": 20},
            
            {"type": "balance", "id": 1103, "q": "둘 중 더 오랫동안 나를 괴롭힐 것 같은 후회는?", 
             "opt": ["A: 친구가 번호를 바꾸자고 제안했지만 거절했는데, 그 번호가 1등이 된 경우 (부작위 후회)", "B: 친구 제안으로 원래 내 번호를 바꿨는데, 원래 번호가 1등이 된 경우 (작위 후회)"],
             "bias_ans": "B", "weight": 25},
            
            {"type": "balance", "id": 1104, "q": "50달러에 산 주식이 100달러를 찍고 현재 75달러라면, 나는 지금 어떤 상태인가?", 
             "opt": ["A: 매수가(50달러) 대비 아직도 25달러나 벌었으니 행복한 이익 상태다.", "B: 전고점(100달러) 대비 내 자산이 25달러나 날아갔으니 불행한 손실 상태다."],
             "bias_ans": "B", "weight": 30},
            
            {"type": "balance", "id": 1105, "q": "과거 매매 경험이 있는 두 종목 중, 현재 내가 더 매수하고 싶은 종목은?", 
             "opt": ["A: 예전에 투자해서 큰 수익을 안겨주어 좋은 기억이 남아있는 종목", "B: 예전에 투자했다가 뼈아픈 손실을 보고 큰 후회를 남겼던 종목"],
             "bias_ans": "A", "weight": 15}
        ],
        12: [
            # 1. 밸런스 게임: 기억의 채색 - 완만한 하락 vs 순간적 폭락 (강의안 22-23p)
            # [수업 팁] 연말 종가 기준으로는 A의 실적이 더 나쁩니다. 하지만 감정적 고통은 급락을 겪은 B가 훨씬 큽니다.
            # 이 부정확한 기억이 추후 제약주에 대한 그릇된 의사결정(기회 회피)을 유발함을 설명.
            {   "type": "balance", "id": 1201, 
                "q": "투자 후 연말이 되었을 때, 나에게 더 '치명적인 고통의 기억'으로 남을 종목은?", 
                "opt": ["A: 연중 내내 서서히 흘러내려 결국 -25% 손실로 마감한 바이오주", 
                        "B: 평온하다가 연말에 대형 악재가 터져 며칠 만에 -20%로 급락한 제약주"]
            },
            # 2. 밸런스 게임: 인지부조화와 방어기제 - 기억의 편집 (강의안 24-25p)
            # [수업 팁] 대다수의 개인투자자는 인지부조화의 고통을 피하기 위해 나쁜 뉴스를 무시하고 기억을 미화합니다.
            # 이로 인해 자신의 실수로부터 배우지 못하고 똑같은 실패를 반복함을 경고.
            {   "type": "balance", "id": 1202, 
                "q": "최근 1년간 주식 투자 성과에 대한 나의 기억 방식은?", 
                "opt": ["A: 수익이 난 대박 종목과 손실이 난 쪽박 종목의 액수를 정확하게 가감하여 기억한다.", 
                        "B: 손실을 본 기억은 애써 지우거나 축소하고, 이익을 크게 본 종목 중심으로 기억한다."]
            },
            # 3. 밸런스 게임: 책임의 유무와 고통의 크기 - 직접투자 vs 펀드 (강의안 27p)
            # [수업 팁] Chang et al.(2016) 연구 연계. 직접 투자는 실수를 무시하기 어려워 '처분효과(버티기)'로 가지만,
            # 펀드 투자는 매니저라는 '희생양'이 있어 책임을 미룰 수 있으므로 오히려 매도가 쉬워짐(역처분효과)을 강의.
            {   "type": "balance", "id": 1203, 
                "q": "보유 자산이 반토막 났을 때, 내가 '의사결정의 실수'를 인정하기 더 괴로운 상황은?", 
                "opt": ["A: 내가 매수 이유를 완벽하게 기록해가며 직접 종목을 고른 주식이 폭락했을 때", 
                        "B: 자산운용사의 간판 펀드매니저가 운영하는 펀드 상품에 가입했는데 폭락했을 때"]
            }
        ],
        13: [
            # 13주차 문제(예: "id": 1301부터 시작)
        ]
    }

# 전체 데이터 로드
all_lecture_data = get_all_lecture_data()

# 수파베이스 연결
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

st.set_page_config(page_title="행동재무학", layout="wide")

# 세션 스테이트 초기화 (학번 삭제, 이름만 사용)
if "std_name" not in st.session_state:
    st.session_state.std_name = st.query_params.get("name", "")

# 사이드바 설정
with st.sidebar:
    mode = st.radio("모드 선택", ["학생 참여", "교수 관리"])
    if mode == "교수 관리":
        pw = st.text_input("교수 비밀번호", type="password")
        if pw == "3383":
            st.success("관리자 모드 활성화")
            sel_class = st.selectbox("수업 선택", ["인하대", "숙대 1", "숙대 2"])
            sel_week = st.number_input("진행 주차", min_value=1, max_value=15, value=11)
            
            current_week_data = all_lecture_data.get(sel_week, [])
            
            if not current_week_data:
                st.warning(f"⚠️ {sel_week}주차 데이터가 등록되지 않았습니다.")
            else:
                active_data = supabase.table("par_beh_fin_active_session").select("*").eq("id", 1).execute()
                stored_idx = active_data.data[0]['current_item_idx'] if active_data.data else 0
                
                if len(current_week_data) > 1:
                    new_idx = st.select_slider(
                        "문제 진행 상황", 
                        options=range(len(current_week_data)), 
                        value=min(stored_idx, len(current_week_data)-1),
                        format_func=lambda x: f"{x+1}번 문제"
                    )
                else:
                    st.info("문제가 1개 등록되어 있습니다.")
                    new_idx = 0
                
                if st.button("📢 이 설정으로 수업 시작"):
                    supabase.table("par_beh_fin_active_session").upsert({
                        "id": 1, "class_name": sel_class, "week_no": sel_week, "current_item_idx": new_idx
                    }).execute()
                    st.success(f"{sel_week}주차 {new_idx+1}번 문제로 세팅되었습니다.")
                    st.rerun()

# --- 학생 참여 화면 ---
if mode == "학생 참여":
    if not st.session_state.std_name:
        st.header("👋 반갑습니다! 정보를 입력해주세요.")
        in_name = st.text_input("이름")
        
        if st.button("수업 참여하기"):
            if in_name:
                st.session_state.std_name = in_name
                st.rerun()
    else:
        active = supabase.table("par_beh_fin_active_session").select("*").eq("id", 1).execute()
        if active.data:
            curr_class = active.data[0]['class_name']
            curr_week = active.data[0]['week_no']
            curr_idx = active.data[0]['current_item_idx']
            
            week_data = all_lecture_data.get(curr_week, [])
            
            if not week_data:
                st.error(f"{curr_week}주차 강의 데이터가 준비되지 않았습니다.")
            else:
                item = week_data[curr_idx]
                st.info(f"🎓 {st.session_state.std_name}님 | {curr_class} {curr_week}주차 진행 중")
                
                # 중복 제출 확인 (학번 대신 이름으로 확인)
                check = supabase.table("par_beh_fin_responses").select("*")\
                    .eq("std_name", st.session_state.std_name)\
                    .eq("class_name", curr_class)\
                    .eq("week_no", curr_week)\
                    .eq("item_id", item['id']).execute()

                st.divider()
                
                if len(check.data) > 0:
                    st.success(f"✅ 제출 완료: {item.get('q', item.get('title'))}")
                    if st.button("🔄 다음 문제 확인 (교수님이 안내하면 누르세요)"):
                        st.rerun()
                else:
                    with st.form(f"live_form_{curr_week}_{curr_idx}"):
                        st.markdown(f"### Q. {item.get('q', item.get('title'))}")
                        
                        if item['type'] == "balance":
                            ans = st.radio("선택해주세요", item['opt'])
                            if st.form_submit_button("참여하기"):
                                supabase.table("par_beh_fin_responses").insert({
                                    "class_name": curr_class, "week_no": curr_week, 
                                    "std_name": st.session_state.std_name, 
                                    "item_id": item['id'], "item_type": "balance", 
                                    "response": ans, "score": 1.0
                                }).execute()
                                st.rerun()
                        # (필요시 quiz 등 기존 로직 추가)
        else:
            st.warning("교수님의 시작 버튼을 기다려주세요.")

# --- 교수용 결과 모니터링 ---
if mode == "교수 관리" and pw == "3383":
    st.divider()
    st.subheader(f"📊 {sel_class} {sel_week}주차 실시간 통계")
    res = supabase.table("par_beh_fin_responses").select("*").eq("class_name", sel_class).eq("week_no", sel_week).limit(5000).execute()
    df = pd.DataFrame(res.data)
    
    if not df.empty:
        current_week_data = all_lecture_data.get(sel_week, [])
        if current_week_data:
            active_session = supabase.table("par_beh_fin_active_session").select("*").eq("id", 1).execute()
            curr_idx = active_session.data[0]['current_item_idx'] if active_session.data else 0
            curr_item_id = current_week_data[curr_idx]['id']
            curr_df = df[df['item_id'] == curr_item_id]
         
            if not curr_df.empty:
                chart_data = curr_df['response'].value_counts().reset_index()
                chart_data.columns = ['응답내용', '인원수']
                chart = alt.Chart(chart_data).mark_bar(color='#E63946', size=50).encode(
                    x=alt.X('응답내용:N', title='응답 선택지'),
                    y=alt.Y('인원수:Q', title='인원수(명)')
                ).properties(height=400)
                st.altair_chart(chart, use_container_width=True)
            
            with st.expander("🎓 학생별 이번 주 참여 점수 및 유형 확인", expanded=True):
                if sel_week == 11:
                    # 11주차: 처분효과 위험 지수 계산 및 유형 판별 로직
                    scores = []
                    for std, group in df.groupby('std_name'):
                        score = 0
                        for _, row in group.iterrows():
                            q = next((q for q in current_week_data if q['id'] == row['item_id']), None)
                            if q and 'bias_ans' in q and row['response'].startswith(q['bias_ans']):
                                score += q['weight']
                        
                        # 점수 기준에 따른 유형 텍스트 할당 (조언 부분 삭제)
                        if score <= 30:
                            p_type = "냉철한 전략가형"
                        elif score <= 60:
                            p_type = "전형적인 개인투자자형"
                        elif score <= 85:
                            p_type = "본능 충실형"
                        else:
                            p_type = "처분효과 고위험군"
                            
                        scores.append({
                            '학생 이름': std, 
                            '위험 지수': int(score),
                            '투자자 유형': p_type
                        })
                    
                    score_df = pd.DataFrame(scores)
                    if not score_df.empty:
                        avg_score = score_df['위험 지수'].mean()
                        st.metric(f"📈 11주차 반 평균 처분효과 위험 지수", f"{avg_score:.1f}점")
                        
                        # 조언 항목이 제외된 데이터프레임 출력
                        st.dataframe(score_df.sort_values(by='위험 지수', ascending=False), use_container_width=True)
                else:
                    # 다른 주차의 일반 참여 점수 집계
                    summary = df.groupby(['std_name'])['score'].sum().reset_index()
                    summary.columns = ['학생 이름', '참여 점수']
                    st.dataframe(summary.sort_values(by='참여 점수', ascending=False), use_container_width=True)
