import streamlit as st
import datetime
import pandas as pd
from collections import defaultdict
import random

st.title("📘 실제로 도움이 되는 세부 시험 계획표")

name = st.text_input("이름을 입력하세요:")
subject_count = st.number_input("시험 과목 수:", min_value=1, max_value=10, value=3)
daily_max_hours = st.slider("하루 공부 가능 시간 (최대 12시간)", 1, 12, 6)

subjects = {}
st.subheader("📝 과목별 정보 입력")

for i in range(subject_count):
    st.markdown(f"### 과목 {i + 1}")
    subject = st.text_input(f"과목명 {i + 1}", key=f"subject_{i}")
    test_date = st.date_input(f"{subject} 시험일", key=f"date_{i}")
    study_amount = st.slider(f"{subject} 공부량 (1~10)", 1, 10, 5, key=f"amount_{i}")
    importance = st.slider(f"{subject} 중요도 (1~5)", 1, 5, 3, key=f"importance_{i}")

    if subject:
        subjects[subject] = {
            "시험일": test_date,
            "공부량": study_amount,
            "중요도": importance
        }

if st.button("📅 계획표 만들기"):
    today = datetime.date.today()
    subject_scores = {}
    total_score = 0
    max_days = 0

    # 시험이 남은 과목만 포함
    for subject, info in subjects.items():
        days_left = (info["시험일"] - today).days
        if days_left <= 0:
            continue
        score = info["공부량"] * info["중요도"]
        subject_scores[subject] = {
            "score": score,
            "days_left": days_left,
            "시험일": info["시험일"],
            "total_hours": 0
        }
        total_score += score
        max_days = max(max_days, days_left)

    if not subject_scores:
        st.warning("⛔ 시험일이 지난 과목만 있습니다. 계획을 생성할 수 없습니다.")
    else:
        total_available_hours = daily_max_hours * max_days

        # 과목별 전체 할당 시간 계산
        all_goals = []
        for subject in subject_scores:
            ratio = subject_scores[subject]["score"] / total_score
            total_hours = round(ratio * total_available_hours, 2)
            subject_scores[subject]["total_hours"] = total_hours

            breakdown = [
                ("개념 정리", 0.4),
                ("문제 풀이", 0.4),
                ("오답 정리", 0.2),
            ]

            for name, r in breakdown:
                hours = round(total_hours * r, 2)
                while hours > 0:
                    h = min(hours, 1.5)
                    all_goals.append((subject, name, round(h, 2)))
                    hours -= h

        # 전체 목표를 분배할 큐
        random.shuffle(all_goals)  # 과목 분산을 위한 셔플

        plan = defaultdict(list)
        current_date = today

        for _ in range(max_days):
            available = daily_max_hours
            day_plan = []
            used_subjects = set()
            i = 0
            while i < len(all_goals) and available > 0:
                subject, goal, h = all_goals[i]
                if subject in used_subjects or h > available:
                    i += 1
                    continue
                used_subjects.add(subject)
                day_plan.append((subject, goal, h))
                available -= h
                all_goals.pop(i)  # 큐에서 제거
            if day_plan:
                plan[current_date] = day_plan
            current_date += datetime.timedelta(days=1)

        # 출력
        st.success(f"✅ {name}님의 공부 계획표")

        for date, schedule in plan.items():
            if not schedule:
                continue
            st.markdown(f"### 📅 {date.strftime('%Y-%m-%d')}")
            data = []
            time_cursor = 9.0
            for subject, goal, hours in schedule:
                start = time_cursor
                end = start + hours
                start_str = f"{int(start):02d}:{int((start % 1)*60):02d}"
                end_str = f"{int(end):02d}:{int((end % 1)*60):02d}"
                time_str = f"{start_str} ~ {end_str}"
                data.append((time_str, subject, f"{subject} {goal} ({hours}시간)"))
                time_cursor = end
            df = pd.DataFrame(data, columns=["시간대", "과목", "공부 목표"])
            st.table(df)
