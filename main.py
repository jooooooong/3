import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.font_manager as fm
import os

# -------------------------------
# 한글 폰트 설정 (NanumGothic)
# -------------------------------
def set_korean_font():
    font_path = "NanumGothic.ttf"
    if os.path.exists(font_path):
        fm.fontManager.addfont(font_path)
        plt.rcParams['font.family'] = 'NanumGothic'
        plt.rcParams['axes.unicode_minus'] = False
    else:
        st.warning("⚠️ NanumGothic.ttf 폰트 파일이 없으면 한글이 깨질 수 있습니다.")

set_korean_font()

# -------------------------------
# 페이지 설정
# -------------------------------
st.set_page_config(page_title="소비자물가 및 소비 패턴 변화 분석", layout="wide")
st.title("📊 소비자물가 상승률과 소비 패턴 변화 분석")

# -------------------------------
# 데이터 불러오기 및 전처리
# -------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv(
        "지출목적별_소비자물가지수_품목포함__2020100__20250611104117_분석(전년_대비_증감률).csv",
        encoding='cp949'
    )
    df.columns = df.columns.str.strip()

    # wide → long format 변환
    id_vars = ['시도별', '지출목적별']
    value_vars = [col for col in df.columns if col not in id_vars]
    df_long = pd.melt(df, id_vars=id_vars, value_vars=value_vars, var_name='시점', value_name='전년_대비_증감률')

    # 시점 형식 변환
    df_long['시점'] = pd.to_datetime(df_long['시점'].str.replace('.1', '-07').str.replace('.0', '-01'), format='%Y-%m', errors='coerce')

    # 수치형 변환
    df_long['전년_대비_증감률'] = pd.to_numeric(df_long['전년_대비_증감률'], errors='coerce')

    return df_long

df = load_data()

# -------------------------------
# 필터 설정
# -------------------------------
st.sidebar.header("🔎 필터 설정")
start_date = st.sidebar.date_input("시작 시점", df["시점"].min().date())
end_date = st.sidebar.date_input("종료 시점", df["시점"].max().date())
category = st.sidebar.selectbox("지출 목적 선택", sorted(df["지출목적별"].unique()))

# 필터 적용
filtered_df = df[(df["시점"] >= pd.to_datetime(start_date)) & (df["시점"] <= pd.to_datetime(end_date))]
filtered_df = filtered_df[filtered_df["지출목적별"] == category]

# -------------------------------
# 1. 시도별 꺾은선 그래프
# -------------------------------
st.subheader("1️⃣ 시도별 소비자물가 상승률 추이")

plt.figure(figsize=(12, 5))
sns.lineplot(data=filtered_df, x="시점", y="전년_대비_증감률", hue="시도별", errorbar=None)
plt.title(f"{category} - 시도별 소비자물가 상승률")
plt.xlabel("시점")
plt.ylabel("전년 대비 상승률 (%)")
plt.xticks(rotation=45)
plt.grid(True)
st.pyplot(plt.gcf())
plt.clf()

# -------------------------------
# 2. 최근 시점 기준 TOP/BOTTOM 10
# -------------------------------
st.subheader("2️⃣ 최근 시점 기준 시도별 상승률 TOP/BOTTOM 10")

latest_date = filtered_df["시점"].max()
latest_df = filtered_df[filtered_df["시점"] == latest_date]

top10 = latest_df.sort_values("전년_대비_증감률", ascending=False).head(10)
bottom10 = latest_df.sort_values("전년_대비_증감률").head(10)

col1, col2 = st.columns(2)
with col1:
    st.markdown("#### 🔺 상승률 TOP 10")
    st.dataframe(top10[["시도별", "전년_대비_증감률"]])
with col2:
    st.markdown("#### 🔻 하락률 TOP 10")
    st.dataframe(bottom10[["시도별", "전년_대비_증감률"]])
