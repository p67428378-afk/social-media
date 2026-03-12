import pytest
from unittest.mock import patch
from flask import Flask
from reaction_service.config import Config
from reaction_service.database import db, CommentReaction
from reaction_service.main import app as flask_app
import uuid

@pytest.fixture(scope='module')
def app():
    flask_app.config.from_object(Config)
    flask_app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:' # Use in-memory SQLite for testing
    flask_app.config['TESTING'] = True
    with flask_app.app_context():
        db.create_all()
        yield flask_app
        db.session.remove()
        db.drop_all()

@pytest.fixture(scope='module')
def client(app):
    return app.test_client()

@pytest.fixture(autouse=True)
def run_around_tests():
    with flask_app.app_context():
        db.session.query(CommentReaction).delete()
        db.session.commit()
        yield

def generate_auth_header():
    return {'Authorization': 'Bearer test_token'}

def test_post_like_reaction(client):
    comment_id = str(uuid.uuid4())
    user_id = str(uuid.uuid4())
    response = client.post(f'/api/comments/{comment_id}/react', json={'user_id': user_id, 'reaction_type': 'like'}, headers=generate_auth_header())
    assert response.status_code == 200
    data = response.get_json()
    assert data['message'] == 'Reaction updated successfully'
    assert data['reaction']['comment_id'] == comment_id
    assert data['reaction']['user_id'] == user_id
    assert data['reaction']['reaction_type'] == 'like'

    # Verify count
    counts_response = client.get(f'/api/comments/{comment_id}/reactions')
    counts_data = counts_response.get_json()
    assert counts_data['likes'] == 1
    assert counts_data['dislikes'] == 0

def test_post_dislike_reaction(client):
    comment_id = str(uuid.uuid4())
    user_id = str(uuid.uuid4())
    response = client.post(f'/api/comments/{comment_id}/react', json={'user_id': user_id, 'reaction_type': 'dislike'}, headers=generate_auth_header())
    assert response.status_code == 200
    data = response.get_json()
    assert data['message'] == 'Reaction updated successfully'
    assert data['reaction']['comment_id'] == comment_id
    assert data['reaction']['user_id'] == user_id
    assert data['reaction']['reaction_type'] == 'dislike'

    # Verify count
    counts_response = client.get(f'/api/comments/{comment_id}/reactions')
    counts_data = counts_response.get_json()
    assert counts_data['likes'] == 0
    assert counts_data['dislikes'] == 1

def test_toggle_reaction_like_to_dislike(client):
    comment_id = str(uuid.uuid4())
    user_id = str(uuid.uuid4())
    # First like
    client.post(f'/api/comments/{comment_id}/react', json={'user_id': user_id, 'reaction_type': 'like'}, headers=generate_auth_header())
    # Then dislike
    response = client.post(f'/api/comments/{comment_id}/react', json={'user_id': user_id, 'reaction_type': 'dislike'}, headers=generate_auth_header())
    assert response.status_code == 200
    data = response.get_json()
    assert data['message'] == 'Reaction updated successfully'
    assert data['reaction']['reaction_type'] == 'dislike'

    # Verify count
    counts_response = client.get(f'/api/comments/{comment_id}/reactions')
    counts_data = counts_response.get_json()
    assert counts_data['likes'] == 0
    assert counts_data['dislikes'] == 1

def test_remove_reaction_by_clicking_same_reaction_again(client):
    comment_id = str(uuid.uuid4())
    user_id = str(uuid.uuid4())
    # First like
    client.post(f'/api/comments/{comment_id}/react', json={'user_id': user_id, 'reaction_type': 'like'}, headers=generate_auth_header())
    # Click like again to remove
    response = client.post(f'/api/comments/{comment_id}/react', json={'user_id': user_id, 'reaction_type': 'like'}, headers=generate_auth_header())
    assert response.status_code == 200
    data = response.get_json()
    assert data['message'] == 'Reaction removed successfully'

    # Verify count
    counts_response = client.get(f'/api/comments/{comment_id}/reactions')
    counts_data = counts_response.get_json()
    assert counts_data['likes'] == 0
    assert counts_data['dislikes'] == 0

def test_delete_reaction(client):
    comment_id = str(uuid.uuid4())
    user_id = str(uuid.uuid4())
    # First like
    client.post(f'/api/comments/{comment_id}/react', json={'user_id': user_id, 'reaction_type': 'like'}, headers=generate_auth_header())
    # Then delete
    response = client.delete(f'/api/comments/{comment_id}/react', json={'user_id': user_id}, headers=generate_auth_header())
    assert response.status_code == 200
    data = response.get_json()
    assert data['message'] == 'Reaction removed successfully'

    # Verify count
    counts_response = client.get(f'/api/comments/{comment_id}/reactions')
    counts_data = counts_response.get_json()
    assert counts_data['likes'] == 0
    assert counts_data['dislikes'] == 0

def test_get_reaction_counts_no_reactions(client):
    comment_id = str(uuid.uuid4())
    response = client.get(f'/api/comments/{comment_id}/reactions')
    assert response.status_code == 200 # Should return 0 likes/dislikes, not 404
    data = response.get_json()
    assert data['comment_id'] == comment_id
    assert data['likes'] == 0
    assert data['dislikes'] == 0

def test_get_reaction_counts_multiple_reactions(client):
    comment_id = str(uuid.uuid4())
    user_id_1 = str(uuid.uuid4())
    user_id_2 = str(uuid.uuid4())
    user_id_3 = str(uuid.uuid4())

    client.post(f'/api/comments/{comment_id}/react', json={'user_id': user_id_1, 'reaction_type': 'like'}, headers=generate_auth_header())
    client.post(f'/api/comments/{comment_id}/react', json={'user_id': user_id_2, 'reaction_type': 'like'}, headers=generate_auth_header())
    client.post(f'/api/comments/{comment_id}/react', json={'user_id': user_id_3, 'reaction_type': 'dislike'}, headers=generate_auth_header())

    response = client.get(f'/api/comments/{comment_id}/reactions')
    assert response.status_code == 200
    data = response.get_json()
    assert data['comment_id'] == comment_id
    assert data['likes'] == 2
    assert data['dislikes'] == 1

def test_unauthenticated_access(client):
    comment_id = str(uuid.uuid4())
    user_id = str(uuid.uuid4())
    response = client.post(f'/api/comments/{comment_id}/react', json={'user_id': user_id, 'reaction_type': 'like'})
    assert response.status_code == 401
    assert response.get_json()['message'] == 'Authentication required'

def test_invalid_reaction_type(client):
    comment_id = str(uuid.uuid4())
    user_id = str(uuid.uuid4())
    response = client.post(f'/api/comments/{comment_id}/react', json={'user_id': user_id, 'reaction_type': 'invalid'}, headers=generate_auth_header())
    assert response.status_code == 400
    assert 'Invalid reaction data' in response.get_json()['message']
