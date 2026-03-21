"""
Tests for the main Flask application.
"""
# pylint: disable=redefined-outer-name

import pytest
from app import app

@pytest.fixture
def client():
    """Create a test client for the app."""
    app.config['TESTING'] = True
    with app.test_client() as testing_client:
        yield testing_client

def test_homepage(client):
    """Test that the homepage loads successfully."""
    response = client.get('/')
    assert response.status_code == 200
    assert b"Upload PDF" in response.data or b"PDF and HTML" in response.data
