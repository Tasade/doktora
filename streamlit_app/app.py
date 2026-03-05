import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

# ─────────────────────────────────────────────
#  SAYFA AYARLARI  (ilk st.* çağrısı olmalı)
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Kuzu Takip Paneli",
    page_icon="🐑",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
#  HAM VERİYİ BUL VE TEMİZLE (dışarıya bağımlılık yok)
# ─────────────────────────────────────────────
APP_DIR  = os.path.dirname(os.path.abspath(__file__))  # streamlit_app/
BASE_DIR = os.path.dirname(APP_DIR)                     # proje kökü

# Ham CSV'yi data/ klasöründe ara
HAM_CSV = os.path.join(BASE_DIR, "data", "Ahmet_Uçak_Kuzu_Listesi.csv")


def kg_temizle(deger):
    if pd.isna(deger):
        return None
    d = str(deger).strip().lower().replace(" kg", "").replace(",", ".")
    if d in ["öldü", "ölü", "-", "", "nan"]:
        return None
    try:
        return float(d)
    except ValueError:
        return None


def tarih_temizle(deger):
    if pd.isna(deger):
        return None
    try:
        return pd.to_datetime(str(deger).strip(), dayfirst=True)
    except Exception:
        return None


@st.cache_data
def veri_yukle():
    df = pd.read_csv(
        HAM_CSV,
        sep=";",
        skiprows=4,
        encoding="utf-8-sig",
        on_bad_lines="skip",
    )
    df.columns = [
        "Sira_No", "Kuzu_Kupe_No", "Turkvet_Kupe_No", "Ana_Kupe_No",
        "Dogum_Tarihi", "Cinsiyet", "Dogum_Tipi",
        "Dogum_Agirligi_kg", "Ikinci_Ay_Agirligi_kg", "Ikinci_Ay_Tartim_Tarihi",
    ]
    # Sadece sayısal sıra no'lu satırlar
    df = df[pd.to_numeric(df["Sira_No"], errors="coerce").notna()].copy()
    df["Sira_No"] = df["Sira_No"].astype(int)

    # Temizle
    df["Dogum_Agirligi_kg"]      = df["Dogum_Agirligi_kg"].apply(kg_temizle)
    df["Ikinci_Ay_Agirligi_kg"]  = df["Ikinci_Ay_Agirligi_kg"].apply(kg_temizle)
    df["Dogum_Tarihi"]           = df["Dogum_Tarihi"].apply(tarih_temizle)
    df["Ikinci_Ay_Tartim_Tarihi"]= df["Ikinci_Ay_Tartim_Tarihi"].apply(tarih_temizle)

    for col in ["Kuzu_Kupe_No", "Turkvet_Kupe_No", "Ana_Kupe_No", "Cinsiyet", "Dogum_Tipi"]:
        df[col] = df[col].astype(str).str.strip().replace("nan", "")

    # Günlük kazanım
    df["Gunluk_Kazanim_g"] = (
        (df["Ikinci_Ay_Agirligi_kg"] - df["Dogum_Agirligi_kg"]) * 1000 / 60
    ).round(1)

    return df


try:
    df = veri_yukle()
except FileNotFoundError:
    st.error(f"Ham veri dosyası bulunamadı:\n`{HAM_CSV}`\n\nLütfen `data/` klasöründe dosyanın var olduğunu kontrol edin.")
    st.stop()

# ─────────────────────────────────────────────
#  ÖZEL CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=Source+Sans+3:wght@400;600&display=swap');

