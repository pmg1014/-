import streamlit as st
import datetime
import pandas as pd
from collections import defaultdict
import random

st.title("📘 시험 대비 공부 계획표")

# 사용자 입력
name = st.text_input("이름을 입력하세요:")
subject_count = st.number_input("시험 과목 수:", min_value=1, max_value=10, value=3)
daily_max_hours = st.slider("하루 공부 가능 시간 (최대 12시간)", 1, 12, 8)

# 과목 정보 입력
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
    total_score = 0
    valid_subjects = {}

    # 시험일이 남은 과목만 필터링
    for subject, info in subjects.items():
        days_left = (info["시험일"] - today).days
        if days_left <= 0:
            continue
        score = info["공부량"] * info["중요도"]
        valid_subjects[subject] = {
            "시험일": info["시험일"],
            "days_left": days_left,
            "score": score
        }
        total_score += score

    if not valid_subjects:
        st.warning("⛔ 시험일이 지난 과목만 있습니다. 계획을 생성할 수 없습니다.")
    else:
        max_days = max(v["days_left"] for v in valid_subjects.values())
        total_available_hours = max_days * daily_max_hours

        # 각 과목에 할당할 전체 시간 계산
        for subject, info in valid_subjects.items():
            ratio = info["score"] / total_score
            total_hours = round(ratio * total_available_hours, 1)
            valid_subjects[subject]["total_hours"] = total_hours
            valid_subjects[subject]["goals"] = []

            # 공부 목표 나누기 (개념 40%, 문제 40%, 오답 20%)
            breakdown = [("개념 정리", 0.4), ("문제 풀이", 0.4), ("오답 정리", 0.2)]
            for part, r in breakdown:
                part_h = round(total_hours * r, 1)
                while part_h > 0:
                    chunk = min(1.5, part_h)
                    valid_subjects[subject]["goals"].append((part, round(chunk, 1)))
                    part_h -= chunk

        # 전체 목표 큐 만들기
        goals_queue = []
        for subject, info in valid_subjects.items():
            for goal, h in info["goals"]:
                goals_queue.append((subject, goal, h))

        # 과목 분산을 위한 섞기
        random.shuffle(goals_queue)

        # 계획표 생성
        plan = defaultdict(list)
        current_date = today

        for _ in range(max_days):
            available = daily_max_hours
            today_plan = []
            used_subjects = set()
            i = 0

            while i < len(goals_queue) and available > 0:
                subject, goal, h = goals_queue[i]
                if subject in used_subjects or h > available:
                    i += 1
                    continue
                used_subjects.add(subject)
                today_plan.append((subject, goal, h))
                available -= h
                goals_queue.pop(i)  # 큐에서 제거
                i = 0  # 다시 처음부터 탐색 (다른 과목 찾기)

            plan[current_date] = today_plan
            current_date += datetime.timedelta(days=1)

        # 결과 출력
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
                data.append((time_str, subject, f"{goal} ({hours}시간)"))
                time_cursor = end
            df = pd.DataFrame(data, columns=["시간대", "과목", "공부 목표"])
            st.table(df)

