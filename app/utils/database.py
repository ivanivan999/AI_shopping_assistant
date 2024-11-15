# app/utils/database.py

import sqlite3
import os
from typing import Optional

def get_db() -> sqlite3.Connection:
    """Get database connection with row factory"""
    # Ensure data directory exists
    os.makedirs('data', exist_ok=True)
    
    conn = sqlite3.connect('data/shopping.db')
    conn.row_factory = sqlite3.Row
    return conn

