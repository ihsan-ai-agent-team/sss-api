from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import json

app = FastAPI()

# CORS ayarı (frontend için gerekebilir)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Gerekirse kısıtlayabilirsin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# JSON dosyasını yükle
with open("sss.json", "r", encoding="utf-8") as file:
    sss_data = json.load(file)

@app.get("/api/sss")
def get_sss():
    return sss_data
