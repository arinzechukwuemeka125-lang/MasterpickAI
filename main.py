from flask import Flask, jsonify
app = Flask(__name__)

@app.route("/")
def home():
    return "MasterpickAI LIVE"

@app.route("/api/predict")
def predict():
    return jsonify([
        {"home":"Arsenal","away":"Man City","pred":"GG"},
        {"home":"Real","away":"Barca","pred":"Over 2.5"}
    ])

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
