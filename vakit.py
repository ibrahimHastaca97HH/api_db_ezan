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

    # Veritabanında var mı?
    result = conn.execute(select(vakitler).where(vakitler.c.id == row_id)).fetchone()
    if result:
        return json.loads(result['data'])

    # Yoksa scrape et
    url = f"https://www.diyanet.gov.tr/tr-TR/namazvakitleri?il={il}"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

    times = soup.find_all("div", class_="tpt-time")
    vakit_list = ["Imsak", "Sunrise", "Dhuhr", "Asr", "Maghrib", "Isha"]
    saatler = [v.text.strip() for v in times]
    vakit_data = dict(zip(vakit_list, saatler))

    vakit_data.update({
        "Fajr": vakit_data["Imsak"],
        "Sunset": vakit_data["Maghrib"],
        "Midnight": "00:39",
        "Firstthird": "23:04",
        "Lastthird": "02:14"
    })

    miladi = datetime.today()
    hicri = convert.Gregorian(miladi.year, miladi.month, miladi.day).to_hijri()

    response_json = {
        "konum": f"{il}, {ilce}, Turkey",
        "tarih": miladi.strftime("%d %B %Y"),
        "hicri": f"{hicri.day} {hicri.month_name()} {hicri.year}",
        "vakitler": vakit_data
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
