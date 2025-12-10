import sqlite3
from pathlib import Path

DB_PATH = Path("users.db")

def InitDB():
    Connection = sqlite3.connect(DB_PATH)
    Connection.execute("""
        CREATE TABLE IF NOT EXISTS USER (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            PhoneNo INTEGER NOT NULL UNIQUE,
            Name VARCHAR2(100) NOT NULL,
            IsActive INTEGER NOT NULL DEFAULT 1,
            Position VARCHAR2(50) NOT NULL
        )
    """)
    Connection.commit()
    Connection.close()

def CreateUser(PhoneNo: int, Name: str, Position: str):
    Connection = sqlite3.connect(DB_PATH)
    try:
        Connection.execute("INSERT INTO USER (PhoneNo, Name, Position) VALUES (?, ?, ?)", (PhoneNo, Name, Position))
        Connection.commit()
    except sqlite3.IntegrityError:
        raise ValueError("Phone number already exists")
    finally:
        Connection.close()

def GetUserByPhone(PhoneNo: int):
    Connection = sqlite3.connect(DB_PATH)
    Query = Connection.execute("SELECT * FROM USER WHERE PhoneNo = ?", (PhoneNo,))
    Data = Query.fetchone()
    Connection.close()
    return Data