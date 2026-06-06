from sqlalchemy.exc import IntegrityError

from database import Base, SessionLocal, engine
from models.user_models import User


class UserRepository:
    def __init__(self):
        Base.metadata.create_all(bind=engine)

    def _get_session(self):
        return SessionLocal()

    def get_all_users(self):
        with self._get_session() as session:
            return session.query(User).order_by(User.id).all()

    def add_user(self, name: str, email: str):
        with self._get_session() as session:
            user = User(name=name, email=email)
            session.add(user)
            session.commit()
            session.refresh(user)
            return user

    def get_user(self, user_id: int) -> User:
        with self._get_session() as session:
            return session.get(User, user_id)

    def update_user(self, user_id: int, name: str, email: str) -> bool:
        with self._get_session() as session:
            user = session.get(User, user_id)
            if not user:
                return False

            user.name = name
            user.email = email
            try:
                session.commit()
            except IntegrityError:
                session.rollback()
                raise
            return True

    def delete_user(self, user_id: int) -> bool:
        with self._get_session() as session:
            user = session.get(User, user_id)
            if not user:
                return False

            session.delete(user)
            session.commit()
            return True