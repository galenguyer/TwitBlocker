from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship

from . import db


class BlockedUser(db.Model):
    __tablename__ = 'blocks'
    blocker_id = Column(String(32), primary_key=True)
    blocked_id = Column(String(32), nullable=False)
    reason = Column(String(256))

    @classmethod
    def get_for_user(cls, user_id: str):
        return cls.query.filter_by(blocker_id=user_id).all()

    @classmethod
    def get_all(cls):
        return cls.query.all()


class AuthUser(db.Model):
    user_id = Column(String(32), primary_key=True)
    name = Column(String(32))
    screen_name = Column(String(32))
    oauth_token = Column(String(64))
    oauth_token_secret = Column(String(64))

    @classmethod
    def by_token(cls, oauth_token: str):
        return cls.query.filter_by(oauth_token=oauth_token).first()

    def get_oauth_token(self):
        return self.oauth_token

    def get_oauth_token_secret(self):
        return self.oauth_token_secret
