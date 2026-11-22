"""
Plik konfiguracyjny
"""
# region importy
# Biblioteki
import os
from typing import Dict

# endregion

ip = '0.0.0.0'
port = 5002
debug = True

base_dir = os.path.dirname(os.path.abspath(__file__)) # Ścieżka bezwzględna obecnego pliku
paths: Dict[str, str] = {
    'base_dir': base_dir,
    'db_file': os.path.join(base_dir, 'database.db'),
    'photos_parts': os.path.join(base_dir, 'uploads', 'parts')

}