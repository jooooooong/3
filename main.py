import streamlit as st

# 가장 먼저 실행
st.set_page_config(page_title="소비자물가 및 소비 패턴 변화 분석", layout="wide")

# 기타 라이브러리
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import os
import altair as alt

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

st.title("📊 소비자물가 상승률과 소비 패턴 변화 분석")
if not set_korean_font():
    st.warning("⚠️ NanumGothic.ttf 폰트 파일이 없으면 그래프에 한글이 깨질 수 있습니다.")

# -------------------------------
# 데이터 불러오기 및 변환
# -------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("지출목적별_소비자물가지수_품목포함__2020100__20250611104117_분석(전년_대비_증감률).csv", encoding='cp949')
    df.columns = df.columns.str.strip()
    df = df[df["지출목적별"] != "지출목적별"]  # 잘못된 항목 제거

    id_vars = ['시도별', '지출목적별']
    value_vars = [col for col in df.columns if col not in id_vars]
    df_long = pd.melt(df, id_vars=id_vars, value_vars=value_vars, var_name='시점', value_name='전년_대비_증감률')

    df_long['시점'] = df_long['시점'].str.replace('.1', '-07').str.replace('.0', '-01')
    df_long['시점'] = pd.to_datetime(df_long['시점'], format='%Y-%m', errors='coerce')
    df_long['연도'] = df_long['시점'].dt.year
    df_long['전년_대비_증감률'] = pd.to_numeric(df_long['전년_대비_증감률'], errors='coerce')

    return df_long

df = load_data()

# -------------------------------
# 필터 설정 (연도 & 지출 항목)
# -------------------------------
st.sidebar.header("🔎 필터 설정")
years = sorted(df["연도"].dropna().unique())
start_year, end_year = st.sidebar.select_slider("연도 범위 선택", options=years, value=(min(years), max(years)))

category_options = sorted(df["지출목적별"].unique())
category = st.sidebar.selectbox("지출 항목 선택", category_options)

filtered_df = df[
    (df["연도"] >= start_year) &
    (df["연도"] <= end_year) &
    (df["지출목적별"] == category)
]

# -------------------------------
# 1. Altair 그래프 (겹쳐서 표시)
# -------------------------------
st.subheader("📈 소비자물가 지수 (원데이터) 및 전년 대비 증감률 추이")

# 원데이터 = 실제 지수, 전년대비 증감률은 y2 축
df_plot = filtered_df.copy()
df_plot["연도"] = df_plot["시점"].dt.year
df_plot["월"] = df_plot["시점"].dt.month
df_plot["표시용시점"] = df_plot["시점"].dt.strftime("%Y-%m")

# Altair 기반 시각화
base = alt.Chart(df_plot).encode(
    x=alt.X('시점:T', axis=alt.Axis(title='시점'))
)

line1 = base.mark_line(color='blue').encode(
    y=alt.Y('전년_대비_증감률:Q', axis=alt.Axis(title='전년 대비 증감률 (%)')),
    tooltip=['표시용시점', '전년_대비_증감률']
)

line2 = base.mark_line(color='orange').encode(
    y=alt.Y('전년_대비_증감률:Q', axis=alt.Axis(title='전년 대비 증감률 (%)'), scale=alt.Scale(zero=False)),
    tooltip=['표시용시점', '전년_대비_증감률']
)

# 실제 지수 (원데이터)
line_data = base.mark_line(color='green').encode(
    y=alt.Y('전년_대비_증감률:Q', axis=alt.Axis(title='지수 값'), scale=alt.Scale(zero=False)),
    tooltip=['표시용시점', '전년_대비_증감률']
)

# 이중 축 그래프 생성
chart = alt.layer(line_data, line1).resolve_scale(
    y='independent'
).properties(width=800, height=400)

st.altair_chart(chart, use_container_width=True)

# -------------------------------
# 2. 최고/최저 요약
# -------------------------------
st.subheader("📌 최고 / 최저 상승률 요약")

if not filtered_df.empty:
    max_row = filtered_df.loc[filtered_df["전년_대비_증감률"].idxmax()]
    min_row = filtered_df.loc[filtered_df["전년_대비_증감률"].idxmin()]

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### 🔺 최고 상승 시점")
        st.metric(
            label=f"{max_row['연도']}년",
            value=f"{max_row['전년_대비_증감률']:.2f}%",
            delta=f"지수값: {max_row['전년_대비_증감률']:.2f}"
        )
    with col2:
        st.markdown("#### 🔻 최저 하락 시점")
        st.metric(
            label=f"{min_row['연도']}년",
            value=f"{min_row['전년_대비_증감률']:.2f}%",
            delta=f"지수값: {min_row['전년_대비_증감률']:.2f}"
        )
else:
    st.info("선택된 범위에 해당하는 데이터가 없습니다.")
