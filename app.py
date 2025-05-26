from flask import Flask, jsonify, request
from vakit import fetch_or_cache_vakitler

app = Flask(__name__)

@app.route("/")
def home():
    return jsonify({"message": "Vakitgeldi Ezan API çalışıyor."})

@app.route("/vakitler")
def get_vakitler():
    il = request.args.get("il", "Hatay")
    ilce = request.args.get("ilce", "Yayladağı")

    try:
        result = fetch_or_cache_vakitler(il, ilce)
        return jsonify(result)
    except Exception as e:
        return jsonify({"hata": str(e)}), 500
