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
start_hour = st.slider("공부 시작 시간", 6, 12, 9)
block_unit = st.selectbox("공부 시간 단위 (시간)", [0.5, 1.0, 1.5], index=2)

# 과목 정보 입력
subjects = {}
st.subheader("📝 과목별 정보 입력")

for i in range(subject_count):
    st.markdown(f"### 과목 {i + 1}")
    subject = st.text_input(f"과목명 {i + 1}", key=f"subject_{i}").strip()
    test_date = st.date_input(f"{subject or '과목'} 시험일", key=f"date_{i}")
    study_amount = st.slider(f"{subject or '과목'} 공부량 (1~10)", 1, 10, 5, key=f"amount_{i}")
    importance = st.slider(f"{subject or '과목'} 중요도 (1~5)", 1, 5, 3, key=f"importance_{i}")

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

    # 유효한 과목 필터링 및 점수 계산
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

        # 각 과목에 공부 시간 분배 및 목표 생성
        for subject, info in valid_subjects.items():
            ratio = info["score"] / total_score
            total_hours = round(ratio * total_available_hours, 1)
            valid_subjects[subject]["total_hours"] = total_hours
            valid_subjects[subject]["goals"] = []

            # 목표 나누기 (개념/문제/오답)
            breakdown = [("개념 정리", 0.4), ("문제 풀이", 0.4), ("오답 정리", 0.2)]
            for part, r in breakdown:
                part_h = round(total_hours * r, 1)
                while part_h > 0:
                    chunk = min(block_unit, part_h)
                    valid_subjects[subject]["goals"].append((part, round(chunk, 1)))
                    part_h -= chunk

        # 전체 목표 큐 (시험일 기준 정렬)
        goals_queue = []
        for subject, info in sorted(valid_subjects.items(), key=lambda x: x[1]["시험일"]):
            for goal, h in info["goals"]:
                goals_queue.append((subject, goal, h))

        # 목표 부족 시 반복 학습 추가
        expected_goal_count = int((max_days * daily_max_hours) / block_unit)
        original_goals = goals_queue.copy()
        while len(goals_queue) < expected_goal_count:
            repeat_sample = random.sample(original_goals, min(len(original_goals), 10))
            goals_queue.extend(repeat_sample)

        # 공부 계획표 생성
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
                goals_queue.pop(i)
                i = 0

            plan[current_date] = today_plan
            current_date += datetime.timedelta(days=1)

        # 출력 및 결과 저장
        st.success(f"✅ {name}님의 공부 계획표")

        full_data = []

        for date, schedule in plan.items():
            if not schedule:
                continue
            st.markdown(f"### 📅 {date.strftime('%Y-%m-%d')}")
            data = []
            time_cursor = float(start_hour)
            for subject, goal, hours in schedule:
                start = time_cursor
                end = start + hours
                start_str = f"{int(start):02d}:{int((start % 1) * 60):02d}"
                end_str = f"{int(end):02d}:{int((end % 1) * 60):02d}"
                time_str = f"{start_str} ~ {end_str}"
                data.append((time_str, subject, f"{goal} ({hours}시간)"))
                full_data.append((date.strftime("%Y-%m-%d"), time_str, subject, f"{goal} ({hours}시간)"))
                time_cursor = end

            df = pd.DataFrame(data, columns=["시간대", "과목", "공부 목표"])
            st.table(df)

        # CSV 다운로드 기능
        if full_data:
            final_df = pd.DataFrame(full_data, columns=["날짜", "시간", "과목", "공부 목표"])
            csv = final_df.to_csv(index=False, encoding='utf-8-sig')
            st.download_button("📥 계획표 다운로드 (CSV)", data=csv, file_name="공부계획표.csv", mime="text/csv")
