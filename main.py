"""
Serwer WWW
"""

# region importy
# Biblioteki
from flask import Flask, render_template, redirect, url_for, request, jsonify
from datetime import datetime

# Moje pliki
from config import ip, port, debug, secret_key
import database
# endregion

def data_home() -> dict:
    data_return = {}
    return data_return

# region Konfiguracja flask
app = Flask(__name__)
app.config['SECRET_KEY'] = secret_key
# endregion

# region Trasy
# Strona główna
@app.route("/", methods=['GET', 'POST'])
def home():
    return render_template("index.html")

# endregion

if __name__ == "__main__":
    print('Uruchamianie serwera WWW.')
    app.run(debug=debug, host=ip, port=port)