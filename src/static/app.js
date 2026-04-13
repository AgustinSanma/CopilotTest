document.addEventListener("DOMContentLoaded", () => {
  const activitiesList = document.getElementById("activities-list");
  const activitySelect = document.getElementById("activity");
  const signupForm = document.getElementById("signup-form");
  const messageDiv = document.getElementById("message");
  const defaultActivityOption = activitySelect.innerHTML;

  function showMessage(text, type) {
    messageDiv.textContent = text;
    messageDiv.classList.remove("success", "error");
    messageDiv.classList.add(type);
    messageDiv.classList.remove("hidden");

    window.clearTimeout(showMessage.timeoutId);
    showMessage.timeoutId = window.setTimeout(() => {
      messageDiv.classList.add("hidden");
    }, 5000);
  }

  function createParticipantItem(participant, activityName) {
    const li = document.createElement("li");
    li.className = "participant-row";

    const span = document.createElement("span");
    span.className = "participant-email";
    span.textContent = participant;

    const button = document.createElement("button");
    button.type = "button";
    button.className = "participant-delete-button";
    button.dataset.activity = activityName;
    button.dataset.email = participant;
    button.setAttribute("aria-label", `Remove ${participant} from ${activityName}`);
    button.title = "Remove participant";

    const icon = document.createElement("span");
    icon.setAttribute("aria-hidden", "true");
    icon.textContent = "\u00d7";

    button.appendChild(icon);
    li.appendChild(span);
    li.appendChild(button);
    return li;
  }

  // Function to fetch activities from API
  async function fetchActivities() {
    try {
      const response = await fetch("/activities", { cache: "no-store" });
      const activities = await response.json();

      // Clear loading message
      activitiesList.innerHTML = "";
      activitySelect.innerHTML = defaultActivityOption;

      // Populate activities list
      Object.entries(activities).forEach(([name, details]) => {
        const activityCard = document.createElement("div");
        activityCard.className = "activity-card";

        const spotsLeft = details.max_participants - details.participants.length;

        // Build card structure using DOM APIs to avoid XSS
        const header = document.createElement("div");
        header.className = "activity-card-header";

        const h4 = document.createElement("h4");
        h4.textContent = name;

        const badge = document.createElement("span");
        badge.className = "spots-badge";
        badge.textContent = `${spotsLeft} spots left`;

        header.appendChild(h4);
        header.appendChild(badge);

        const descP = document.createElement("p");
        descP.textContent = details.description;

        const scheduleP = document.createElement("p");
        const scheduleStrong = document.createElement("strong");
        scheduleStrong.textContent = "Schedule: ";
        scheduleP.appendChild(scheduleStrong);
        scheduleP.appendChild(document.createTextNode(details.schedule));

        const participantsSection = document.createElement("div");
        participantsSection.className = "participants-section";

        const participantsHeading = document.createElement("div");
        participantsHeading.className = "participants-heading";

        const headingStrong = document.createElement("strong");
        headingStrong.textContent = "Participants";

        const countBadge = document.createElement("span");
        countBadge.className = "participants-count";
        countBadge.textContent = details.participants.length;

        participantsHeading.appendChild(headingStrong);
        participantsHeading.appendChild(countBadge);
        participantsSection.appendChild(participantsHeading);

        if (details.participants.length > 0) {
          const ul = document.createElement("ul");
          ul.className = "participants-list";
          details.participants.forEach((participant) => {
            ul.appendChild(createParticipantItem(participant, name));
          });
          participantsSection.appendChild(ul);
        } else {
          const emptyP = document.createElement("p");
          emptyP.className = "participants-empty";
          emptyP.textContent = "No students signed up yet.";
          participantsSection.appendChild(emptyP);
        }

        activityCard.appendChild(header);
        activityCard.appendChild(descP);
        activityCard.appendChild(scheduleP);
        activityCard.appendChild(participantsSection);
        activitiesList.appendChild(activityCard);

        // Add option to select dropdown
        const option = document.createElement("option");
        option.value = name;
        option.textContent = name;
        activitySelect.appendChild(option);
      });
    } catch (error) {
      activitiesList.innerHTML = "<p>Failed to load activities. Please try again later.</p>";
      console.error("Error fetching activities:", error);
    }
  }

  activitiesList.addEventListener("click", async (event) => {
    const deleteButton = event.target.closest(".participant-delete-button");

    if (!deleteButton) {
      return;
    }

    const { activity, email } = deleteButton.dataset;

    if (!activity || !email) {
      return;
    }

    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(activity)}/participants?email=${encodeURIComponent(email)}`,
        {
          method: "DELETE",
        }
      );

      const result = await response.json();

      if (!response.ok) {
        showMessage(result.detail || "Failed to remove participant.", "error");
        return;
      }

      showMessage(result.message, "success");
      await fetchActivities();
    } catch (error) {
      showMessage("Failed to remove participant. Please try again.", "error");
      console.error("Error removing participant:", error);
    }
  });

  // Handle form submission
  signupForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const email = document.getElementById("email").value;
    const activity = document.getElementById("activity").value;

    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(activity)}/signup?email=${encodeURIComponent(email)}`,
        {
          method: "POST",
        }
      );

      const result = await response.json();

      if (response.ok) {
        showMessage(result.message, "success");
        signupForm.reset();
        await fetchActivities();
      } else {
        showMessage(result.detail || "An error occurred", "error");
      }
    } catch (error) {
      showMessage("Failed to sign up. Please try again.", "error");
      console.error("Error signing up:", error);
    }
  });

  // Initialize app
  fetchActivities();
});
