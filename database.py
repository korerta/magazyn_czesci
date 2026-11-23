"""
Plik obsługujący bazę danych
"""

# region importy
# Biblioteki
import sqlite3

# Moje pliki
from config import paths

# endregion

#region Funkcje wykorzystywane wiele razy
# Zamknięcie połączenia z bazą danych
def close_connection(conn) -> None:
    """
    Funkcja zamykająca połączenie z bazą danych
    :param conn: Połączenie z bazą danych
    :return: Nic nie zwraca
    """

    try:
        conn.close()

    except Exception as error:
        print('Błąd podczas zamykania połączenia z bazą danych, błąd:', error)

# Otwieranie połączenia i tworzenie kursora
def conn_cursor() -> dict:
    """
    Funkcja otwierająca połączenie z bazą danych i tworzy kursor
    :return: Zwraca kursor i połączenie z bazą danych
    """
    data_return = {}

    try:
        conn = sqlite3.connect(paths['db_file'], timeout=30.0)  # Otwieranie połączenia
        cursor = conn.cursor()  # Tworzenie kursora do zapytań
        data_return['cursor'] = cursor
        data_return['conn'] = conn
        data_return['status'] = True

    except Exception as error:
        data_return['error'] = error
        data_return['status'] = False

    return data_return
#endregion

# region Zapytania
# Dodanie części do magazynu
def add_part(name_part: str, desc_part: str, condition_part: str, oem_part: str, vehicle: str, location: str, is_wrapped: bool, uuid: str) -> bool:
    """
    Dodanie części do magazynu
    :param name_part: Nazwa części
    :param desc_part: Opis części
    :param condition_part: Stan części (uszkodzony, nowy itp
    :param oem_part: Numer OEM części
    :param vehicle: Z jakiego pojazdu część pochodzi
    :param location: Umiejscowienie w magazynie części
    :param is_wrapped: Czy część jest zapakowana
    :param uuid: Identyfikator wewnętrzny części
    :return: Zwraca bool czy się udało
    """

    data_conn_cursor = conn_cursor()  # Połączenie z bazą danych

    # Jeśli nie zwróciło żadnego błędu
    if data_conn_cursor['status']:
        cursor = data_conn_cursor['cursor']
        conn = data_conn_cursor['conn']

        try:
            query = "INSERT INTO parts (name, description, condition, oem_number, vehicle, location, is_wrapped, uuid) VALUES (?, ?, ?, ?, ?, ?, ?, ?);"
            cursor.execute(query, (name_part, desc_part, condition_part, oem_part, vehicle, location, is_wrapped, uuid))
            conn.commit()
            return True

        except Exception as error:
            try:
                conn.rollback()
            except Exception:
                pass
            print('Błąd podczas zwracania rezultatu w add_part, błąd:', error)
            return False

        finally:
            try:
                cursor.close()
            except Exception:
                pass

            close_connection(conn)

    # Jeśli zwróciło błąd
    else:
        print('Błąd podczas zwracania rezultatu w add_part.')
        return False

# Zwrócenie wszystkich części
def return_parts(deleted: bool) -> dict:
    """
    :param deleted: Bool zwrócić dostępne czy usunięte True - Usunięte, False - Dostępne
    Zwrócenie wszystkich części
    :return: Zwraca dict z częściami
    """

    res_conn = conn_cursor() # Połączenie z bazą danych
    data_return = {}

    # Jeśli nie zwróciło żadnego błędu
    if res_conn.get('status'):
        try:
            cursor = res_conn['cursor']

            if deleted:
                cursor.execute("SELECT * FROM parts WHERE deleted=1")
            else:
                cursor.execute("SELECT * FROM parts WHERE deleted=0")

            data_return['result'] = cursor.fetchall()
            data_return['status'] = True

        except Exception as error:
            print('Błąd podczas zwracania rezultatu w return_parts, błąd:', error)
            data_return['status'] = False
            data_return['error'] = f'Błąd podczas zwracania rezultatu w return_parts, błąd: {error}'

        finally:
            conn = res_conn['conn']
            close_connection(conn)

    # Jeśli zwróciło błąd
    else:
        print('Błąd podczas zwracania rezultatu w return_parts')
        data_return['status'] = False
        data_return['error'] = 'Błąd podczas zwracania rezultatu w return_parts'

    return data_return

# Zwrócenie części
def return_part(id_part: int) -> dict:
    """
    Zwrócenie części
    :param id_part: Identyfikator części
    :return: Zwraca dict z częściami
    """

    res_conn = conn_cursor() # Połączenie z bazą danych
    data_return = {}

    # Jeśli nie zwróciło żadnego błędu
    if res_conn.get('status'):
        try:
            cursor = res_conn['cursor']

            cursor.execute("SELECT * FROM parts WHERE id= ?", (id_part,))
            data_return['result'] = cursor.fetchone()
            data_return['status'] = True

        except Exception as error:
            print('Błąd podczas zwracania rezultatu w return_part, błąd:', error)
            data_return['status'] = False
            data_return['error'] = f'Błąd podczas zwracania rezultatu w return_part, błąd: {error}'

        finally:
            conn = res_conn['conn']
            close_connection(conn)

    # Jeśli zwróciło błąd
    else:
        print('Błąd podczas zwracania rezultatu w return_part')
        data_return['status'] = False
        data_return['error'] = 'Błąd podczas zwracania rezultatu w return_part'

    return data_return

# Dodanie części z kosza do magazynu
def return_part_back(id_part: int) -> bool:
    """
    Dodanie części do magazynu
    :param id_part: Identyfikator części
    :return: Zwraca bool czy się udało
    """

    data_conn_cursor = conn_cursor()  # Połączenie z bazą danych

    # Jeśli nie zwróciło żadnego błędu
    if data_conn_cursor['status']:
        cursor = data_conn_cursor['cursor']
        conn = data_conn_cursor['conn']

        try:
            query = "UPDATE parts SET deleted= 0 WHERE id= ?"
            cursor.execute(query, (id_part,))
            conn.commit()
            return True

        except Exception as error:
            try:
                conn.rollback()
            except Exception:
                pass
            print('Błąd podczas zwracania rezultatu w return_part_back, błąd:', error)
            return False

        finally:
            try:
                cursor.close()
            except Exception:
                pass

            close_connection(conn)

    # Jeśli zwróciło błąd
    else:
        print('Błąd podczas zwracania rezultatu w return_part_back.')
        return False


# endregion