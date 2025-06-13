import streamlit as st

# ✅ set_page_config는 반드시 가장 위에서 실행
st.set_page_config(page_title="소비자물가 및 소비 패턴 변화 분석", layout="wide")

# 나머지 라이브러리 임포트
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.font_manager as fm
import os

# -------------------------------
# 한글 폰트 설정
# -------------------------------
def set_korean_font():
    font_path = "NanumGothic.ttf"
    if os.path.exists(font_path):
        fm.fontManager.addfont(font_path)
        plt.rcParams['font.family'] = 'NanumGothic'
        plt.rcParams['axes.unicode_minus'] = False
        return True
    return False

# -------------------------------
# 앱 제목 및 폰트 경고
# -------------------------------
st.title("📊 소비자물가 상승률과 소비 패턴 변화 분석")

if not set_korean_font():
    st.warning("⚠️ NanumGothic.ttf 폰트 파일이 없으면 그래프에 한글이 깨질 수 있습니다.")

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

    # wide → long 변환
    id_vars = ['시도별', '지출목적별']
    value_vars = [col for col in df.columns if col not in id_vars]
    df_long = pd.melt(df, id_vars=id_vars, value_vars=value_vars,
                      var_name='시점', value_name='전년_대비_증감률')

    # 시점 열 문자열 → 날짜
    df_long['시점'] = pd.to_datetime(
        df_long['시점'].str.replace('.1', '-07').str.replace('.0', '-01'),
        format='%Y-%m', errors='coerce'
    )

    # 수치형 변환
    df_long['전년_대비_증감률'] = pd.to_numeric(df_long['전년_대비_증감률'], errors='coerce')

    return df_long

df = load_data()

# -------------------------------
# 사이드바 필터
# -------------------------------
st.sidebar.header("🔎 필터 설정")
start_date = st.sidebar.date_input("시작 시점", df["시점"].min().date())
end_date = st.sidebar.date_input("종료 시점", df["시점"].max().date())
category = st.sidebar.selectbox("지출 목적 선택", sorted(df["지출목적별"].unique()))

# 필터 적용
filtered_df = df[
    (df["시점"] >= pd.to_datetime(start_date)) &
    (df["시점"] <= pd.to_datetime(end_date)) &
    (df["지출목적별"] == category)
]

# -------------------------------
# 1. 꺾은선 그래프
# -------------------------------
st.subheader("📈 전년 대비 소비자물가 상승률 추이")

plt.figure(figsize=(12, 5))
sns.lineplot(data=filtered_df, x="시점", y="전년_대비_증감률", errorbar=None)
plt.title(f"{category} - 소비자물가 상승률 추이")
plt.xlabel("시점")
plt.ylabel("전년 대비 상승률 (%)")
plt.xticks(rotation=45)
plt.grid(True)
st.pyplot(plt.gcf())
plt.clf()

# -------------------------------
# 2. 최대/최소 상승률 시점 요약
# -------------------------------
st.subheader("📌 선택 기간 내 최고 / 최저 전년 대비 상승률")

if not filtered_df.empty:
    max_row = filtered_df.loc[filtered_df["전년_대비_증감률"].idxmax()]
    min_row = filtered_df.loc[filtered_df["전년_대비_증감률"].idxmin()]

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 🔺 가장 많이 오른 시점")
        st.metric(
            label=f"{max_row['시점'].strftime('%Y년 %m월')}",
            value=f"{max_row['전년_대비_증감률']:.2f}%",
        )

    with col2:
        st.markdown("#### 🔻 가장 많이 내린 시점")
        st.metric(
            label=f"{min_row['시점'].strftime('%Y년 %m월')}",
            value=f"{min_row['전년_대비_증감률']:.2f}%",
        )
else:
    st.info("선택된 조건에 해당하는 데이터가 없습니다.")
