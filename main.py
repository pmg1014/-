import streamlit as st
import datetime
from collections import defaultdict

st.title('🧠 시간대 기반 시험 공부 시간표')

name = st.text_input('이름을 입력해주세요:')
subject_count = st.number_input('시험 과목 수를 입력하세요:', min_value=1, max_value=10, value=3)
daily_hours = st.slider('하루 공부 시간 (시간 단위)', 1, 10, 4)

subjects = {}
st.subheader('📌 과목별 정보 입력')

# 과목 입력 받기
for i in range(subject_count):
    st.markdown(f"### 과목 {i + 1}")
    subject = st.text_input(f'과목명 {i + 1}', key=f'subject_{i}')
    test_date = st.date_input(f'{subject} 시험일', key=f'date_{i}')
    study_amount = st.slider(f'{subject} 공부량 (1~10)', 1, 10, 5, key=f'amount_{i}')
    importance = st.slider(f'{subject} 중요도 (1~5)', 1, 5, 3, key=f'importance_{i}')
    
    if subject:
        subjects[subject] = {
            '시험일': test_date,
            '공부량': study_amount,
            '중요도': importance
        }

if st.button('📅 시간표 생성'):
    if not subjects:
        st.warning('과목을 입력해주세요.')
    else:
        today = datetime.date.today()
        schedule = defaultdict(list)

        # 노력량 계산
        total_effort = 0
        effort_map = {}
        for subject, info in subjects.items():
            test_date = info['시험일']
            days_left = (test_date - today).days
            if days_left <= 0:
                st.warning(f"{subject} 시험일이 지났거나 오늘입니다. 제외됩니다.")
                continue
            effort = info['공부량'] * info['중요도']
            effort_map[subject] = {'effort': effort, 'days': days_left}
            total_effort += effort

        if not effort_map:
            st.error("⚠️ 모든 과목의 시험일이 지나거나 입력되지 않아 시간표를 생성할 수 없습니다.")
        else:
            total_slots = sum(v['days'] for v in effort_map.values()) * daily_hours

            # 과목별로 할당할 슬롯 수 계산
            slot_allocation = {}
            for subject, data in effort_map.items():
                slot_allocation[subject] = round((data['effort'] / total_effort) * total_slots)

            # 슬롯 분배
            current_slot = {subject: 0 for subject in slot_allocation}
            subject_list = list(slot_allocation.keys())
            date_cursor = today

            while any(current_slot[subject] < slot_allocation[subject] for subject in subject_list):
                day_schedule = []
                for h in range(daily_hours):
                    for subject in subject_list:
                        if current_slot[subject] < slot_allocation[subject]:
                            current_slot[subject] += 1
                            hour_start = 9 + h  # 시작시간 고정 (예: 오전 9시)
                            hour_end = hour_start + 1
                            time_range = f"{hour_start:02d}:00 ~ {hour_end:02d}:00"
                            day_schedule.append((time_range, subject))
                            break
                schedule[date_cursor] = day_schedule
                date_cursor += datetime.timedelta(days=1)

            # 출력
            st.success(f'{name}님의 시간표입니다 📘')

            for date in sorted(schedule.keys()):
                st.markdown(f"### 📅 {date.strftime('%Y-%m-%d')}")
                for time_range, subject in schedule[date]:
                    st.write(f"🕘 {time_range} → **{subject}**")
