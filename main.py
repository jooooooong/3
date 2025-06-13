import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# -------------------------------
# 설정
# -------------------------------
st.set_page_config(page_title="소비자물가 및 소비 패턴 변화 분석", layout="wide")
st.title("📈 소비자물가 상승률과 소비 패턴 변화 분석")

# -------------------------------
# 데이터 로딩
# -------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("지출목적별_소비자물가지수_품목포함__2020100__20250611104117_분석(전년_대비_증감률).csv", encoding='utf-8')
    df.columns = df.columns.str.strip()  # 컬럼명 공백 제거
    df['시점'] = pd.to_datetime(df['시점'], format='%Y%m')  # 날짜형으로 변환
    return df

df = load_data()

# -------------------------------
# 사용자 입력
# -------------------------------
st.sidebar.header("🔍 필터 설정")
start_date = st.sidebar.date_input("시작 시점", df["시점"].min().date())
end_date = st.sidebar.date_input("종료 시점", df["시점"].max().date())
category = st.sidebar.selectbox("지출 목적 선택", ["전체지수"] + sorted(df["지출목적별"].unique()))

filtered_df = df[(df["시점"] >= pd.to_datetime(start_date)) & (df["시점"] <= pd.to_datetime(end_date))]

if category != "전체지수":
    filtered_df = filtered_df[filtered_df["지출목적별"] == category]

# -------------------------------
# 1. 소비자물가 상승률 추이
# -------------------------------
st.subheader("1️⃣ 소비자물가 상승률 추이")

plt.figure(figsize=(12, 4))
sns.lineplot(data=filtered_df, x="시점", y="전년_대비_증감률", hue="지출목적별")
plt.title("전년 대비 소비자물가 상승률")
plt.xlabel("시점")
plt.ylabel("전년 대비 상승률 (%)")
plt.xticks(rotation=45)
st.pyplot(plt.gcf())
plt.clf()

# -------------------------------
# 2. 품목별 소비자물가 상승률 (최근 월)
# -------------------------------
st.subheader("2️⃣ 최근 시점 품목별 소비자물가 상승률 TOP 10")

latest_date = filtered_df["시점"].max()
latest_df = filtered_df[filtered_df["시점"] == latest_date]

top10 = latest_df.sort_values("전년_대비_증감률", ascending=False).head(10)
bottom10 = latest_df.sort_values("전년_대비_증감률").head(10)

col1, col2 = st.columns(2)

with col1:
    st.markdown("#### 📈 상승률 TOP 10")
    st.dataframe(top10[["지출목적별", "품목", "전년_대비_증감률"]])
with col2:
    st.markdown("#### 📉 하락률 TOP 10")
    st.dataframe(bottom10[["지출목적별", "품목", "전년_대비_증감률"]])

# -------------------------------
# 3. 품목별 상세 변화 그래프
# -------------------------------
st.subheader("3️⃣ 품목별 상세 변화 추이")

selected_items = st.multiselect("분석할 품목 선택", sorted(df["품목"].dropna().unique()), default=["쌀", "휘발유"])

if selected_items:
    item_df = df[df["품목"].isin(selected_items)]

    plt.figure(figsize=(14, 5))
    sns.lineplot(data=item_df, x="시점", y="전년_대비_증감률", hue="품목")
    plt.title("품목별 소비자물가 상승률 추이")
    plt.xlabel("시점")
    plt.ylabel("전년 대비 상승률 (%)")
    plt.xticks(rotation=45)
    st.pyplot(plt.gcf())
    plt.clf()
