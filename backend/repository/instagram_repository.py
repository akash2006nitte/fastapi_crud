from sqlalchemy.exc import IntegrityError
from sqlalchemy import select, or_

from database import Base, SessionLocal, engine
from models.user_models import Comment, Follow, Like, Post, User


class InstagramRepository:
    def __init__(self):
        Base.metadata.create_all(bind=engine)

    def _get_session(self):
        return SessionLocal()

    def _user_exists(self, session, user_id: int) -> bool:
        return session.get(User, user_id) is not None

    def _post_exists(self, session, post_id: int) -> bool:
        return session.get(Post, post_id) is not None

    def create_user(self, username: str, email: str, full_name: str | None = None, bio: str | None = None):
        with self._get_session() as session:
            user = User(username=username, email=email, full_name=full_name, bio=bio)
            session.add(user)
            session.commit()
            session.refresh(user)
            return user

    def list_users(self):
        with self._get_session() as session:
            return session.query(User).order_by(User.id).all()

    def get_user(self, user_id: int):
        with self._get_session() as session:
            return session.get(User, user_id)

    def update_user(self, user_id: int, username: str, email: str, full_name: str | None = None, bio: str | None = None):
        with self._get_session() as session:
            user = session.get(User, user_id)
            if not user:
                return False

            user.username = username
            user.email = email
            user.full_name = full_name
            user.bio = bio
            session.commit()
            session.refresh(user)
            return user

    def delete_user(self, user_id: int) -> bool:
        with self._get_session() as session:
            user = session.get(User, user_id)
            if not user:
                return False

            session.delete(user)
            session.commit()
            return True

    def create_post(self, user_id: int, image_url: str, caption: str | None = None):
        with self._get_session() as session:
            if not self._user_exists(session, user_id):
                return None

            post = Post(user_id=user_id, image_url=image_url, caption=caption)
            session.add(post)
            session.commit()
            session.refresh(post)
            return post

    def list_posts(self):
        with self._get_session() as session:
            return session.query(Post).order_by(Post.created_at.desc()).all()

    def get_post(self, post_id: int):
        with self._get_session() as session:
            return session.get(Post, post_id)

    def list_user_posts(self, user_id: int):
        with self._get_session() as session:
            return session.query(Post).filter(Post.user_id == user_id).order_by(Post.created_at.desc()).all()

    def add_comment(self, post_id: int, user_id: int, text: str):
        with self._get_session() as session:
            if not self._post_exists(session, post_id) or not self._user_exists(session, user_id):
                return None

            comment = Comment(post_id=post_id, user_id=user_id, text=text)
            session.add(comment)
            session.commit()
            session.refresh(comment)
            return comment

    def list_comments(self, post_id: int):
        with self._get_session() as session:
            return session.query(Comment).filter(Comment.post_id == post_id).order_by(Comment.created_at.asc()).all()

    def like_post(self, post_id: int, user_id: int) -> bool:
        with self._get_session() as session:
            if not self._post_exists(session, post_id) or not self._user_exists(session, user_id):
                return False

            existing_like = session.query(Like).filter(Like.post_id == post_id, Like.user_id == user_id).first()
            if existing_like:
                return False

            like = Like(post_id=post_id, user_id=user_id)
            session.add(like)
            session.commit()
            return True

    def unlike_post(self, post_id: int, user_id: int) -> bool:
        with self._get_session() as session:
            like = session.query(Like).filter(Like.post_id == post_id, Like.user_id == user_id).first()
            if not like:
                return False

            session.delete(like)
            session.commit()
            return True

    def follow_user(self, follower_id: int, followed_id: int) -> bool:
        with self._get_session() as session:
            if follower_id == followed_id:
                return False
            if not self._user_exists(session, follower_id) or not self._user_exists(session, followed_id):
                return False

            existing = session.query(Follow).filter(
                Follow.follower_id == follower_id,
                Follow.followed_id == followed_id,
            ).first()
            if existing:
                return False

            follow = Follow(follower_id=follower_id, followed_id=followed_id)
            session.add(follow)
            session.commit()
            return True

    def unfollow_user(self, follower_id: int, followed_id: int) -> bool:
        with self._get_session() as session:
            follow = session.query(Follow).filter(
                Follow.follower_id == follower_id,
                Follow.followed_id == followed_id,
            ).first()
            if not follow:
                return False

            session.delete(follow)
            session.commit()
            return True

    def get_feed(self, user_id: int, limit: int = 20):
        with self._get_session() as session:
            if not self._user_exists(session, user_id):
                return None

            followed_ids = select(Follow.followed_id).where(Follow.follower_id == user_id)
            return (
                session.query(Post)
                .filter(or_(Post.user_id == user_id, Post.user_id.in_(followed_ids)))
                .order_by(Post.created_at.desc())
                .limit(limit)
                .all()
            )