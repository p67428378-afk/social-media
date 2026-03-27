from flask import Flask, request, jsonify
from pydantic import ValidationError
from reaction_service.config import Config
from reaction_service.database import db, CommentReaction
from reaction_service.schemas import ReactionRequest, ReactionRemoveRequest, ReactionResponse, ReactionCountsResponse
from reaction_service.services import ReactionService

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

# Placeholder for a simple in-memory cache for reaction counts
# In a real application, this would be Redis or a similar distributed cache
reaction_counts_cache = {}

# Placeholder for authentication decorator
def authenticate_user(f):
    # In a real application, this would validate a JWT or session token
    # For now, it just checks for a basic Authorization header
    def decorated_function(*args, **kwargs):
        if "Authorization" not in request.headers:
            return jsonify({"message": "Authentication required"}), 401
        # Further validation (e.g., JWT decoding) would go here
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__ # Preserve original function name
    return decorated_function

@app.before_request
def create_tables():
    with app.app_context():
        db.create_all()

@app.route("/api/comments/<uuid:comment_id>/react", methods=["POST"])
@authenticate_user
def react_to_comment(comment_id):
    try:
        reaction_data = ReactionRequest(**request.json)
    except ValidationError as e:
        return jsonify({"message": "Invalid reaction data", "errors": e.errors()}), 400

    reaction = ReactionService.process_reaction(str(comment_id), reaction_data)

    # Invalidate cache for this comment
    reaction_counts_cache.pop(str(comment_id), None)

    if reaction is None:
        return jsonify({"message": "Reaction removed successfully"}), 200
    else:
        return jsonify({"message": "Reaction updated successfully", "reaction": ReactionResponse.model_validate(reaction.to_dict()).model_dump()}), 200

@app.route("/api/comments/<uuid:comment_id>/react", methods=["DELETE"])
@authenticate_user
def remove_reaction_from_comment(comment_id):
    try:
        remove_data = ReactionRemoveRequest(**request.json)
    except ValidationError as e:
        return jsonify({"message": "Invalid request data", "errors": e.errors()}), 400

    if ReactionService.remove_reaction(str(comment_id), remove_data):
        # Invalidate cache for this comment
        reaction_counts_cache.pop(str(comment_id), None)
        return jsonify({"message": "Reaction removed successfully"}), 200
    return jsonify({"message": "Reaction not found or not owned by user"}), 404

@app.route("/api/comments/<uuid:comment_id>/reactions", methods=["GET"])
def get_comment_reactions(comment_id):
    comment_id_str = str(comment_id)
    if comment_id_str in reaction_counts_cache:
        return jsonify(reaction_counts_cache[comment_id_str]), 200

    counts = ReactionService.get_reaction_counts(comment_id_str)
    if counts:
        response_data = ReactionCountsResponse(comment_id=comment_id_str, likes=counts["likes"], dislikes=counts["dislikes"])
        reaction_counts_cache[comment_id_str] = response_data.model_dump()
        return jsonify(response_data.model_dump()), 200
    return jsonify({"message": "Comment not found or no reactions yet"}), 404

if __name__ == "__main__":
    app.run(debug=True)
