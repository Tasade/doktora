import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

st.title("Kuzu Büyüme Analizi Dashboard")

df = pd.read_csv("data/kuzu_clean.csv")

st.header("Veri Seti")
st.dataframe(df)

st.header("Temel İstatistikler")
st.write(df.describe())

# -----------------------------
# Doğum Ağırlığı Dağılımı
# -----------------------------

st.subheader("Doğum Ağırlığı Dağılımı")

fig, ax = plt.subplots()

sns.histplot(df["dogum_agirligi"], kde=True, ax=ax)

st.pyplot(fig)

# -----------------------------
# 2.Ay Ağırlığı
# -----------------------------

st.subheader("2. Ay Ağırlık Dağılımı")

fig, ax = plt.subplots()

sns.histplot(df["ay2_agirligi"], kde=True, ax=ax)

st.pyplot(fig)

# -----------------------------
# Growth Relationship
# -----------------------------

st.subheader("Doğum Ağırlığı vs 2.Ay Ağırlığı")

fig, ax = plt.subplots()

sns.scatterplot(
    x=df["dogum_agirligi"],
    y=df["ay2_agirligi"]
)

st.pyplot(fig)

# -----------------------------
# Cinsiyet Etkisi
# -----------------------------

st.subheader("Cinsiyete Göre 2.Ay Ağırlık")

fig, ax = plt.subplots()

sns.boxplot(
    x="cinsiyet",
    y="ay2_agirligi",
    data=df
)

st.pyplot(fig)

# -----------------------------
# Doğum Tipi Etkisi
# -----------------------------

st.subheader("Doğum Tipine Göre 2.Ay Ağırlık")

fig, ax = plt.subplots()

sns.boxplot(
    x="dogum_tipi",
    y="ay2_agirligi",
    data=df
)

st.pyplot(fig)

# -----------------------------
# ADG Analizi
# -----------------------------

st.subheader("Günlük Canlı Ağırlık Artışı (ADG)")

fig, ax = plt.subplots()

sns.histplot(df["gunluk_agirlik_artisi"], kde=True)

st.pyplot(fig)

# -----------------------------
# Korelasyon
# -----------------------------

st.subheader("Korelasyon Matrisi")

corr = df[
["dogum_agirligi","ay2_agirligi","gunluk_agirlik_artisi"]
].corr()

fig, ax = plt.subplots()

sns.heatmap(corr, annot=True)

st.pyplot(fig)
