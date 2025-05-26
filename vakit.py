import requests
from bs4 import BeautifulSoup
from datetime import datetime, date
from hijri_converter import convert
from sqlalchemy import select
from db import engine, vakitler
import json

def fetch_or_cache_vakitler(il, ilce):
    conn = engine.connect()
    today = date.today()
    row_id = f"{il.lower()}_{ilce.lower()}_{today.isoformat()}"

    # Veritabanında kayıt var mı?
    result = conn.execute(select(vakitler).where(vakitler.c.id == row_id)).fetchone()
    if result:
        return json.loads(result['data'])

    # Diyanet'ten veri çek
    url = f"https://www.diyanet.gov.tr/tr-TR/namazvakitleri?il={il}"
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception("Diyanet sayfasına ulaşılamıyor.")

    soup = BeautifulSoup(response.content, "html.parser")

    # Namaz vakti tablosunu bul
    table = soup.find("table", id="today-pray-times")
    if not table:
        raise Exception("Namaz vakit tablosu bulunamadı. Sayfa yapısı değişmiş olabilir.")

    rows = table.find_all("tr")
    vakit_data_raw = {}

    for row in rows:
        cols = row.find_all("td")
        if len(cols) == 2:
            name = cols[0].text.strip()
            time = cols[1].text.strip()
            vakit_data_raw[name] = time

    # Türkçe -> İngilizce çeviri
    translation = {
        "İmsak": "Imsak",
        "Güneş": "Sunrise",
        "Öğle": "Dhuhr",
        "İkindi": "Asr",
        "Akşam": "Maghrib",
        "Yatsı": "Isha"
    }

    translated_data = {}
    for tr_key, en_key in translation.items():
        if tr_key in vakit_data_raw:
            translated_data[en_key] = vakit_data_raw[tr_key]
        else:
            raise Exception(f"{tr_key} vakti bulunamadı. Sayfa yapısı değişmiş olabilir.")

    # Sanal vakitler ekle
    translated_data.update({
        "Fajr": translated_data["Imsak"],
        "Sunset": translated_data["Maghrib"],
        "Midnight": "00:39",     # Örnek değerler (gelişmiş hesaplama yapılabilir)
        "Firstthird": "23:04",
        "Lastthird": "02:14"
    })

    # Miladi ve Hicri tarih bilgileri
    miladi = datetime.today()
    hicri = convert.Gregorian(miladi.year, miladi.month, miladi.day).to_hijri()

    response_json = {
        "konum": f"{il}, {ilce}, Turkey",
        "tarih": miladi.strftime("%d %B %Y"),
        "hicri": f"{hicri.day} {hicri.month_name()} {hicri.year} AH",
        "vakitler": translated_data
    }

    # Veritabanına kaydet
    conn.execute(vakitler.insert().values(
        id=row_id,
        il=il,
        ilce=ilce,
        tarih=today,
        data=json.dumps(response_json)
    ))

    return response_json
