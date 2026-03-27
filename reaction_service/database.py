import uuid
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Enum, UniqueConstraint

db = SQLAlchemy()

class CommentReaction(db.Model):
    __tablename__ = 'comment_reactions'
    reaction_id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), nullable=False)
    comment_id = db.Column(db.String(36), nullable=False)
    reaction_type = db.Column(Enum('like', 'dislike', name='reaction_types'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    __table_args__ = (UniqueConstraint('user_id', 'comment_id', name='_user_comment_uc'),)

    def __repr__(self):
        return f"<CommentReaction {self.reaction_id} - User {self.user_id} reacted {self.reaction_type} to Comment {self.comment_id}>"

    def to_dict(self):
        return {
            "reaction_id": self.reaction_id,
            "user_id": self.user_id,
            "comment_id": self.comment_id,
            "reaction_type": self.reaction_type,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
