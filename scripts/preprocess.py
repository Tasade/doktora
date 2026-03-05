import pandas as pd
import re
import os

# Yollar
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INPUT_PATH = os.path.join(BASE_DIR, "data", "Ahmet_Uçak_Kuzu_Listesi.csv")
OUTPUT_PATH = os.path.join(BASE_DIR, "scripts", "temiz_veri.csv")


def kg_temizle(deger):
    """'3,1 kg' gibi değerleri float'a çevirir. 'öldü' gibi değerleri NaN yapar."""
    if pd.isna(deger):
        return None
    deger = str(deger).strip().lower()
    if deger in ["öldü", "ölü", "-", ""]:
        return None
    deger = deger.replace(" kg", "").replace(",", ".")
    try:
        return float(deger)
    except ValueError:
        return None


def tarih_temizle(deger):
    """Çeşitli tarih formatlarını standart YYYY-MM-DD'ye çevirir."""
    if pd.isna(deger):
        return None
    try:
        return pd.to_datetime(str(deger).strip(), dayfirst=True).strftime("%Y-%m-%d")
    except Exception:
        return None


def main():
    print("Ham veri okunuyor...")

    # İlk 4 satır başlık/meta bilgisi — atla, gerçek başlık 5. satırda
    df = pd.read_csv(
        INPUT_PATH,
        sep=";",
        skiprows=4,
        encoding="utf-8-sig",
        on_bad_lines="skip",
    )

    # Sütun isimlerini temizle
    df.columns = [
        "Sira_No",
        "Kuzu_Kupe_No",
        "Turkvet_Kupe_No",
        "Ana_Kupe_No",
        "Dogum_Tarihi",
        "Cinsiyet",
        "Dogum_Tipi",
        "Dogum_Agirligi_kg",
        "Ikinci_Ay_Agirligi_kg",
        "Ikinci_Ay_Tartim_Tarihi",
    ]

    # Boş / anlamsız satırları at (Sira_No sayısal olmayan satırlar)
    df = df[pd.to_numeric(df["Sira_No"], errors="coerce").notna()].copy()
    df["Sira_No"] = df["Sira_No"].astype(int)

    # Ağırlık sütunlarını temizle
    df["Dogum_Agirligi_kg"] = df["Dogum_Agirligi_kg"].apply(kg_temizle)
    df["Ikinci_Ay_Agirligi_kg"] = df["Ikinci_Ay_Agirligi_kg"].apply(kg_temizle)

    # Tarih sütunlarını standartlaştır
    df["Dogum_Tarihi"] = df["Dogum_Tarihi"].apply(tarih_temizle)
    df["Ikinci_Ay_Tartim_Tarihi"] = df["Ikinci_Ay_Tartim_Tarihi"].apply(tarih_temizle)

    # Metin sütunlarını trim'le
    for col in ["Kuzu_Kupe_No", "Turkvet_Kupe_No", "Ana_Kupe_No", "Cinsiyet", "Dogum_Tipi"]:
        df[col] = df[col].astype(str).str.strip().replace("nan", "")

    # Günlük ağırlık kazanımı hesapla
    df["Gunluk_Kazanim_g"] = (
        (df["Ikinci_Ay_Agirligi_kg"] - df["Dogum_Agirligi_kg"]) * 1000 / 60
    ).round(1)

    print(f"Temizlenen kayıt sayısı: {len(df)}")
    print(df.dtypes)

    df.to_csv(OUTPUT_PATH, index=False, encoding="utf-8-sig")
    print(f"Temiz veri kaydedildi: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
    # İlk 4 satır başlık/meta bilgisi — atla, gerçek başlık 5. satırda
    df = pd.read_csv(
        INPUT_PATH,
        sep=";",
        skiprows=4,
        encoding="utf-8-sig",
        on_bad_lines="skip",
    )

    # Sütun isimlerini temizle
    df.columns = [
        "Sira_No",
        "Kuzu_Kupe_No",
        "Turkvet_Kupe_No",
        "Ana_Kupe_No",
        "Dogum_Tarihi",
        "Cinsiyet",
        "Dogum_Tipi",
        "Dogum_Agirligi_kg",
        "Ikinci_Ay_Agirligi_kg",
        "Ikinci_Ay_Tartim_Tarihi",
    ]

    # Boş / anlamsız satırları at (Sira_No sayısal olmayan satırlar)
    df = df[pd.to_numeric(df["Sira_No"], errors="coerce").notna()].copy()
    df["Sira_No"] = df["Sira_No"].astype(int)

    # Ağırlık sütunlarını temizle
    df["Dogum_Agirligi_kg"] = df["Dogum_Agirligi_kg"].apply(kg_temizle)
    df["Ikinci_Ay_Agirligi_kg"] = df["Ikinci_Ay_Agirligi_kg"].apply(kg_temizle)

    # Tarih sütunlarını standartlaştır
    df["Dogum_Tarihi"] = df["Dogum_Tarihi"].apply(tarih_temizle)
    df["Ikinci_Ay_Tartim_Tarihi"] = df["Ikinci_Ay_Tartim_Tarihi"].apply(tarih_temizle)

    # Metin sütunlarını trim'le
    for col in ["Kuzu_Kupe_No", "Turkvet_Kupe_No", "Ana_Kupe_No", "Cinsiyet", "Dogum_Tipi"]:
        df[col] = df[col].astype(str).str.strip().replace("nan", "")

    # Günlük ağırlık kazanımı hesapla
    df["Gunluk_Kazanim_g"] = (
        (df["Ikinci_Ay_Agirligi_kg"] - df["Dogum_Agirligi_kg"]) * 1000 / 60
    ).round(1)

    print(f"Temizlenen kayıt sayısı: {len(df)}")
    print(df.dtypes)

    df.to_csv(OUTPUT_PATH, index=False, encoding="utf-8-sig")
    print(f"Temiz veri kaydedildi: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
