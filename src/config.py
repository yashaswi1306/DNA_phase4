#Configuration for the WBMC Phase 4 Flask application

import os

#Return MariaDB connection settings from environment variables
def get_db_config():

    return {
        "host": os.getenv("DB_HOST", "127.0.0.1"),
        "port": int(os.getenv("DB_PORT", "3306")),
        "user": os.getenv("DB_USER", "root"),
        "password": os.getenv("DB_PASS", ""),
        "database": os.getenv("DB_NAME", "wbmc_db"),
        "charset": "utf8mb4",
        "connect_timeout": 5,
    }


SECRET_KEY = os.getenv(
    "FLASK_SECRET_KEY",
    "dev-only-change-this-key"
)
