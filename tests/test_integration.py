"""
Integration tests for the FastAPI application
"""
import pytest
from fastapi.testclient import TestClient


class TestIntegration:
    """Integration test cases"""
    
    def test_complete_user_journey(self, client: TestClient, reset_activities):
        """Test a complete user journey through the application"""
        # 1. Get list of activities
        response = client.get("/activities")
        assert response.status_code == 200
        activities = response.json()
        
        # 2. Pick an activity and sign up
        activity_name = "Programming Class"
        new_email = "journey@mergington.edu"
        
        signup_response = client.post(
            f"/activities/{activity_name}/signup",
            data={"email": new_email}
        )
        assert signup_response.status_code == 200
        
        # 3. Verify the signup by checking activities again
        response = client.get("/activities")
        assert response.status_code == 200
        updated_activities = response.json()
        assert new_email in updated_activities[activity_name]["participants"]
        
        # 4. Try to sign up again (should fail)
        duplicate_response = client.post(
            f"/activities/{activity_name}/signup",
            data={"email": new_email}
        )
        assert duplicate_response.status_code == 400
        
        # 5. Unregister from the activity
        unregister_response = client.delete(
            f"/activities/{activity_name}/unregister?email={new_email}"
        )
        assert unregister_response.status_code == 200
        
        # 6. Verify unregistration
        response = client.get("/activities")
        assert response.status_code == 200
        final_activities = response.json()
        assert new_email not in final_activities[activity_name]["participants"]
    
    def test_multiple_activities_signup(self, client: TestClient, reset_activities):
        """Test signing up for multiple activities"""
        email = "multisport@mergington.edu"
        activities_to_join = ["Chess Club", "Programming Class", "Art Studio"]
        
        # Sign up for multiple activities
        for activity in activities_to_join:
            response = client.post(
                f"/activities/{activity}/signup",
                data={"email": email}
            )
            assert response.status_code == 200
        
        # Verify user is in all activities
        response = client.get("/activities")
        assert response.status_code == 200
        all_activities = response.json()
        
        for activity in activities_to_join:
            assert email in all_activities[activity]["participants"]
        
        # Unregister from one activity
        response = client.delete(
            f"/activities/Chess Club/unregister?email={email}"
        )
        assert response.status_code == 200
        
        # Verify user is still in other activities but removed from Chess Club
        response = client.get("/activities")
        assert response.status_code == 200
        updated_activities = response.json()
        
        assert email not in updated_activities["Chess Club"]["participants"]
        assert email in updated_activities["Programming Class"]["participants"]
        assert email in updated_activities["Art Studio"]["participants"]
    
    def test_concurrent_operations(self, client: TestClient, reset_activities):
        """Test handling of concurrent-like operations"""
        # Simulate multiple users signing up for the same activity
        emails = [
            "concurrent1@mergington.edu",
            "concurrent2@mergington.edu",
            "concurrent3@mergington.edu"
        ]
        
        activity = "Drama Club"
        
        # Sign up all users
        for email in emails:
            response = client.post(
                f"/activities/{activity}/signup",
                data={"email": email}
            )
            assert response.status_code == 200
        
        # Verify all are registered
        response = client.get("/activities")
        participants = response.json()[activity]["participants"]
        
        for email in emails:
            assert email in participants
        
        # Remove all users
        for email in emails:
            response = client.delete(
                f"/activities/{activity}/unregister?email={email}"
            )
            assert response.status_code == 200
        
        # Verify all are removed
        response = client.get("/activities")
        final_participants = response.json()[activity]["participants"]
        
        for email in emails:
            assert email not in final_participants