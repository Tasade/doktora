import pandas as pd
import numpy as np

df = pd.read_csv("data/kuzu_listesi.csv", sep=";", engine="python")

# header temizleme
df.columns = df.iloc[3]
df = df.drop([0,1,2,3]).reset_index(drop=True)

df.columns = [
"sira_no",
"kuzu_kupeno",
"turkvet_no",
"ana_kupeno",
"dogum_tarihi",
"cinsiyet",
"dogum_tipi",
"dogum_agirligi",
"ay2_agirligi",
"tartim_tarihi"
]

# tarih dönüşümü
df["dogum_tarihi"] = pd.to_datetime(df["dogum_tarihi"], dayfirst=True)
df["tartim_tarihi"] = pd.to_datetime(df["tartim_tarihi"], dayfirst=True)

# ağırlık temizleme
df["dogum_agirligi"] = (
    df["dogum_agirligi"]
    .str.replace("kg","")
    .str.replace(",",".")
    .astype(float)
)

df["ay2_agirligi"] = (
    df["ay2_agirligi"]
    .str.replace("kg","")
    .str.replace(",",".")
    .astype(float)
)

# gün farkı
df["gun_sayisi"] = (df["tartim_tarihi"] - df["dogum_tarihi"]).dt.days

# ADG
df["gunluk_agirlik_artisi"] = (
    df["ay2_agirligi"] - df["dogum_agirligi"]
) / df["gun_sayisi"]

# eksik veri temizleme
df = df.dropna()

df.to_csv("data/kuzu_clean.csv", index=False)

print("Veri temizlendi")
