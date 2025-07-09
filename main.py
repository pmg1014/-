import streamlit as st
import datetime
import pandas as pd
from collections import defaultdict, deque

st.title('📚 조화로운 시험 공부 계획표')

name = st.text_input('이름을 입력해주세요:')
subject_count = st.number_input('시험 과목 수:', min_value=1, max_value=10, value=3)
daily_hours = st.slider('하루 공부 시간 (시간 단위)', 1, 10, 4)

subjects = {}
st.subheader('📝 과목별 시험 정보 입력')

# 과목 정보 입력
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

if st.button('🗓️ 공부 계획표 생성'):
    if not subjects:
        st.warning('과목을 1개 이상 입력해주세요.')
    else:
        today = datetime.date.today()
        effort_map = {}
        total_effort = 0

        # 유효한 과목 필터링
        for subject, info in subjects.items():
            days_left = (info['시험일'] - today).days
            if days_left <= 0:
                st.warning(f'{subject} 시험일이 지났거나 오늘입니다. 제외됩니다.')
                continue
            effort = info['공부량'] * info['중요도']
            effort_map[subject] = {
                'effort': effort,
                'days_left': days_left
            }
            total_effort += effort

        if not effort_map:
            st.error("⛔ 남은 과목이 없습니다.")
        else:
            # 전체 슬롯 수 계산
            total_slots = sum(v['days_left'] for v in effort_map.values()) * daily_hours

            # 과목별 할당할 슬롯 수 계산
            slot_allocation = {
                subject: round((info['effort'] / total_effort) * total_slots)
                for subject, info in effort_map.items()
            }

            # 과목들을 균형 있게 분배할 순서 큐 만들기
            subject_queue = deque(sorted(slot_allocation.items(), key=lambda x: -x[1]))

            schedule = defaultdict(list)
            current_date = today

            while any(v > 0 for _, v in slot_allocation.items()):
                day = []
                used_today = set()
                for hour in range(daily_hours):
                    for _ in range(len(subject_queue)):
                        subject, slots_left = subject_queue.popleft()
                        if slots_left > 0 and subject not in used_today:
                            hour_start = 9 + hour
                            hour_end = hour_start + 1
                            time_range = f"{hour_start:02d}:00 ~ {hour_end:02d}:00"
                            day.append((time_range, subject))
                            slot_allocation[subject] -= 1
                            used_today.add(subject)
                            subject_queue.append((subject, slot_allocation[subject]))
                            break
                        else:
                            subject_queue.append((subject, slots_left))
                schedule[current_date] = day
                current_date += datetime.timedelta(days=1)

            # 결과 출력
            st.success(f'📅 {name}님의 공부 시간표입니다.')

            for date in sorted(schedule.keys()):
                st.markdown(f"### {date.strftime('%Y-%m-%d')}")
                time_list = [entry[0] for entry in schedule[date]]
                subject_list = [entry[1] for entry in schedule[date]]
                df = pd.DataFrame({
                    "시간": time_list,
                    "공부 과목": subject_list
                })
                st.table(df)
