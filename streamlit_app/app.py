import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from pathlib import Path

st.title("Kuzu Büyüme Performansı Analizi")

# dosya yolu
base_path = Path(__file__).resolve().parent.parent
data_path = base_path / "scripts" / "kuzu_clean.csv"

# veri yükleme
df = pd.read_csv(data_path)

st.subheader("Veri Önizleme")
st.dataframe(df)

# temel istatistik
st.subheader("Temel İstatistikler")
st.write(df.describe())

# doğum ağırlığı dağılımı
st.subheader("Doğum Ağırlığı Dağılımı")

fig, ax = plt.subplots()
sns.histplot(df["doğum_ağırlığı"], kde=True, ax=ax)
st.pyplot(fig)

# 2. ay ağırlığı
st.subheader("2. Ay Ağırlığı Dağılımı")

fig, ax = plt.subplots()
sns.histplot(df["2._ay_ağırlığı"], kde=True, ax=ax)
st.pyplot(fig)

# büyüme ilişkisi
st.subheader("Doğum Ağırlığı vs 2. Ay Ağırlığı")

fig, ax = plt.subplots()
sns.scatterplot(
    x="doğum_ağırlığı",
    y="2._ay_ağırlığı",
    data=df,
    ax=ax
)
st.pyplot(fig)

# cinsiyet etkisi
st.subheader("Cinsiyet Etkisi")

fig, ax = plt.subplots()
sns.boxplot(
    x="cinsiyet",
    y="2._ay_ağırlığı",
    data=df,
    ax=ax
)
st.pyplot(fig)

# doğum tipi
st.subheader("Doğum Tipi Analizi")

fig, ax = plt.subplots()
sns.boxplot(
    x="doğum_tipi",
    y="2._ay_ağırlığı",
    data=df,
    ax=ax
)
st.pyplot(fig)

# ADG analizi
st.subheader("Günlük Ağırlık Artışı")

fig, ax = plt.subplots()
sns.histplot(df["gunluk_agirlik_artisi"], kde=True, ax=ax)
st.pyplot(fig)

# korelasyon
st.subheader("Korelasyon Matrisi")

corr = df[
["doğum_ağırlığı","2._ay_ağırlığı","gunluk_agirlik_artisi"]
].corr()

fig, ax = plt.subplots()
sns.heatmap(corr, annot=True, cmap="coolwarm", ax=ax)
st.pyplot(fig)
