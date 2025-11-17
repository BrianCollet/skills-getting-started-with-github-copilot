document.addEventListener("DOMContentLoaded", () => {
  loadActivities();

  const signupForm = document.getElementById("signup-form");
  signupForm.addEventListener("submit", handleSignup);
});

// Load activities from the server
async function loadActivities() {
  try {
    const response = await fetch("/activities");
    const activities = await response.json();

    displayActivities(activities);
    populateActivitySelect(activities);
  } catch (error) {
    console.error("Error loading activities:", error);
    document.getElementById("activities-list").innerHTML =
      '<p class="error">Error loading activities. Please try again later.</p>';
  }
}

// Display activities on the page
function displayActivities(activities) {
  const activitiesList = document.getElementById("activities-list");

  if (Object.keys(activities).length === 0) {
    activitiesList.innerHTML = "<p>No activities available at this time.</p>";
    return;
  }

  activitiesList.innerHTML = "";

  for (const [name, activity] of Object.entries(activities)) {
    const activityCard = document.createElement("div");
    activityCard.className = "activity-card";

    const participantsList = activity.participants
      .map((email) => `<li>${email}</li>`)
      .join("");

    const spotsRemaining = activity.max_participants - activity.participants.length;

    activityCard.innerHTML = `
            <h4>${name}</h4>
            <p><strong>Description:</strong> ${activity.description}</p>
            <p><strong>Schedule:</strong> ${activity.schedule}</p>
            <p><strong>Spots:</strong> ${activity.participants.length}/${activity.max_participants} filled 
               <span class="spots-remaining">(${spotsRemaining} spots remaining)</span></p>
            <div class="participants-section">
                <h5>Current Participants:</h5>
                ${activity.participants.length > 0 ? 
                    `<ul class="participants-list">${participantsList}</ul>` : 
                    '<p class="no-participants">No participants yet - be the first to sign up!</p>'
                }
            </div>
        `;

    activitiesList.appendChild(activityCard);
  }
}

// Populate the activity select dropdown
function populateActivitySelect(activities) {
  const activitySelect = document.getElementById("activity");

  // Clear existing options except the first one
  activitySelect.innerHTML = '<option value="">-- Select an activity --</option>';

  for (const name of Object.keys(activities)) {
    const option = document.createElement("option");
    option.value = name;
    option.textContent = name;
    activitySelect.appendChild(option);
  }
}

// Handle signup form submission
async function handleSignup(event) {
  event.preventDefault();

  const email = document.getElementById("email").value;
  const activityName = document.getElementById("activity").value;
  const messageDiv = document.getElementById("message");

  if (!email || !activityName) {
    showMessage("Please fill in all fields.", "error");
    return;
  }

  try {
    const response = await fetch(
      `/activities/${encodeURIComponent(activityName)}/signup`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
        },
        body: `email=${encodeURIComponent(email)}`,
      }
    );

    const result = await response.json();

    if (response.ok) {
      showMessage(result.message, "success");
      document.getElementById("signup-form").reset();
      // Reload activities to show updated participant list
      loadActivities();
    } else {
      showMessage(result.detail || "An error occurred during signup.", "error");
    }
  } catch (error) {
    console.error("Error during signup:", error);
    showMessage("Network error. Please try again later.", "error");
  }
}

// Show message to the user
function showMessage(message, type) {
  const messageDiv = document.getElementById("message");
  messageDiv.textContent = message;
  messageDiv.className = `message ${type}`;
  messageDiv.classList.remove("hidden");

  // Hide message after 5 seconds
  setTimeout(() => {
    messageDiv.classList.add("hidden");
  }, 5000);
}
