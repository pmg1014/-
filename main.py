import streamlit as st
import datetime
from collections import defaultdict

st.title('📚 시험 공부 계획 자동 생성기')

name = st.text_input('이름을 입력해주세요:')
subject_count = st.number_input('시험 과목 수를 입력하세요:', min_value=1, max_value=10, value=3)

subjects = {}

st.subheader('📌 과목별 정보 입력')

# 과목별 입력 받기
for i in range(subject_count):
    st.markdown(f"### 과목 {i + 1}")
    subject = st.text_input(f'과목명 {i + 1}', key=f'subject_{i}')
    test_date = st.date_input(f'{subject} 시험일', key=f'date_{i}')
    study_amount = st.slider(f'{subject} 공부량 (1~10)', 1, 10, 5, key=f'amount_{i}')
    importance = st.slider(f'{subject} 중요도 (1~5)', 1, 5, 3, key=f'importance_{i}')
    
    if subject:  # 과목명이 비어있지 않다면
        subjects[subject] = {
            '시험일': test_date,
            '공부량': study_amount,
            '중요도': importance
        }

if st.button('📅 공부 계획 세우기'):
    if not subjects:
        st.warning('최소 1개 이상의 과목 정보를 입력해야 해요.')
    else:
        today = datetime.date.today()
        study_plan = defaultdict(list)

        for subject, info in subjects.items():
            test_date = info['시험일']
            days_left = (test_date - today).days

            if days_left <= 0:
                st.error(f"❗ '{subject}' 시험일이 지났거나 오늘입니다. 계획에서 제외합니다.")
                continue

            total_effort = info['공부량'] * info['중요도']
            daily_effort = total_effort / days_left

            for i in range(days_left):
                study_date = today + datetime.timedelta(days=i)
                study_plan[study_date].append((subject, round(daily_effort, 1)))

        st.success(f'✅ {name}님의 공부 계획표가 생성되었습니다!')

        for date in sorted(study_plan.keys()):
            st.markdown(f"### 📅 {date.strftime('%Y-%m-%d')}")
            for subject, effort in study_plan[date]:
                st.write(f"  - {subject}: {effort} 단위 공부")

