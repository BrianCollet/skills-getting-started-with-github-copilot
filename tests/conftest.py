"""
Conftest file for pytest configuration and fixtures
"""
import pytest
from fastapi.testclient import TestClient
import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from app import app, activities


@pytest.fixture
def client():
    """FastAPI test client fixture"""
    return TestClient(app)


@pytest.fixture
def reset_activities():
    """Reset activities data before each test"""
    # Store original activities
    original_activities = {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        },
        "Basketball Team": {
            "description": "Competitive basketball team with games and tournaments",
            "schedule": "Mondays and Wednesdays, 4:00 PM - 6:00 PM",
            "max_participants": 15,
            "participants": ["alex@mergington.edu", "sarah@mergington.edu"]
        },
        "Track and Field": {
            "description": "Running, jumping, and throwing events training",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
            "max_participants": 25,
            "participants": ["james@mergington.edu", "maria@mergington.edu"]
        },
        "Drama Club": {
            "description": "Theater performances and acting workshops",
            "schedule": "Thursdays, 3:30 PM - 5:30 PM",
            "max_participants": 18,
            "participants": ["lucas@mergington.edu", "emily@mergington.edu"]
        },
        "Art Studio": {
            "description": "Painting, drawing, and creative art projects",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 16,
            "participants": ["anna@mergington.edu", "david@mergington.edu"]
        },
        "Debate Team": {
            "description": "Competitive debating and public speaking skills",
            "schedule": "Tuesdays, 3:30 PM - 5:00 PM",
            "max_participants": 14,
            "participants": ["sophia@mergington.edu", "ethan@mergington.edu"]
        },
        "Science Olympiad": {
            "description": "STEM competitions and scientific research projects",
            "schedule": "Fridays, 4:00 PM - 6:00 PM",
            "max_participants": 20,
            "participants": ["rachel@mergington.edu", "thomas@mergington.edu"]
        }
    }
    
    # Reset to original state
    activities.clear()
    activities.update(original_activities)
    
    yield
    
    # Clean up after test (reset again)
    activities.clear()
    activities.update(original_activities)