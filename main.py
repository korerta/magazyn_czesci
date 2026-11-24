"""
Serwer WWW
"""

# region importy
# Biblioteki
from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
import uuid, os
from datetime import datetime

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
            data_return['error'] = f'Brakuje pola formularza {x}'
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
        data_return['error'] = f'Jakieś pole formularza ma nieprawidłowy typ danych, błąd: {error}'
        return data_return
    # endregion

    # region obsługa is_wrapped
    if not 'is_wrapped' in form:
        is_wrapped = False

    else:
        is_wrapped = True
    # endregion

    id_part = str(uuid.uuid4())  # ID nowego CV

    # region czas dodania części do magazynu
    now_full_time = datetime.now()
    time_add = now_full_time.strftime("%Y-%m-%d %H:%M:%S")
    # endregion

    # region tworzenie folderu dla części
    path = os.path.join(paths['photos_parts'], id_part)
    try:
        os.makedirs(path, exist_ok=True)

    except Exception as error:
        print(f'Błąd podczas tworzenia katalogu na grafiki części, błąd: {error}.')
        data_return['error'] = f'Błąd podczas tworzenia katalogu na grafiki części, błąd: {error}.'
        return data_return
    # endregion

    # region obsługa zdjęć
    for photo in files.getlist('photos'):
        if photo and photo.filename != '':
            if not upload_file(photo, id_part):
                data_return['error'] = 'Błąd podczas dodawania zdjęcia części.'
                return data_return
    # endregion

    # region dodanie do bazy danych części
    if database.add_part(name_part, desc_part, condition_part, oem_part, vehicle, location, is_wrapped, id_part, time_add):
        data_return['message'] = 'Pomyślnie dodano część do magazynu.'
        data_return['status'] = True

    else:
        data_return['error'] = 'Błąd podczas dodawania części do magazynu.'
    # endregion

    return data_return

def return_parts(deleted: bool) -> dict:
    data_return = {} # dane do zwrócenia

    result = database.return_parts(deleted) # zapytanie do bazy danych

    # region obsługa błędu
    if not result['status']:
        data_return['result'] = ()
        data_return['error'] = result['error']
        print(result['error'])
    # endregion

    data_return = result # wszystko git

    return data_return

def show_part_form(form: dict) -> dict:
    """
    :param form: Formularz
    :return: Zwraca dict
    """
    data_return = {'status': False} # dane do zwrócenia

    # region czy jest w adresie URL Identyfikator części
    if not 'part_id' in form:
        data_return['error'] = 'W adresie URL brak ID części'
        return data_return
    # endregion

    # region czy Identyfikator części jest liczbą
    try:
        id_part = int(form['part_id'])

    except Exception as error:
        print(f'Identyfikator części nie jest liczbą całkowitą, błąd: {error}.')
        data_return['error'] = f'Identyfikator części nie jest liczbą całkowitą, błąd: {error}.'
        return data_return
    # endregion

    result = database.return_part(id_part) # zapytanie do bazy danych

    data_return = result

    # region obsługa błędu
    if not result['status']:
        print(result['error'])
        return data_return
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

def del_return_back_part(form: dict, change: int) -> dict:
    """
    :param form: Formularz
    :param change: Zmienić wartość na 1 czy 0
    :return: Zwraca dict
    """

    data_return = {'status': False, 'error': '', 'message': ''}

    # region czy Identyfikator części jest liczbą
    try:
        id_part = int(form['part_id'])

    except Exception as error:
        print(f'Identyfikator części nie jest liczbą całkowitą, błąd: {error}.')
        data_return['error'] = f'Identyfikator części nie jest liczbą całkowitą, błąd: {error}.'
        return data_return
    # endregion

    # region walidacja zmiennej change
    if change != 0 and change != 1:
        print('Nieprawidłowa wartość w polu part_id.')
        data_return['error'] = 'Nieprawidłowa wartość w polu part_id.'
        return data_return
    # endregion

    # region czy się udało przywrócić/usunąć część
    if not database.return_part_back(id_part, change):
        if not change:
            print('Błąd podczas przywracania części z kosza do magazynu.')
            data_return['error'] = 'Błąd podczas przywracania części z kosza do magazynu.'

        else:
            print('Błąd podczas usuwania części z magazynu.')
            data_return['error'] = 'Błąd podczas usuwania części z magazynu.'

    else:
        if not change:
            data_return['message'] = 'Pomyślnie przywrócono z kosza część.'

        else:
            data_return['message'] = 'Pomyślnie usunięto część z magazynu.'

        data_return['status'] = True
    # endregion

    return data_return

def find_part(form: dict) -> dict:
    data_return = {} # dane do zwrócenia

    id_part = form['id_search'] # zmienna z ID części

    result = database.find_part(id_part) # zapytanie do bazy danych

    # region jeśli wystąpił błąd
    if not result['status']:
        data_return['error'] = result['error']
        print(result['error'])
    # endregion

    data_return = result # wszystko git

    return data_return

# endregion

# region Konfiguracja flask
app = Flask(__name__)
# endregion

# region Trasy
# Strona główna
@app.route("/", methods=['GET', 'POST'])
def home():
    return_data = {'del_form': '', 'find_form': ''}
    # przesłanie formularza
    if request.form:
        if 'id_search' in request.form:
            return_data['find_form'] = find_part(request.form)

        if 'part_id' in request.form:
            return_data['del_form'] = del_return_back_part(request.form, 1)

    return_data['parts_form'] = return_parts(False)

    return render_template("index.html", data=return_data)

# Dodaj część
@app.route("/add_part", methods=['GET', 'POST'])
def add_part():
    return_data = {}

    # przesłanie formularza
    if request.form:
        return_data = add_part_form(request.form, request.files)

    return render_template("add_part.html", data=return_data)

# Wyświetl część
@app.route("/show_part", methods=['GET', 'POST'])
def show_part():
    return_data = {}

    # przesłanie formularza
    if request.args:
        return_data = show_part_form(request.args)

    return render_template("show_part.html", data=return_data)

# Kosz
@app.route("/basket", methods=['GET', 'POST'])
def basket():
    parts = {
        'parts': return_parts(True),
        'form_back_part': {
            'error': '',
            'message': ''
        }
    }

    if request.form:
        result = del_return_back_part(request.form, 0)
        parts['form_back_part'] = result

    return render_template("basket.html", data=parts)

# endregion

if __name__ == "__main__":
    print('Uruchamianie serwera WWW.')
    app.run(debug=debug, host=ip, port=port)