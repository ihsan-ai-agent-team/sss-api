from fastapi import FastAPI, Query, Request
from rapidfuzz import process, fuzz
import json, re, unicodedata, pathlib

app = FastAPI(title="SSS API", version="1.0")

_TURKISH_MAP = str.maketrans("çğıöşü", "cgiosu")

def normalize(text: str) -> str:
    text = text.lower().translate(_TURKISH_MAP)
    text = unicodedata.normalize("NFKD", text)
    text = re.sub(r"[^\w\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

json_path = pathlib.Path(__file__).with_name("sss.json")
with json_path.open(encoding="utf-8") as f:
    sss_raw = json.load(f)

questions_norm = [normalize(item["soru"]) for item in sss_raw]

THRESHOLD = 30
SCORER = fuzz.token_set_ratio

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
            "soru": q,
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

@app.get("/", tags=["health"])
def health():
    return {"status": "ok"}

@app.api_route("/api/sss", methods=["GET", "POST"], tags=["faq"])
async def faq_handler(request: Request, q: str = Query(None)):
    q_value = q

    # POST geldiyse ve query boşsa body'yi dene
    if request.method == "POST" and not q_value:
        try:
            data = await request.json()
            q_from_body = data.get("q")
            if q_from_body:
                q_value = q_from_body
        except:
            pass

    if not q_value:
        return {"error": "Missing 'q' in query or body"}

    return find_best_match(q_value)