[data-testid="stAppViewContainer"] { background: #f5f0e8; }
[data-testid="stSidebar"] { background: #2d4a22 !important; }
[data-testid="stSidebar"] * { color: #e8dfc8 !important; }
[data-testid="stSidebar"] .stMultiSelect [data-baseweb="tag"] {
    background-color: #5a8a3c !important;
}

.hero-title {
    font-family: 'Playfair Display', serif;
    font-size: 2.6rem; color: #2d4a22;
    line-height: 1.15; margin-bottom: 0;
}
.hero-sub {
    font-family: 'Source Sans 3', sans-serif;
    font-size: 1rem; color: #6b7c5a;
    margin-top: 4px; letter-spacing: 0.04em;
}
.metric-card {
    background: #ffffff; border-radius: 12px;
    padding: 18px 20px;
    box-shadow: 0 2px 8px rgba(45,74,34,0.08);
    border-left: 4px solid #5a8a3c;
    font-family: 'Source Sans 3', sans-serif;
    margin-bottom: 6px;
}
.metric-label {
    font-size: 0.78rem; color: #6b7c5a;
    text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 6px;
}
.metric-value {
    font-family: 'Playfair Display', serif;
    font-size: 2rem; color: #2d4a22; line-height: 1;
}
.metric-sub { font-size: 0.75rem; color: #a0a896; margin-top: 4px; }
.section-title {
    font-family: 'Playfair Display', serif;
    font-size: 1.25rem; color: #2d4a22;
    border-bottom: 2px solid #c8d9b0;
    padding-bottom: 6px; margin-bottom: 12px; margin-top: 4px;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  RENK PALETİ & TEMA
# ─────────────────────────────────────────────
RENKLER = {
    "Erkek": "#2d7d46", "Dişi": "#c07038",
    "Tek": "#5a8a3c", "İkiz": "#e08c3a", "Üçüz": "#9b59b6",
}
TEMA = dict(
    plot_bgcolor="#ffffff", paper_bgcolor="#ffffff",
    font_family="Times New Roman", font_color="#000000",
    xaxis=dict(showgrid=True, gridcolor="#eeebe4", linecolor="#ddd",
               tickfont=dict(family="Times New Roman", color="#000000"),
               title_font=dict(family="Times New Roman", color="#000000")),
    yaxis=dict(showgrid=True, gridcolor="#eeebe4", linecolor="#ddd",
               tickfont=dict(family="Times New Roman", color="#000000"),
               title_font=dict(family="Times New Roman", color="#000000")),
)

# ─────────────────────────────────────────────
#  KENAR ÇUBUĞU FİLTRELER
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🔍 Filtreler")
    st.markdown("---")
    cinsiyet_sec = st.multiselect(
        "Cinsiyet",
        options=sorted(df["Cinsiyet"].replace("", pd.NA).dropna().unique()),
        default=sorted(df["Cinsiyet"].replace("", pd.NA).dropna().unique()),
    )
    dogum_tipi_sec = st.multiselect(
        "Doğum Tipi",
        options=sorted(df["Dogum_Tipi"].replace("", pd.NA).dropna().unique()),
        default=sorted(df["Dogum_Tipi"].replace("", pd.NA).dropna().unique()),
    )
    min_ag = float(df["Dogum_Agirligi_kg"].min())
    max_ag = float(df["Dogum_Agirligi_kg"].max())
    agirlik_aralik = st.slider(
        "Doğum Ağırlığı (kg)",
        min_value=min_ag, max_value=max_ag,
        value=(min_ag, max_ag), step=0.1,
    )
    st.markdown("---")
    st.markdown(
        "<div style='font-size:0.78rem;opacity:0.7'>Kırklareli İli · Kıvırcık Irk<br>"
        "Ahmet Uçak · Düzorman · 2012</div>",
        unsafe_allow_html=True,
    )

# Filtre uygula
fdf = df[
    df["Cinsiyet"].isin(cinsiyet_sec) &
    df["Dogum_Tipi"].isin(dogum_tipi_sec) &
    df["Dogum_Agirligi_kg"].between(*agirlik_aralik)
].copy()

# ─────────────────────────────────────────────
#  BAŞLIK
# ─────────────────────────────────────────────
st.markdown(
    '<div class="hero-title">🐑 Kıvırcık Kuzu Takip Paneli</div>'
    '<div class="hero-sub">Kırklareli İli Halk Elinde Islah Projesi — Ahmet Uçak · Düzorman</div>',
    unsafe_allow_html=True,
)
st.markdown("<br>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  METRİK KARTLAR
# ─────────────────────────────────────────────
erkek_n = int((fdf["Cinsiyet"] == "Erkek").sum())
disi_n  = int((fdf["Cinsiyet"] == "Dişi").sum())
ort_dog = fdf["Dogum_Agirligi_kg"].mean()
ort_2ay = fdf["Ikinci_Ay_Agirligi_kg"].mean()
ort_kaz = fdf["Gunluk_Kazanim_g"].mean()
olum_n  = int(fdf["Ikinci_Ay_Agirligi_kg"].isna().sum())

def kart(col, label, value, sub=""):
    col.markdown(
        f'<div class="metric-card">'
        f'<div class="metric-label">{label}</div>'
        f'<div class="metric-value">{value}</div>'
        f'<div class="metric-sub">{sub}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

c1, c2, c3, c4, c5, c6 = st.columns(6)
kart(c1, "Toplam Kuzu", len(fdf), f"{erkek_n} erkek · {disi_n} dişi")
kart(c2, "Erkek", erkek_n, f"%{erkek_n/len(fdf)*100:.0f}" if len(fdf) else "—")
kart(c3, "Dişi", disi_n,   f"%{disi_n/len(fdf)*100:.0f}" if len(fdf) else "—")
kart(c4, "Ort. Doğum Ağırlığı", f"{ort_dog:.2f} kg", "tüm kuzular")
kart(c5, "Ort. 2. Ay Ağırlığı", f"{ort_2ay:.2f} kg" if not pd.isna(ort_2ay) else "—", "60. gün")
kart(c6, "Günlük Kazanım", f"{ort_kaz:.0f} g/gün" if not pd.isna(ort_kaz) else "—", f"{olum_n} ölüm kaydı")

st.markdown("<br>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  BÖLÜM 1: Ağırlık dağılımları
# ─────────────────────────────────────────────
st.markdown('<div class="section-title">Ağırlık Dağılımları</div>', unsafe_allow_html=True)
col1, col2 = st.columns(2)

with col1:
    fig = go.Figure()
    for cins in ["Erkek", "Dişi"]:
        veri = fdf[fdf["Cinsiyet"] == cins]["Ikinci_Ay_Agirligi_kg"].dropna()
        fig.add_trace(go.Violin(
            y=veri, name=cins, box_visible=True, meanline_visible=True,
            points="all", jitter=0.3, pointpos=-1.6,
            marker=dict(size=4, opacity=0.5),
            fillcolor=RENKLER[cins], line_color=RENKLER[cins], opacity=0.75,
        ))
    fig.update_layout(**TEMA, title="Cinsiyete Göre 2. Ay Ağırlığı",
                      yaxis_title="2. Ay Ağırlığı (kg)", height=380)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    fig = px.histogram(
        fdf, x="Dogum_Agirligi_kg", color="Cinsiyet",
        nbins=16, barmode="overlay", opacity=0.75,
        color_discrete_map=RENKLER,
        labels={"Dogum_Agirligi_kg": "Doğum Ağırlığı (kg)", "count": "Kuzu Sayısı"},
        title="Doğum Ağırlığı Dağılımı",
    )
    fig.update_layout(**TEMA, height=380)
    st.plotly_chart(fig, use_container_width=True)

# ─────────────────────────────────────────────
#  BÖLÜM 2: Karşılaştırmalı analizler
# ─────────────────────────────────────────────
st.markdown('<div class="section-title">Doğum Tipi Karşılaştırması</div>', unsafe_allow_html=True)
col3, col4 = st.columns(2)

with col3:
    ort = (
        fdf.groupby("Dogum_Tipi")[["Dogum_Agirligi_kg", "Ikinci_Ay_Agirligi_kg"]]
        .mean().reset_index()
    )
    ort_melt = ort.melt(id_vars="Dogum_Tipi", var_name="Ölçüm", value_name="kg")
    ort_melt["Ölçüm"] = ort_melt["Ölçüm"].map({
        "Dogum_Agirligi_kg": "Doğum",
        "Ikinci_Ay_Agirligi_kg": "2. Ay (60. gün)",
    })
    fig = px.bar(
        ort_melt, x="Dogum_Tipi", y="kg", color="Ölçüm",
        barmode="group", text_auto=".2f",
        color_discrete_sequence=["#5a8a3c", "#e08c3a"],
        labels={"Dogum_Tipi": "Doğum Tipi", "kg": "Ort. Ağırlık (kg)"},
        title="Doğum Tipine Göre Ortalama Ağırlık",
    )
    fig.update_traces(textposition="outside", textfont_size=11)
    fig.update_layout(**TEMA, height=370)
    st.plotly_chart(fig, use_container_width=True)

with col4:
    pivot = fdf.groupby(["Dogum_Tipi", "Cinsiyet"]).size().unstack(fill_value=0)
    fig = px.imshow(
        pivot, text_auto=True,
        color_continuous_scale=["#f5f0e8", "#2d4a22"],
        title="Doğum Tipi × Cinsiyet Isı Haritası",
        labels={"x": "Cinsiyet", "y": "Doğum Tipi", "color": "Sayı"},
        aspect="auto",
    )
    fig.update_layout(**TEMA, height=370, coloraxis_showscale=False)
    st.plotly_chart(fig, use_container_width=True)

# ─────────────────────────────────────────────
#  BÖLÜM 3: Zaman serisi
# ─────────────────────────────────────────────
st.markdown('<div class="section-title">Zaman İçinde Doğumlar</div>', unsafe_allow_html=True)
col5, col6 = st.columns([2, 1])

with col5:
    gunluk = fdf.groupby(["Dogum_Tarihi", "Cinsiyet"]).size().reset_index(name="Adet")
    fig = px.bar(
        gunluk, x="Dogum_Tarihi", y="Adet", color="Cinsiyet",
        color_discrete_map=RENKLER,
        labels={"Dogum_Tarihi": "Doğum Tarihi", "Adet": "Kuzu Sayısı"},
        title="Güne Göre Doğum Sayısı",
    )
    fig.update_layout(**TEMA, height=340, bargap=0.15)
    st.plotly_chart(fig, use_container_width=True)

with col6:
    tip_say = fdf["Dogum_Tipi"].value_counts().reset_index()
    tip_say.columns = ["Doğum Tipi", "Adet"]
    fig = px.pie(
        tip_say, values="Adet", names="Doğum Tipi",
        color="Doğum Tipi",
        color_discrete_map={"Tek": "#5a8a3c", "İkiz": "#e08c3a", "Üçüz": "#9b59b6"},
        title="Doğum Tipi Oranı", hole=0.45,
    )
    fig.update_traces(textinfo="percent+label", textfont_size=13)
    fig.update_layout(**TEMA, height=340, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

# ─────────────────────────────────────────────
#  BÖLÜM 4: Büyüme & kazanım analizi
# ─────────────────────────────────────────────
st.markdown('<div class="section-title">Büyüme & Kazanım Analizi</div>', unsafe_allow_html=True)
col7, col8 = st.columns(2)

scatter_df = fdf.dropna(subset=["Dogum_Agirligi_kg", "Ikinci_Ay_Agirligi_kg"])

with col7:
    fig = px.scatter(
        scatter_df,
        x="Dogum_Agirligi_kg", y="Ikinci_Ay_Agirligi_kg",
        color="Cinsiyet", symbol="Dogum_Tipi",
        trendline="ols", color_discrete_map=RENKLER,
        hover_data=["Kuzu_Kupe_No", "Ana_Kupe_No", "Gunluk_Kazanim_g"],
        labels={
            "Dogum_Agirligi_kg": "Doğum Ağırlığı (kg)",
            "Ikinci_Ay_Agirligi_kg": "2. Ay Ağırlığı (kg)",
        },
        title="Doğum → 2. Ay Ağırlığı (Trend Çizgili)",
    )
    fig.update_traces(marker=dict(size=7, opacity=0.75), selector=dict(mode="markers"))
    fig.update_layout(**TEMA, height=380)
    st.plotly_chart(fig, use_container_width=True)

with col8:
    kaz_df = fdf.dropna(subset=["Gunluk_Kazanim_g"])
    fig = px.box(
        kaz_df, x="Cinsiyet", y="Gunluk_Kazanim_g",
        color="Cinsiyet", facet_col="Dogum_Tipi",
        points="all", color_discrete_map=RENKLER,
        labels={"Gunluk_Kazanim_g": "Günlük Kazanım (g/gün)", "Cinsiyet": ""},
        title="Günlük Kazanım: Cinsiyet × Doğum Tipi",
    )
    fig.update_layout(**TEMA, height=380, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

# ─────────────────────────────────────────────
#  BÖLÜM 5: Ana bazlı performans
# ─────────────────────────────────────────────
st.markdown('<div class="section-title">Ana Bazlı Büyüme Performansı</div>', unsafe_allow_html=True)

ana_df = (
    fdf[fdf["Ana_Kupe_No"].astype(str).str.strip().ne("")]
    .groupby("Ana_Kupe_No")
    .agg(
        Kuzu_Sayisi=("Sira_No", "count"),
        Ort_Dogum_Ag=("Dogum_Agirligi_kg", "mean"),
        Ort_2ay_Ag=("Ikinci_Ay_Agirligi_kg", "mean"),
        Ort_Kazanim=("Gunluk_Kazanim_g", "mean"),
    )
    .dropna(subset=["Ort_2ay_Ag"])
    .reset_index()
    .sort_values("Ort_2ay_Ag", ascending=False)
    .head(25)
)

fig = px.scatter(
    ana_df,
    x="Ort_Dogum_Ag", y="Ort_2ay_Ag",
    size="Kuzu_Sayisi", color="Ort_Kazanim",
    hover_name="Ana_Kupe_No",
    hover_data={"Kuzu_Sayisi": True, "Ort_Kazanim": ":.1f"},
    color_continuous_scale=["#c8d9b0", "#2d4a22"],
    size_max=25,
    labels={
        "Ort_Dogum_Ag": "Ort. Doğum Ağırlığı (kg)",
        "Ort_2ay_Ag": "Ort. 2. Ay Ağırlığı (kg)",
        "Ort_Kazanim": "Günlük Kazanım (g/gün)",
        "Kuzu_Sayisi": "Kuzu Sayısı",
    },
    title="En İyi 25 Ana — Daire büyüklüğü: kuzu sayısı · Renk: günlük kazanım",
)
fig.update_layout(**TEMA, height=400, coloraxis_colorbar=dict(title="g/gün"))
st.plotly_chart(fig, use_container_width=True)

# ─────────────────────────────────────────────
#  HAM VERİ TABLOSU
# ─────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
with st.expander("📋 Filtrelenmiş Veri Tablosu"):
    gorunen = fdf[[
        "Sira_No", "Kuzu_Kupe_No", "Ana_Kupe_No",
        "Dogum_Tarihi", "Cinsiyet", "Dogum_Tipi",
        "Dogum_Agirligi_kg", "Ikinci_Ay_Agirligi_kg", "Gunluk_Kazanim_g",
    ]].rename(columns={
        "Sira_No": "Sıra", "Kuzu_Kupe_No": "Küpe No", "Ana_Kupe_No": "Ana Küpe",
        "Dogum_Tarihi": "Doğum Tarihi", "Cinsiyet": "Cinsiyet", "Dogum_Tipi": "Doğum Tipi",
        "Dogum_Agirligi_kg": "Doğum Ağ. (kg)", "Ikinci_Ay_Agirligi_kg": "2. Ay Ağ. (kg)",
        "Gunluk_Kazanim_g": "Günlük Kaz. (g)",
    })
    st.dataframe(gorunen.reset_index(drop=True), use_container_width=True, height=350)
    st.caption(f"Toplam {len(gorunen)} kayıt gösteriliyor.")
