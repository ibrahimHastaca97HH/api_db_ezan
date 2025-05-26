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

    result = conn.execute(select(vakitler).where(vakitler.c.id == row_id)).fetchone()
    if result:
        return json.loads(result['data'])

    # Web sayfasından veriyi çek
    url = f"https://www.diyanet.gov.tr/tr-TR/namazvakitleri?il={il}"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

    # Yeni yapıya uygun div-based çekme
    time_names = soup.find_all("div", class_="tpt-label")
    time_values = soup.find_all("div", class_="tpt-time")

    if not time_names or not time_values or len(time_names) != len(time_values):
        raise Exception("Namaz vakit tablosu bulunamadı. Sayfa yapısı değişmiş olabilir.")

    vakit_data_raw = {}
    for name, value in zip(time_names, time_values):
        vakit_data_raw[name.text.strip()] = value.text.strip()

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

    # Ek vakitler
    translated_data.update({
        "Fajr": translated_data["Imsak"],
        "Sunset": translated_data["Maghrib"],
        "Midnight": "00:39",
        "Firstthird": "23:04",
        "Lastthird": "02:14"
    })

    # Tarihler
    miladi = datetime.today()
    hicri = convert.Gregorian(miladi.year, miladi.month, miladi.day).to_hijri()

    response_json = {
        "konum": f"{il}, {ilce}, Turkey",
        "tarih": miladi.strftime("%d %B %Y"),
        "hicri": f"{hicri.day} {hicri.month_name()} {hicri.year} H",
        "vakitler": translated_data
    }

    # Veritabanına ekle
    conn.execute(vakitler.insert().values(
        id=row_id,
        il=il,
        ilce=ilce,
        tarih=today,
        data=json.dumps(response_json)
    ))

    return response_json
