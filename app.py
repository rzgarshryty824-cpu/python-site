from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return "سایت من آنلاین شد 🌍"

if __name__ == "__main__":
    app.run()
