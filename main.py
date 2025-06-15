import streamlit as st

# ✅ 반드시 가장 먼저 실행
st.set_page_config(page_title="소비자물가 및 소비 패턴 변화 분석", layout="wide")

# 라이브러리 임포트
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.font_manager as fm
import altair as alt
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

st.title("📊 소비자물가 상승률과 소비 패턴 변화 분석")

if not set_korean_font():
    st.warning("⚠️ NanumGothic.ttf 폰트 파일이 없으면 그래프에 한글이 깨질 수 있습니다.")

# -------------------------------
# 데이터 불러오기
# -------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv(
        "지출목적별_소비자물가지수_품목포함__2020100__20250611104117_분석(전년_대비_증감률).csv",
        encoding='cp949'
    )
    df.columns = df.columns.str.strip()

    # melt로 긴 포맷으로 변환
    year_cols = df.columns[2:]
    half = ['원데이터', '전년_대비_증감률']
    years = list(dict.fromkeys(col.split('.')[0] for col in year_cols))  # 중복 제거 순서 유지

    records = []
    for _, row in df.iterrows():
        for i, year in enumerate(years):
            try:
                raw = float(row[2 + i * 2])
            except:
                raw = None
            try:
                diff = float(row[2 + i * 2 + 1])
            except:
                diff = None
            records.append({
                '시도별': row['시도별'],
                '지출목적별': row['지출목적별'],
                '연도': int(year),
                '소비자물가지수': raw,
                '전년_대비_증감률': diff
            })

    df_long = pd.DataFrame.from_records(records)
    df_long['표시용연도'] = df_long['연도'].astype(str) + "년"
    return df_long

df = load_data()

# -------------------------------
# 필터 설정
# -------------------------------
st.sidebar.header("🔎 필터 설정")
years = sorted(df["연도"].unique())
start_year, end_year = st.sidebar.select_slider("분석 기간 선택", options=years, value=(years[0], years[-1]))

category_list = sorted([c for c in df["지출목적별"].unique() if "지출목적별" not in c])
category = st.sidebar.selectbox("지출 항목 선택", category_list)

# 필터 적용
df_plot = df[
    (df["연도"] >= start_year) &
    (df["연도"] <= end_year) &
    (df["지출목적별"] == category)
]

# -------------------------------
# 시각화: 꺾은선 그래프
# -------------------------------
st.subheader("📈 소비자물가지수 & 전년 대비 증감률")

line_cpi = alt.Chart(df_plot).mark_line(color="green", strokeWidth=3).encode(
    x=alt.X("연도:O", title="연도"),
    y=alt.Y("소비자물가지수:Q", title="지수"),
    tooltip=["표시용연도", alt.Tooltip("소비자물가지수:Q", title="지수")]
)

point_cpi = alt.Chart(df_plot).mark_point(color="green", size=70).encode(
    x="연도:O",
    y="소비자물가지수:Q",
    tooltip=["표시용연도", alt.Tooltip("소비자물가지수:Q", title="지수")]
)

line_rate = alt.Chart(df_plot).mark_line(color="blue", strokeDash=[0], strokeWidth=2).encode(
    x="연도:O",
    y=alt.Y("전년_대비_증감률:Q", title="전년 대비 증감률 (%)"),
    tooltip=["표시용연도", alt.Tooltip("전년_대비_증감률:Q", title="전년 대비")]
)

point_rate = alt.Chart(df_plot).mark_point(color="blue", size=70).encode(
    x="연도:O",
    y="전년_대비_증감률:Q",
    tooltip=["표시용연도", alt.Tooltip("전년_대비_증감률:Q", title="전년 대비")]
)

chart = alt.layer(line_cpi + point_cpi, line_rate + point_rate).resolve_scale(y='independent')
st.altair_chart(chart, use_container_width=True)

# -------------------------------
# 최대 상승/하락 시점 표시
# -------------------------------
st.subheader("📌 최대 상승/하락 시점")

max_row = df_plot.loc[df_plot['전년_대비_증감률'].idxmax()]
min_row = df_plot.loc[df_plot['전년_대비_증감률'].idxmin()]

col1, col2 = st.columns(2)
with col1:
    st.markdown(f"🔺 **가장 많이 오른 해**: {max_row['연도']}년")
    st.markdown(f"- 상승률: {max_row['전년_대비_증감률']}%")
    st.markdown(f"- 소비자물가지수: {max_row['소비자물가지수']}")

with col2:
    st.markdown(f"🔻 **가장 많이 내린 해**: {min_row['연도']}년")
    st.markdown(f"- 하락률: {min_row['전년_대비_증감률']}%")
    st.markdown(f"- 소비자물가지수: {min_row['소비자물가지수']}")
