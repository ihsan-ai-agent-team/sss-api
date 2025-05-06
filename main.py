# main.py
from fastapi import FastAPI, Query
from rapidfuzz import process, fuzz
import json, re, unicodedata, pathlib

app = FastAPI(title="SSS API", version="1.0")

# ---------- Yardımcı fonksiyonlar ----------
_TURKISH_MAP = str.maketrans("çğıöşü", "cgiosu")  # çok hafif transliterasyon

def normalize(text: str) -> str:
    """
    - Küçük harfe çevir
    - Türkçe özel harfleri mapping ile sadeleştir
    - Unicode normalizasyonu
    - Noktalama / fazla boşluk temizliği
    """
    text = text.lower().translate(_TURKISH_MAP)
    text = unicodedata.normalize("NFKD", text)
    text = re.sub(r"[^\w\s]", " ", text)      # noktalama → boşluk
    text = re.sub(r"\s+", " ", text).strip()  # çoklu boşluk temizle
    return text

# ---------- Veri yükleme ----------
json_path = pathlib.Path(__file__).with_name("sss.json")
with json_path.open(encoding="utf-8") as f:
    sss_raw = json.load(f)

# Normalize edilmiş soru listesi + indeks tut
questions_norm = [normalize(item["Soru"]) for item in sss_raw]

# RapidFuzz ayarları
THRESHOLD = 30           # 0-100 arası – düşürürseniz daha gevşek olur
SCORER   = fuzz.token_set_ratio  # kelime sırası / ek farklarını daha iyi tolere eder

# ---------- API ----------
@app.get("/", tags=["health"])
def health():
    return {"status": "ok"}

@app.get("/api/sss", tags=["faq"])
def get_faq(q: str = Query(..., description="Kullanıcının Türkçe sorusu")):
    q_norm = normalize(q)

    # En iyi 1 eşleşmeyi al (skor, index, …)
    match = process.extractOne(
        q_norm,
        questions_norm,
        scorer=SCORER,
        score_cutoff=THRESHOLD
    )

    if match:
        _, score, idx = match           # bize index ve skor döner
        item = sss_raw[idx]
        return {
            "soru":   item["Soru"],
            "cevap":  item["Cevap"],
            "modul":  item["Modul"],
            "url":    item["URL"],
            "skor":   score             # debug için skor da döndürüyoruz
        }

    return {
        "cevap": "Üzgünüm, bu konuda bir bilgi bulamadım.",
        "skor": 0
    }
