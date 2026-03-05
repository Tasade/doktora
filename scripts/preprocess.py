import pandas as pd
import numpy as np
from pathlib import Path

# Dosya yolları
base_path = Path(__file__).resolve().parent.parent

raw_data = base_path / "data" / "Ahmet Uçak Kuzu Listesi.csv"
clean_data = base_path / "scripts" / "kuzu_clean.csv"

# Veri yükleme
df = pd.read_csv(raw_data, sep=",", engine="python")

# kolon isimlerini temizleme
df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

# tarihleri düzeltme
df["doğum_tarihi"] = pd.to_datetime(df["doğum_tarihi"], errors="coerce")
df["2._ay_tartım_tarihi"] = pd.to_datetime(df["2._ay_tartım_tarihi"], errors="coerce")

# sayısal verileri temizleme
df["doğum_ağırlığı"] = pd.to_numeric(df["doğum_ağırlığı"], errors="coerce")
df["2._ay_ağırlığı"] = pd.to_numeric(df["2._ay_ağırlığı"], errors="coerce")

# gün farkı
df["gun_sayisi"] = (df["2._ay_tartım_tarihi"] - df["doğum_tarihi"]).dt.days

# growth metriği
df["gunluk_agirlik_artisi"] = (
    df["2._ay_ağırlığı"] - df["doğum_ağırlığı"]
) / df["gun_sayisi"]

# eksik veri temizleme
df = df.dropna()

# aykırı değer temizleme
from scipy.stats import zscore

df = df[(np.abs(zscore(df[["doğum_ağırlığı","2._ay_ağırlığı"]])) < 3).all(axis=1)]

# temiz veri kaydet
df.to_csv(clean_data, index=False)

print("Temiz veri kaydedildi:", clean_data)
