import streamlit as st
import datetime
import pandas as pd
from collections import defaultdict

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
            "total_hours": 0  # 나중에 계산
        }
        total_score += score
        max_days = max(max_days, days_left)

    if not subject_scores:
        st.warning("⛔ 시험일이 지난 과목만 있습니다. 계획을 생성할 수 없습니다.")
    else:
        total_available_hours = daily_max_hours * max_days

        # 과목별 전체 할당 시간 계산
        for subject in subject_scores:
            ratio = subject_scores[subject]["score"] / total_score
            total_hours = round(ratio * total_available_hours, 2)
            subject_scores[subject]["total_hours"] = total_hours
            subject_scores[subject]["remaining"] = total_hours

            # 세부 목표 분할
            subject_scores[subject]["goals"] = []
            breakdown = [
                ("개념 정리", 0.4),
                ("문제 풀이", 0.4),
                ("오답 정리", 0.2),
            ]
            for name, ratio in breakdown:
                part_hours = round(total_hours * ratio, 2)
                chunks = []
                while part_hours > 0:
                    h = min(part_hours, 1.5)
                    chunks.append((name, round(h, 2)))
                    part_hours -= h
                subject_scores[subject]["goals"].extend(chunks)

        # 계획표 생성
        plan = defaultdict(list)
        current_date = today

        for _ in range(max_days):
            available = daily_max_hours
            day_schedule = []

            # 과목별로 고르게 분산
            for subject, info in subject_scores.items():
                if not info["goals"]:
                    continue
                while available > 0 and info["goals"]:
                    goal, time = info["goals"][0]
                    if time > available:
                        break
                    info["goals"].pop(0)
                    available -= time
                    day_schedule.append((subject, goal, time))
                if available <= 0:
                    break

            if day_schedule:
                plan[current_date] = day_schedule
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
                start_str = f"{int(start):02d}:{int((start%1)*60):02d}"
                end_str = f"{int(end):02d}:{int((end%1)*60):02d}"
                time_str = f"{start_str} ~ {end_str}"
                data.append((time_str, subject, f"{subject} {goal} ({hours}시간)"))
                time_cursor = end
            df = pd.DataFrame(data, columns=["시간대", "과목", "공부 목표"])
            st.table(df)
