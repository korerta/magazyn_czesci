"""
Plik konfiguracyjny
"""

# region importy
# biblioteki
import os
# endregion

ip = '0.0.0.0'
port = 5001
debug = True
secret_key = os.getenv("secret_key")
