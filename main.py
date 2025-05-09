from fastapi import FastAPI, Query, Request
from rapidfuzz import process, fuzz
import json, re, unicodedata, pathlib

app = FastAPI(title="SSS API", version="1.0")

# ---------- Yardımcı fonksiyonlar ----------
_TURKISH_MAP = str.maketrans("çğıöşü", "cgiosu")  # çok hafif transliterasyon

def normalize(text: str) -> str:
    text = text.lower().translate(_TURKISH_MAP)
    text = unicodedata.normalize("NFKD", text)
    text = re.sub(r"[^\w\s]", " ", text)      # noktalama → boşluk
    text = re.sub(r"\s+", " ", text).strip()  # çoklu boşluk temizle
    return text

# ---------- Veri yükleme ----------
json_path = pathlib.Path(__file__).with_name("sss.json")
with json_path.open(encoding="utf-8") as f:
    sss_raw = json.load(f)

questions_norm = [normalize(item["soru"]) for item in sss_raw]

THRESHOLD = 30
SCORER = fuzz.token_set_ratio

# ---------- Ortak iş mantığı ----------
def find_best_match(q: str):
    q_norm = normalize(q)
    match = process.extractOne(
        q_norm,
        questions_norm,
        scorer=SCORER,
        score_cutoff=THRESHOLD
    )

    if match:
        _, score, idx = match
        item = sss_raw[idx]
        return {
            "soru": q,                   # Kullanıcının sorduğu orijinal soru
            "cevap": item["cevap"],
            "modul": item["modul"],
            "url": item["url"],
            "skor": score
        }
    else:
        return {
            "soru": q,
            "cevap": "Üzgünüm, bu konuda bir bilgi bulamadım.",
            "modul": None,
            "url": None,
            "skor": 0
        }

# ---------- API ----------
@app.get("/", tags=["health"])
def health():
    return {"status": "ok"}

@app.get("/api/sss", tags=["faq"])
def get_faq(q: str = Query(..., description="Kullanıcının Türkçe sorusu")):
    return find_best_match(q)

@app.post("/api/sss", tags=["faq"])
async def post_faq(request: Request):
    data = await request.json()
    q = data.get("q")
    if not q:
        return {"error": "Missing 'q' in JSON body"}
    return find_best_match(q)
