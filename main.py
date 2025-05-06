from fastapi import FastAPI, Query
import json
from difflib import get_close_matches

app = FastAPI()

# SSS verisini önceden yükle
with open("sss.json", "r", encoding="utf-8") as f:
    sss_list = json.load(f)

@app.get("/")
def home():
    return {"status": "OK"}

@app.get("/api/sss")
def get_answer(q: str = Query(..., description="Kullanıcı sorusu")):
    questions = [item["Soru"] for item in sss_list]
    match = get_close_matches(q, questions, n=1, cutoff=0.4)

    if match:
        # Eşleşen soruyu bul
        for item in sss_list:
            if item["Soru"] == match[0]:
                return {
                    "soru": item["Soru"],
                    "cevap": item["Cevap"],
                    "modul": item["Modul"],
                    "url": item["URL"]
                }

    return {"cevap": "Üzgünüm, bu konuda bir bilgi bulamadım."}
