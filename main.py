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

st.title("\ud83d\udcca \uc18c\ube44\uc790\ubb3c가 \uc0c1승\ub960과 \uc18c비 \ud328턴 변화 및 분석")

if not set_korean_font():
    st.warning("\u26a0\ufe0f NanumGothic.ttf \ud3f0트 \ud30c일이 \uc5c6으면 \uadf8래프에 \ud55c글이 깊일 \uc218 있습니다.")

# -------------------------------
# \ub370이\ud130 \ubd88러오기
# -------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv(
        "\uc9c0출목적별_\uc18c\ube44자\ubb3c가지수_\ud488목포함__2020100__20250611104117_\ubd84석(\uc804년_\ub300비_\uc99d가률).csv",
        encoding='cp949'
    )
    df.columns = df.columns.str.strip()

    # melt\ub85c \uae38 \ud3ec맷으로 \ubcc0환
    year_cols = df.columns[2:]
    years = list(dict.fromkeys(col.split('.')[0] for col in year_cols))

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
                '\uc2dc도별': row['\uc2dc도별'],
                '\uc9c0출목적별': row['\uc9c0출목적별'],
                '\uc5f0도': int(year),
                '\uc18c\ube44\uc790\ubb3c가지수': raw,
                '\uc804년_\ub300비_\uc99d가률': diff
            })

    df_long = pd.DataFrame.from_records(records)
    df_long['\ud45c시용\uc5f0도'] = df_long['\uc5f0도'].astype(str) + "\ub144"
    return df_long

df = load_data()

# -------------------------------
# \ud544터 \uc124정
# -------------------------------
st.sidebar.header("\ud83d\udd0e \ud544\ud130 \uc124정")
years = sorted(df["\uc5f0도"].unique())
start_year, end_year = st.sidebar.select_slider("\ubd84석 \uae30간 \uc120택", options=years, value=(years[0], years[-1]))

category_list = sorted([c for c in df["\uc9c0출목적별"].unique() if "\uc9c0출목적별" not in c])
category = st.sidebar.selectbox("\uc9c0출 \ud56d목 \uc120택", category_list)

# \ud544\ud130 \uc801용
df_plot = df[
    (df["\uc5f0도"] >= start_year) &
    (df["\uc5f0도"] <= end_year) &
    (df["\uc9c0출목적별"] == category)
]

# -------------------------------
# \uc2dc각화: \uaebc여선 \uadf8래프
# -------------------------------
st.subheader("\ud83d\udcc8 \uc18c\ube44\uc790\ubb3c가지수 & \uc804년 \ub300비 \uc99d가률")

line_cpi = alt.Chart(df_plot).mark_line(color="green", strokeWidth=3).encode(
    x=alt.X("\uc5f0도:O", title="\uc5f0도", labelAngle=0),
    y=alt.Y("\uc18c\ube44\uc790\ubb3c가지수:Q", title="\uc9c0수"),
    tooltip=["\ud45c시용\uc5f0도", alt.Tooltip("\uc18c\ube44\uc790\ubb3c가지수:Q", title="\uc9c0수")]
)

point_cpi = alt.Chart(df_plot).mark_circle(color="green", size=40).encode(
    x=alt.X("\uc5f0도:O", labelAngle=0),
    y="\uc18c\ube44\uc790\ubb3c가지수:Q",
    tooltip=["\ud45c시용\uc5f0도", alt.Tooltip("\uc18c\ube44\uc790\ubb3c가지수:Q", title="\uc9c0수")]
)

line_rate = alt.Chart(df_plot).mark_line(color="blue", strokeDash=[0], strokeWidth=2).encode(
    x=alt.X("\uc5f0도:O", labelAngle=0),
    y=alt.Y("\uc804년_\ub300비_\uc99d가률:Q", title="\uc804년 \ub300비 \uc99d가률 (%)"),
    tooltip=["\ud45c시용\uc5f0도", alt.Tooltip("\uc804년_\ub300비_\uc99d가률:Q", title="\uc804년 \ub300비")]
)

point_rate = alt.Chart(df_plot).mark_circle(color="blue", size=40).encode(
    x=alt.X("\uc5f0도:O", labelAngle=0),
    y="\uc804년_\ub300비_\uc99d가률:Q",
    tooltip=["\ud45c시용\uc5f0도", alt.Tooltip("\uc804년_\ub300비_\uc99d가률:Q", title="\uc804년 \ub300비")]
)

chart = alt.layer(line_cpi + point_cpi, line_rate + point_rate).resolve_scale(y='independent')
st.altair_chart(chart, use_container_width=True)

# -------------------------------
# \ucd5c대 \uc0c1승/\ud558랑 \uc2dc점 \ud45c시
# -------------------------------
st.subheader("\ud83d\udccc \ucd5c대 \uc0c1승/\ud558랑 \uc2dc점")

max_row = df_plot.loc[df_plot['\uc804년_\ub300비_\uc99d가률'].idxmax()]
min_row = df_plot.loc[df_plot['\uc804년_\ub300비_\uc99d가률'].idxmin()]

col1, col2 = st.columns(2)
with col1:
    st.markdown(f"\ud83d\udd3a **\uac00\uc7a5 \ub9ce이 \uc62c아\ub978 \ud574**: {max_row['\uc5f0도']}\ub144")
    st.markdown(f"- \uc0c1승\ub960: {max_row['\uc804년_\ub300비_\uc99d가률']}%")
    st.markdown(f"- \uc18c\ube44\uc790\ubb3c가지수: {max_row['\uc18c\ube44\uc790\ubb3c가지수']}")

with col2:
    st.markdown(f"\ud83d\udd3b **\uac00\uc7a5 \ub9ce이 \ub0b4린 \ud574**: {min_row['\uc5f0도']}\ub144")
    st.markdown(f"- \ud558랑\ub960: {min_row['\uc804년_\ub300비_\uc99d가률']}%")
    st.markdown(f"- \uc18c\ube44\uc790\ubb3c가지수: {min_row['\uc18c\ube44\uc790\ubb3c가지수']}")
