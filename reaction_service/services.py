from sqlalchemy.exc import IntegrityError
from reaction_service.database import db, CommentReaction
from reaction_service.schemas import ReactionRequest, ReactionRemoveRequest

class ReactionService:
    @staticmethod
    def process_reaction(comment_id: str, reaction_data: ReactionRequest):
        user_id = reaction_data.user_id
        reaction_type = reaction_data.reaction_type

        existing_reaction = CommentReaction.query.filter_by(user_id=user_id, comment_id=comment_id).first()

        if existing_reaction:
            if existing_reaction.reaction_type == reaction_type:
                # User clicked the same reaction again, so remove it
                db.session.delete(existing_reaction)
                db.session.commit()
                return None  # Reaction removed
            else:
                # User changed reaction type (e.g., like to dislike)
                existing_reaction.reaction_type = reaction_type
                db.session.commit()
                return existing_reaction  # Reaction updated
        else:
            # No existing reaction, create a new one
            new_reaction = CommentReaction(user_id=user_id, comment_id=comment_id, reaction_type=reaction_type)
            db.session.add(new_reaction)
            try:
                db.session.commit()
                return new_reaction  # Reaction created
            except IntegrityError:
                db.session.rollback()
                # This can happen in a race condition if two identical reactions are tried to be added concurrently
                # Re-fetch and return the existing one, or handle as appropriate for idempotency
                return CommentReaction.query.filter_by(user_id=user_id, comment_id=comment_id).first()

    @staticmethod
    def remove_reaction(comment_id: str, remove_data: ReactionRemoveRequest):
        user_id = remove_data.user_id
        reaction = CommentReaction.query.filter_by(user_id=user_id, comment_id=comment_id).first()
        if reaction:
            db.session.delete(reaction)
            db.session.commit()
            return True
        return False

    @staticmethod
    def get_reaction_counts(comment_id: str):
        likes = CommentReaction.query.filter_by(comment_id=comment_id, reaction_type='like').count()
        dislikes = CommentReaction.query.filter_by(comment_id=comment_id, reaction_type='dislike').count()
        return {"comment_id": comment_id, "likes": likes, "dislikes": dislikes}
