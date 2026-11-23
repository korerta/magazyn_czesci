"""
Serwer WWW
"""
# region importy
# Biblioteki
from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
import uuid, os

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

def return_parts(deleted: bool) -> dict:
    data_return = {'status': False}

    # region pobranie z bazy danych części oraz obsługa błędu
    parts = database.return_parts(deleted)
    if not parts['status']:
        data_return['parts'] = ()
        data_return['message'] = 'Wystąpił nieoczekiwany bład podczas pobierania części z bazy danych.'
        print('Wystąpił nieoczekiwany bład podczas pobierania części z bazy danych.')
    # endregion

    data_return['status'] = True
    data_return['parts'] = parts['result']

    return data_return

def show_part_form(form: dict) -> dict:
    """
    :param form: Formularz
    :return: Zwraca dict
    """
    data_return = {'status': False}

    # region czy jest w adresie URL Identyfikator części
    if not 'part_id' in form:
        data_return['message'] = 'W adresie URL brak ID części'
        return data_return
    # endregion

    # region czy Identyfikator części jest liczbą
    try:
        id_part = int(form['part_id'])

    except Exception as error:
        print(f'Identyfikator części nie jest liczbą całkowitą, błąd: {error}.')
        data_return['message'] = f'Identyfikator części nie jest liczbą całkowitą, błąd: {error}.'
        return data_return
    # endregion

    # region pobranie z bazy danych części
    result = database.return_part(id_part)
    if not result['status']:
        print('Błąd podczas pobierania części z bazy danych.')
        data_return['message'] = 'Błąd podczas pobierania części z bazy danych.'
        return data_return

    data_return['data'] = result['result']
    # endregion

    uuid = result['result'][9] # UUID

    # region pobranie zdjęć
    list_photos = []
    path = os.path.join('static', 'parts', uuid)
    for file in os.listdir(path):
        full_path = os.path.join(path, file)
        list_photos.append(full_path)
    # endregion

    data_return['photos'] = list_photos

    return data_return

def return_back_part(form: dict) -> dict:
    """
    :param form: Formularz
    :return: Zwraca dict
    """

    data_return = {'status': False}

    # region czy jest w adresie URL Identyfikator części
    if not 'part_id' in form:
        data_return['message'] = 'Nie znaleziono ID części'
        return data_return
    # endregion

    # region czy Identyfikator części jest liczbą
    try:
        id_part = int(form['part_id'])

    except Exception as error:
        print(f'Identyfikator części nie jest liczbą całkowitą, błąd: {error}.')
        data_return['message'] = f'Identyfikator części nie jest liczbą całkowitą, błąd: {error}.'
        return data_return
    # endregion

    # region czy się udało przywrócić część z kosza do magazynu
    if not database.return_part_back(id_part):
        print('Błąd podczas przywracania z kosza części do magazynu.')
        data_return['message'] = 'Błąd podczas przywracania z kosza części do magazynu.'
        return data_return

    data_return['status'] = True
    data_return['message'] = 'Pomyślnie przywrócono z kosza część.'

    return data_return


# endregion

# region Konfiguracja flask
app = Flask(__name__)
# endregion

# region Trasy
# Strona główna
@app.route("/", methods=['GET', 'POST'])
def home():
    parts = return_parts(False)
    return render_template("index.html", data=parts)

# Dodaj część
@app.route("/add_part", methods=['GET', 'POST'])
def add_part():
    return_data = []
    # przesłanie formularza
    if request.form:
        return_data = add_part_form(request.form, request.files)

    return render_template("add_part.html", data=return_data)

# Wyświetl część
@app.route("/show_part", methods=['GET', 'POST'])
def show_part():
    return_data = []
    # przesłanie formularza
    if request.args:
        return_data = show_part_form(request.args)

    return render_template("show_part.html", data=return_data)

# Kosz
@app.route("/basket", methods=['GET', 'POST'])
def basket():
    parts = return_parts(True)
    if request.form:
        result = return_back_part(request.form)

        parts['message'] = result['message']

    return render_template("basket.html", data=parts)

# endregion

if __name__ == "__main__":
    print('Uruchamianie serwera WWW.')
    app.run(debug=debug, host=ip, port=port)