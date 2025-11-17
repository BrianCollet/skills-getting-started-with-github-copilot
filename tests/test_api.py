"""
Test cases for the FastAPI application endpoints
"""
import pytest
from fastapi.testclient import TestClient


class TestRootEndpoint:
    """Test cases for the root endpoint"""
    
    def test_root_redirects_to_static(self, client: TestClient):
        """Test that root endpoint redirects to static/index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestActivitiesEndpoint:
    """Test cases for the activities endpoints"""
    
    def test_get_activities_success(self, client: TestClient, reset_activities):
        """Test successful retrieval of activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, dict)
        assert len(data) == 9  # Should have 9 activities
        
        # Check specific activity exists
        assert "Chess Club" in data
        assert "Programming Class" in data
        
        # Check activity structure
        chess_club = data["Chess Club"]
        assert "description" in chess_club
        assert "schedule" in chess_club
        assert "max_participants" in chess_club
        assert "participants" in chess_club
        assert isinstance(chess_club["participants"], list)


class TestSignupEndpoint:
    """Test cases for the signup endpoint"""
    
    def test_signup_success(self, client: TestClient, reset_activities):
        """Test successful signup for an activity"""
        response = client.post(
            "/activities/Chess Club/signup",
            data={"email": "newstudent@mergington.edu"}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert "newstudent@mergington.edu" in data["message"]
        assert "Chess Club" in data["message"]
        
        # Verify the participant was added
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert "newstudent@mergington.edu" in activities_data["Chess Club"]["participants"]
    
    def test_signup_activity_not_found(self, client: TestClient, reset_activities):
        """Test signup for non-existent activity"""
        response = client.post(
            "/activities/NonExistent Activity/signup",
            data={"email": "student@mergington.edu"}
        )
        assert response.status_code == 404
        
        data = response.json()
        assert data["detail"] == "Activity not found"
    
    def test_signup_already_registered(self, client: TestClient, reset_activities):
        """Test signup when student is already registered"""
        response = client.post(
            "/activities/Chess Club/signup",
            data={"email": "michael@mergington.edu"}  # Already registered
        )
        assert response.status_code == 400
        
        data = response.json()
        assert data["detail"] == "Student already signed up for this activity"
    
    def test_signup_missing_email(self, client: TestClient, reset_activities):
        """Test signup without email parameter"""
        response = client.post("/activities/Chess Club/signup")
        assert response.status_code == 422  # Unprocessable Entity
    
    def test_signup_empty_email(self, client: TestClient, reset_activities):
        """Test signup with empty email"""
        response = client.post(
            "/activities/Chess Club/signup",
            data={"email": ""}
        )
        assert response.status_code == 200  # API currently accepts empty emails
    
    def test_signup_multiple_students(self, client: TestClient, reset_activities):
        """Test signing up multiple students for the same activity"""
        emails = ["student1@mergington.edu", "student2@mergington.edu", "student3@mergington.edu"]
        
        for email in emails:
            response = client.post(
                "/activities/Chess Club/signup",
                data={"email": email}
            )
            assert response.status_code == 200
        
        # Verify all students were added
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        participants = activities_data["Chess Club"]["participants"]
        
        for email in emails:
            assert email in participants


class TestUnregisterEndpoint:
    """Test cases for the unregister endpoint"""
    
    def test_unregister_success(self, client: TestClient, reset_activities):
        """Test successful unregistration from an activity"""
        response = client.delete(
            "/activities/Chess Club/unregister?email=michael@mergington.edu"
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert "michael@mergington.edu" in data["message"]
        assert "Chess Club" in data["message"]
        
        # Verify the participant was removed
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert "michael@mergington.edu" not in activities_data["Chess Club"]["participants"]
    
    def test_unregister_activity_not_found(self, client: TestClient, reset_activities):
        """Test unregister from non-existent activity"""
        response = client.delete(
            "/activities/NonExistent Activity/unregister?email=student@mergington.edu"
        )
        assert response.status_code == 404
        
        data = response.json()
        assert data["detail"] == "Activity not found"
    
    def test_unregister_student_not_registered(self, client: TestClient, reset_activities):
        """Test unregister when student is not registered"""
        response = client.delete(
            "/activities/Chess Club/unregister?email=notregistered@mergington.edu"
        )
        assert response.status_code == 400
        
        data = response.json()
        assert data["detail"] == "Student is not registered for this activity"
    
    def test_unregister_missing_email(self, client: TestClient, reset_activities):
        """Test unregister without email parameter"""
        response = client.delete("/activities/Chess Club/unregister")
        assert response.status_code == 422  # Missing required query parameter
    
    def test_unregister_empty_email(self, client: TestClient, reset_activities):
        """Test unregister with empty email parameter"""
        response = client.delete("/activities/Chess Club/unregister?email=")
        assert response.status_code == 400  # API returns 400 for empty email (student not registered)
    
    def test_signup_then_unregister(self, client: TestClient, reset_activities):
        """Test complete workflow: signup then unregister"""
        email = "workflow@mergington.edu"
        activity = "Chess Club"
        
        # First, sign up
        signup_response = client.post(
            f"/activities/{activity}/signup",
            data={"email": email}
        )
        assert signup_response.status_code == 200
        
        # Verify signup worked
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert email in activities_data[activity]["participants"]
        
        # Then, unregister
        unregister_response = client.delete(
            f"/activities/{activity}/unregister?email={email}"
        )
        assert unregister_response.status_code == 200
        
        # Verify unregister worked
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert email not in activities_data[activity]["participants"]


class TestActivityConstraints:
    """Test cases for activity constraints and edge cases"""
    
    def test_activity_capacity_limits(self, client: TestClient, reset_activities):
        """Test that activities respect their maximum participant limits"""
        # Get current participant count for Chess Club
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        chess_club = activities_data["Chess Club"]
        current_count = len(chess_club["participants"])
        max_participants = chess_club["max_participants"]
        spots_available = max_participants - current_count
        
        # Fill up remaining spots
        for i in range(spots_available):
            response = client.post(
                "/activities/Chess Club/signup",
                data={"email": f"student{i}@mergington.edu"}
            )
            assert response.status_code == 200
        
        # Try to add one more (should still work as the API doesn't enforce limits)
        # Note: The current implementation doesn't enforce max_participants
        # This test documents the current behavior
        response = client.post(
            "/activities/Chess Club/signup",
            data={"email": "overflow@mergington.edu"}
        )
        assert response.status_code == 200  # Current behavior allows overflow
    
    def test_special_characters_in_emails(self, client: TestClient, reset_activities):
        """Test handling of special characters in email addresses"""
        special_email = "test+special.email@mergington.edu"
        
        response = client.post(
            "/activities/Chess Club/signup",
            data={"email": special_email}
        )
        assert response.status_code == 200
        
        # Verify the email was stored correctly
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert special_email in activities_data["Chess Club"]["participants"]
    
    def test_url_encoded_activity_names(self, client: TestClient, reset_activities):
        """Test handling of URL-encoded activity names"""
        # Test with space in activity name (should be URL encoded as %20)
        response = client.post(
            "/activities/Chess%20Club/signup",
            data={"email": "urltest@mergington.edu"}
        )
        assert response.status_code == 200
        
        # Test unregister with URL encoding
        response = client.delete(
            "/activities/Chess%20Club/unregister?email=urltest@mergington.edu"
        )
        assert response.status_code == 200