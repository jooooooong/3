import streamlit as st

# ✅ set_page_config는 가장 위에서 실행
st.set_page_config(page_title="소비자물가 및 소비 패턴 변화 분석", layout="wide")

# 라이브러리 불러오기
import pandas as pd
import altair as alt
import matplotlib.font_manager as fm
import os

# -------------------------------
# 한글 폰트 설정
# -------------------------------
def set_korean_font():
    font_path = "NanumGothic.ttf"
    if os.path.exists(font_path):
        fm.fontManager.addfont(font_path)
        return True
    return False

# 앱 제목 및 폰트 경고
st.title("📊 소비자물가 상승률과 소비 패턴 변화 분석")
if not set_korean_font():
    st.warning("⚠️ NanumGothic.ttf 폰트 파일이 없으면 그래프에 한글이 깨질 수 있습니다.")

# -------------------------------
# 데이터 로드 및 전처리
# -------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("지출목적별_소비자물가지수_품목포함__2020100__20250611104117_분석(전년_대비_증감률).csv", encoding='cp949', skiprows=[1])
    df.columns = df.iloc[0]
    df = df.drop(index=0)
    df = df.rename(columns={df.columns[0]: "시도별", df.columns[1]: "지출목적별"})
    df = df.reset_index(drop=True)

    id_vars = ["시도별", "지출목적별"]
    value_vars = df.columns.difference(id_vars)
    df_long = df.melt(id_vars=id_vars, value_vars=value_vars, var_name="시점_원본", value_name="값")

    df_long["연도"] = df_long["시점_원본"].str.extract(r"(\d{4})")
    df_long["구분"] = df_long["시점_원본"].apply(lambda x: "소비자물가지수" if "전년" not in x else "전년_대비_증감률")
    df_pivot = df_long.pivot_table(index=["시도별", "지출목적별", "연도"], columns="구분", values="값", aggfunc="first").reset_index()

    df_pivot["소비자물가지수"] = pd.to_numeric(df_pivot["소비자물가지수"], errors="coerce")
    df_pivot["전년_대비_증감률"] = pd.to_numeric(df_pivot["전년_대비_증감률"], errors="coerce")
    return df_pivot

df = load_data()

# -------------------------------
# 사이드바 필터 설정
# -------------------------------
st.sidebar.header("🔎 필터 설정")
available_categories = sorted([c for c in df["지출목적별"].unique() if "지출목적별" not in c])
selected_category = st.sidebar.selectbox("지출 항목 선택", available_categories)

years = sorted(df["연도"].dropna().unique())
start_year, end_year = st.sidebar.select_slider("연도 범위", options=years, value=(years[0], years[-1]))

df_filtered = df[
    (df["지출목적별"] == selected_category) &
    (df["연도"] >= start_year) &
    (df["연도"] <= end_year)
]

# -------------------------------
# 최고/최저 변화율 지점 표시
# -------------------------------
df_notna = df_filtered.dropna(subset=["전년_대비_증감률"])
max_row = df_notna.loc[df_notna["전년_대비_증감률"].idxmax()]
min_row = df_notna.loc[df_notna["전년_대비_증감률"].idxmin()]

st.subheader("📌 변화율이 가장 큰 시점")
col1, col2 = st.columns(2)
with col1:
    st.markdown(f"#### 🔺 상승률 최고")
    st.metric(label=f"{max_row['연도']}년", value=f"{max_row['전년_대비_증감률']}%", delta=f"{max_row['소비자물가지수']}")
with col2:
    st.markdown(f"#### 🔻 하락률 최저")
    st.metric(label=f"{min_row['연도']}년", value=f"{min_row['전년_대비_증감률']}%", delta=f"{min_row['소비자물가지수']}")

# -------------------------------
# 그래프 시각화 (Altair)
# -------------------------------
st.subheader("📈 소비자물가지수 & 전년 대비 증감률")

df_plot = df_filtered.copy()
df_plot["표시용연도"] = df_plot["연도"] + "년"

line_cpi = alt.Chart(df_plot).mark_line(color="green", strokeWidth=3).encode(
    x=alt.X("연도:O", title="연도", labelAngle=0),
    y=alt.Y("소비자물가지수:Q", title="지수"),
    tooltip=["표시용연도", alt.Tooltip("소비자물가지수:Q", title="지수")]
)

point_cpi = alt.Chart(df_plot).mark_point(color="green", size=40, filled=True).encode(
    x=alt.X("연도:O", labelAngle=0),
    y="소비자물가지수:Q",
    tooltip=["표시용연도", alt.Tooltip("소비자물가지수:Q", title="지수")]
)

line_rate = alt.Chart(df_plot).mark_line(color="blue", strokeDash=[0], strokeWidth=2).encode(
    x=alt.X("연도:O", labelAngle=0),
    y=alt.Y("전년_대비_증감률:Q", title="전년 대비 증감률 (%)"),
    tooltip=["표시용연도", alt.Tooltip("전년_대비_증감률:Q", title="전년 대비")]
)

point_rate = alt.Chart(df_plot).mark_point(color="blue", size=40, filled=True).encode(
    x=alt.X("연도:O", labelAngle=0),
    y="전년_대비_증감률:Q",
    tooltip=["표시용연도", alt.Tooltip("전년_대비_증감률:Q", title="전년 대비")]
)

chart = alt.layer(line_cpi + point_cpi, line_rate + point_rate).resolve_scale(y='independent')
st.altair_chart(chart, use_container_width=True)
