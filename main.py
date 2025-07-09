import streamlit as st
import datetime
import pandas as pd
from collections import defaultdict

st.title("📚 실제 도움이 되는 공부 계획표")

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

    for subject, info in subjects.items():
        days_left = (info["시험일"] - today).days
        if days_left <= 0:
            st.warning(f"⛔ {subject} 시험일이 지났거나 오늘입니다. 제외됩니다.")
            continue
        score = info["공부량"] * info["중요도"]
        subject_scores[subject] = {
            "score": score,
            "days_left": days_left,
            "total_hours": 0  # 나중에 계산
        }
        total_score += score
        max_days = max(max_days, days_left)

    if not subject_scores:
        st.error("⛔ 계획을 세울 수 있는 과목이 없습니다.")
    else:
        total_available_hours = daily_max_hours * max_days

        # 과목별 전체 할당 시간 계산
        for subject in subject_scores:
            ratio = subject_scores[subject]["score"] / total_score
            subject_scores[subject]["total_hours"] = round(ratio * total_available_hours, 2)
            subject_scores[subject]["remaining"] = subject_scores[subject]["total_hours"]

        # 계획표 생성
        plan = defaultdict(list)
        current_date = today

        for day in range(max_days):
            available = daily_max_hours
            day_schedule = []
            # 각 과목 중 남은 시간 많은 순서로 선택
            candidates = sorted(subject_scores.items(), key=lambda x: -x[1]["remaining"])

            for subject, info in candidates:
                if info["remaining"] <= 0:
                    continue
                alloc = min(available, info["remaining"], 3)  # 과목당 하루 최대 3시간
                if alloc < 0.3:
                    continue
                subject_scores[subject]["remaining"] -= alloc
                available -= alloc
                day_schedule.append((subject, round(alloc, 2)))
                if available <= 0:
                    break

            plan[current_date] = day_schedule
            current_date += datetime.timedelta(days=1)

        # 출력
        st.success(f"✅ {name}님의 맞춤 공부 계획표")
        for date, schedule in plan.items():
            if not schedule:
                continue
            st.markdown(f"### 📅 {date.strftime('%Y-%m-%d')}")
            data = []
            time_cursor = 9.0
            for subject, hours in schedule:
                start = time_cursor
                end = start + hours
                time_str = f"{int(start):02d}:{int((start%1)*60):02d} ~ {int(end):02d}:{int((end%1)*60):02d}"
                goal = f"{subject} 공부 ({hours}시간)"
                data.append((time_str, subject, goal))
                time_cursor = end
            df = pd.DataFrame(data, columns=["시간대", "과목", "목표"])
            st.table(df)
