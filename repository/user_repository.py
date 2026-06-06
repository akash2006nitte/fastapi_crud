import sqlite3
from pathlib import Path

from models.user_models import User


class UserRepository:
    def __init__(self):
        self.db_path = Path(__file__).resolve().parent.parent / "users.db"
        self._initialize_database()

    def _get_connection(self):
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize_database(self):
        with self._get_connection() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    email TEXT NOT NULL UNIQUE
                )
                """
            )
            connection.commit()

    def _row_to_user(self, row):
        if row is None:
            return None
        return User(id=row["id"], name=row["name"], email=row["email"])

    def get_all_users(self):
        with self._get_connection() as connection:
            rows = connection.execute(
                "SELECT id, name, email FROM users ORDER BY id"
            ).fetchall()
            return [self._row_to_user(row) for row in rows]

    def add_user(self, name: str, email: str):
        with self._get_connection() as connection:
            cursor = connection.execute(
                "INSERT INTO users (name, email) VALUES (?, ?)",
                (name, email),
            )
            connection.commit()
            return User(id=cursor.lastrowid, name=name, email=email)

    def get_user(self, user_id: int) -> User:
        with self._get_connection() as connection:
            row = connection.execute(
                "SELECT id, name, email FROM users WHERE id = ?",
                (user_id,),
            ).fetchone()
            return self._row_to_user(row)

    def update_user(self, user_id: int, name: str, email: str) -> bool:
        with self._get_connection() as connection:
            cursor = connection.execute(
                "UPDATE users SET name = ?, email = ? WHERE id = ?",
                (name, email, user_id),
            )
            connection.commit()
            return cursor.rowcount > 0

    def delete_user(self, user_id: int) -> bool:
        with self._get_connection() as connection:
            cursor = connection.execute(
                "DELETE FROM users WHERE id = ?",
                (user_id,),
            )
            connection.commit()
            return cursor.rowcount > 0