# Magazyn Części

Lekka aplikacja webowa oparta na szkielecie Flask oraz bazie danych SQLite, przeznaczona do ewidencji, wyszukiwania oraz katalogowania części samochodowych wraz z dokumentacją fotograficzną.

## Funkcjonalności

* **Ewidencja części:** Dodawanie nowych pozycji wraz ze szczegółowymi parametrami (nazwa, opis, stan techniczny, numer OEM, pojazd docelowy, dokładna lokalizacja w magazynie oraz informacja o zapakowaniu).
* **Dokumentacja fotograficzna:** Obsługa przesyłania wielu zdjęć jednocześnie dla pojedynczej części. Pliki są automatycznie izolowane w dedykowanych katalogach identyfikowanych przez UUID rekordu.
* **Wyszukiwarka:** Szybkie wyszukiwanie dostępnych części po wewnętrznym identyfikatorze (ID), numerze katalogowym OEM lub unikalnym identyfikatorze UUID.
* **Mechanizm kosza (Soft Delete):** Usuwanie części z głównego widoku przenosi je do kosza, umożliwiając ich późniejsze przywrócenie bez utraty danych i powiązanych plików.
* **Widok szczegółowy:** Dedykowana karta dla każdej części prezentująca pełną specyfikację techniczną oraz galerię zapisanych zdjęć.

## Struktura projektu

```text
magazyn_czesci/
├── config.py           # Konfiguracja sieciowa serwera oraz ścieżek systemowych
├── database.py         # Warstwa dostępu do danych i obsługa zapytań SQLite
├── main.py             # Główna logika aplikacji, walidacja formularzy i routing Flask
├── database.db         # Plik bazy danych SQLite
├── static/
│   └── parts/          # Katalog przechowujący podfoldery (UUID) ze zdjęciami części
└── templates/
    ├── index.html      # Strona główna (wyszukiwarka, usuwanie, lista dostępnych części)
    ├── add_part.html   # Formularz dodawania nowej części i zdjęć
    ├── show_part.html  # Widok szczegółowy pojedynczej części wraz z galerią
    └── basket.html     # Widok kosza z możliwością przywracania usuniętych pozycji
```

## Schemat bazy danych

Aplikacja wykorzystuje pojedynczą tabelę `parts` w bazie SQLite:

| Kolumna | Typ | Opis |
| :--- | :--- | :--- |
| `id` | `INTEGER` | Klucz główny (AUTOINCREMENT) |
| `name` | `TEXT` | Nazwa części |
| `description` | `TEXT` | Szczegółowy opis części |
| `date` | `TEXT` | Data i godzina dodania rekordu (`YYYY-MM-DD HH:MM:SS`) |
| `condition` | `TEXT` | Stan części (np. nowy, używany, uszkodzony) |
| `oem_number` | `TEXT` | Numer katalogowy OEM |
| `vehicle` | `TEXT` | Pojazd, z którego pochodzi część |
| `location` | `TEXT` | Dokładne miejsce składowania w magazynie |
| `is_wrapped` | `INTEGER` | Flaga zapakowania (`0` - nie, `1` - tak) |
| `uuid` | `TEXT` | Unikalny identyfikator powiązany z katalogiem zdjęć |
| `deleted` | `INTEGER` | Flaga stanu w koszu (`0` - aktywna, `1` - w koszu) |

## Wymagania i instalacja

### Wymagania wstępne
* Python 3.8 lub nowszy
* Biblioteka `Flask` oraz `Werkzeug`

### Kroki uruchomienia

1. Sklonuj repozytorium lub skopiuj pliki projektu do katalogu docelowego.
2. Zainstaluj wymagane zależności:
   ```bash
   pip install flask
   ```
3. Upewnij się, że plik bazy danych `database.db` zawiera tabelę `parts` zgodną ze schematem powyżej.
4. Dostosuj ustawienia w pliku `config.py` (domyślnie serwer nasłuchuje na adresie `0.0.0.0` i porcie `5002`).
5. Uruchom aplikację:
   ```bash
   python main.py
   ```
6. Otwórz przeglądarkę internetową i przejdź pod adres `http://127.0.0.1:5002` (lub adres IP hosta w sieci lokalnej).

## Konfiguracja

Parametry startowe aplikacji znajdują się w pliku `config.py`:

* `ip` – adres interfejsu sieciowego (domyślnie `'0.0.0.0'`, co umożliwia dostęp z innych urządzeń w sieci lokalnej).
* `port` – port serwera HTTP (domyślnie `5002`).
* `debug` – tryb debugowania Flaska (`True` / `False`).
* `paths` – słownik definiujący bezwzględne ścieżki do pliku bazy danych (`database.db`) oraz katalogu ze zdjęciami (`static/parts`).

---

*Uwaga: Niniejsza dokumentacja (plik README.md) została wygenerowana automatycznie przez sztuczną inteligencję (AI) na podstawie analizy kodu źródłowego projektu.*