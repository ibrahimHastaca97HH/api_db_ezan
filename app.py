from flask import Flask, jsonify, request
from vakit import fetch_or_cache_vakitler

app = Flask(__name__)

@app.route("/")
def home():
    return jsonify({"message": "Vakitgeldi Ezan API çalışıyor."})

@app.route("/vakitler")
def get_vakitler():
    il = request.args.get("il")
    ilce = request.args.get("ilce")

    if not il or not ilce:
        return jsonify({"hata": "Lütfen 'il' ve 'ilce' parametrelerini belirtin."}), 400

    try:
        result = fetch_or_cache_vakitler(il, ilce)
        return jsonify(result)
    except Exception as e:
        return jsonify({"hata": str(e)}), 500

# === Bu kısım Render için gereklidir ===
if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
