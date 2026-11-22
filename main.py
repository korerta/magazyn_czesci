"""
Serwer WWW
"""
import os.path

# region importy
# Biblioteki
from flask import Flask, render_template, redirect, url_for, request
from werkzeug.utils import secure_filename
import uuid

# Moje pliki
from config import ip, port, debug, paths
import database
# endregion

# region obsługa formularzy
def add_part_form(form: dict, files: dict) -> dict:
    data_return = {'status': False}

    # Wrzucanie plików
    def upload_file(file, id_part_in):
        safe_name = secure_filename(file.filename)
        ext = safe_name.rsplit('.', 1)[1].lower() if '.' in safe_name else 'jpg'
        unique_filename = f"{uuid.uuid4().hex[:8]}.{ext}"

        path = os.path.join(paths['photos_parts'], id_part_in, unique_filename)

        # Zapis pliku do określonego folderu
        try:
            file.save(path)
            return True

        except Exception as error:
            print('Błąd podczas wrzucania pliku błąd:', error, '.')
            return False

    # region czy otrzymano wszystkie pola formularza
    for x in ('name_part', 'desc_part', 'condition_part', 'oem_part', 'vehicle', 'location'):
        if not x in form:
            print('Brakuje pola formularza', x)
            data_return['message'] = f'Brakuje pola formularza {x}'
            return data_return
    # endregion

    # region walidacja typów danych formularzy
    try:
        name_part = str(form['name_part'])
        desc_part = str(form['desc_part'])
        condition_part = str(form['condition_part'])
        oem_part = str(form['oem_part'])
        vehicle = str(form['vehicle'])
        location = str(form['location'])

    except Exception as error:
        print(f'Jakieś pole formularza ma nieprawidłowy typ danych, błąd: {error}')
        data_return['message'] = f'Jakieś pole formularza ma nieprawidłowy typ danych, błąd: {error}'
        return data_return
    # endregion

    # region obsługa is_wrapped
    if not 'is_wrapped' in form:
        is_wrapped = False

    else:
        is_wrapped = True
    # endregion

    id_part = str(uuid.uuid4())  # ID nowego CV

    # region tworzenie folderu dla części
    path = os.path.join(paths['photos_parts'], id_part)
    os.makedirs(path, exist_ok=True)
    # endregion

    # region obsługa zdjęć
    for photo in files.getlist('photos'):
        if not upload_file(photo, id_part):
            data_return['message'] = 'Błąd podczas dodawania zdjęcia części.'
            return data_return
    # endregion

    # region dodanie do bazy danych części
    if database.add_part(name_part, desc_part, condition_part, oem_part, vehicle, location, is_wrapped, id_part):
        data_return['message'] = 'Pomyślnie dodano część do magazynu.'

    else:
        data_return['message'] = 'Błąd podczas dodawania części do magazynu.'
    # endregion

    return data_return

# endregion

# region Konfiguracja flask
app = Flask(__name__)
# endregion

# region Trasy
# Strona główna
@app.route("/", methods=['GET', 'POST'])
def home():
    return render_template("index.html")

# Dodaj część
@app.route("/add_part", methods=['GET', 'POST'])
def add_part():
    return_data = []
    # przesłanie formularza
    if request.form:
        return_data = add_part_form(request.form, request.files)

    return render_template("add_part.html", data=return_data)

# endregion

if __name__ == "__main__":
    print('Uruchamianie serwera WWW.')
    app.run(debug=debug, host=ip, port=port)