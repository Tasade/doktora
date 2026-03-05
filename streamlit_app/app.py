import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

# ── Sayfa yapılandırması ──────────────────────────────────────────────────────
st.set_page_config(
    page_title="Kuzu Takip Paneli",
    page_icon="🐑",
    layout="wide",
)

# ── Veri yükleme ──────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "scripts", "temiz_veri.csv")


@st.cache_data
def veri_yukle():
    df = pd.read_csv(DATA_PATH, encoding="utf-8-sig")
    df["Dogum_Tarihi"] = pd.to_datetime(df["Dogum_Tarihi"])
    df["Ikinci_Ay_Tartim_Tarihi"] = pd.to_datetime(df["Ikinci_Ay_Tartim_Tarihi"])
    return df


df = veri_yukle()

# ── Başlık ─────────────────────────────────────────────────────────────────────
st.title("🐑 Kıvırcık Kuzu Takip Paneli")
st.caption("Kırklareli İli — Ahmet Uçak  |  Kayıt yılı: 2012")

# ── Kenar çubuğu filtreleri ───────────────────────────────────────────────────
with st.sidebar:
    st.header("🔍 Filtreler")

    cinsiyet_sec = st.multiselect(
        "Cinsiyet",
        options=df["Cinsiyet"].unique().tolist(),
        default=df["Cinsiyet"].unique().tolist(),
    )

    dogum_tipi_sec = st.multiselect(
        "Doğum Tipi",
        options=df["Dogum_Tipi"].unique().tolist(),
        default=df["Dogum_Tipi"].unique().tolist(),
    )

    min_ag, max_ag = float(df["Dogum_Agirligi_kg"].min()), float(df["Dogum_Agirligi_kg"].max())
    agirlik_aralik = st.slider(
        "Doğum Ağırlığı (kg)",
        min_value=min_ag,
        max_value=max_ag,
        value=(min_ag, max_ag),
        step=0.1,
    )

filtrelenmis = df[
    df["Cinsiyet"].isin(cinsiyet_sec)
    & df["Dogum_Tipi"].isin(dogum_tipi_sec)
    & df["Dogum_Agirligi_kg"].between(*agirlik_aralik)
]

# ── Özet metrikler ─────────────────────────────────────────────────────────────
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Toplam Kuzu", len(filtrelenmis))
c2.metric("Erkek", int((filtrelenmis["Cinsiyet"] == "Erkek").sum()))
c3.metric("Dişi", int((filtrelenmis["Cinsiyet"] == "Dişi").sum()))
c4.metric(
    "Ort. Doğum Ağırlığı",
    f"{filtrelenmis['Dogum_Agirligi_kg'].mean():.2f} kg",
)
c5.metric(
    "Ort. 2. Ay Ağırlığı",
    f"{filtrelenmis['Ikinci_Ay_Agirligi_kg'].mean():.2f} kg",
)

st.divider()

# ── Grafikler ──────────────────────────────────────────────────────────────────
col1, col2 = st.columns(2)

with col1:
    st.subheader("Cinsiyete Göre Ağırlık Dağılımı")
    fig1 = px.box(
        filtrelenmis,
        x="Cinsiyet",
        y="Ikinci_Ay_Agirligi_kg",
        color="Cinsiyet",
        points="all",
        color_discrete_map={"Erkek": "#4C78A8", "Dişi": "#F58518"},
        labels={"Ikinci_Ay_Agirligi_kg": "2. Ay Ağırlığı (kg)"},
    )
    fig1.update_layout(showlegend=False)
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.subheader("Doğum Tipine Göre Ortalama Ağırlıklar")
    ort = (
        filtrelenmis.groupby("Dogum_Tipi")[["Dogum_Agirligi_kg", "Ikinci_Ay_Agirligi_kg"]]
        .mean()
        .reset_index()
    )
    fig2 = px.bar(
        ort.melt(id_vars="Dogum_Tipi", var_name="Ölçüm", value_name="kg"),
        x="Dogum_Tipi",
        y="kg",
        color="Ölçüm",
        barmode="group",
        labels={"Dogum_Tipi": "Doğum Tipi", "kg": "Ağırlık (kg)"},
        color_discrete_sequence=["#72B7B2", "#FF9DA7"],
    )
    st.plotly_chart(fig2, use_container_width=True)

col3, col4 = st.columns(2)

with col3:
    st.subheader("Günlük Ağırlık Kazanımı (g/gün)")
    fig3 = px.histogram(
        filtrelenmis.dropna(subset=["Gunluk_Kazanim_g"]),
        x="Gunluk_Kazanim_g",
        color="Cinsiyet",
        nbins=20,
        barmode="overlay",
        opacity=0.75,
        color_discrete_map={"Erkek": "#4C78A8", "Dişi": "#F58518"},
        labels={"Gunluk_Kazanim_g": "Günlük Kazanım (g/gün)"},
    )
    st.plotly_chart(fig3, use_container_width=True)

with col4:
    st.subheader("Doğum Tarihine Göre Kuzu Sayısı")
    gunluk = filtrelenmis.groupby("Dogum_Tarihi").size().reset_index(name="Adet")
    fig4 = px.bar(
        gunluk,
        x="Dogum_Tarihi",
        y="Adet",
        labels={"Dogum_Tarihi": "Doğum Tarihi", "Adet": "Kuzu Sayısı"},
        color_discrete_sequence=["#54A24B"],
    )
    st.plotly_chart(fig4, use_container_width=True)

st.divider()

# ── Doğum ağırlığı vs 2. ay ağırlığı scatter ──────────────────────────────────
st.subheader("Doğum Ağırlığı → 2. Ay Ağırlığı İlişkisi")
fig5 = px.scatter(
    filtrelenmis.dropna(subset=["Dogum_Agirligi_kg", "Ikinci_Ay_Agirligi_kg"]),
    x="Dogum_Agirligi_kg",
    y="Ikinci_Ay_Agirligi_kg",
    color="Cinsiyet",
    symbol="Dogum_Tipi",
    hover_data=["Kuzu_Kupe_No", "Ana_Kupe_No"],
    trendline="ols",
    color_discrete_map={"Erkek": "#4C78A8", "Dişi": "#F58518"},
    labels={
        "Dogum_Agirligi_kg": "Doğum Ağırlığı (kg)",
        "Ikinci_Ay_Agirligi_kg": "2. Ay Ağırlığı (kg)",
    },
)
st.plotly_chart(fig5, use_container_width=True)

# ── Ham veri tablosu ──────────────────────────────────────────────────────────
with st.expander("📋 Filtrelenmiş Ham Veri"):
    st.dataframe(filtrelenmis.reset_index(drop=True), use_container_width=True)
