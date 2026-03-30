document.addEventListener("DOMContentLoaded", () => {
  const isLoggedIn = localStorage.getItem("isLoggedIn");
  const userRole = localStorage.getItem("currentUserRole");
  const userDataStr = localStorage.getItem("userData");

  if (!isLoggedIn || userRole !== "Bachelor") {
    alert("Access Denied! You must be logged in as a Bachelor.");
    window.location.href = "login.html";
    return;
  }

  const loginBtn = document.querySelector(".login-btn");
  if (loginBtn) {
    loginBtn.addEventListener("click", (e) => {
      e.preventDefault();
      localStorage.clear();
      window.location.href = "login.html";
    });
  }

  if (userDataStr) {
    const userData = JSON.parse(userDataStr);
    const userNameElement = document.getElementById("userName");
    if (userNameElement) {
      userNameElement.textContent = userData.name || "Bachelor";
    }
    fetchUserBookings(userData.id);
  }
});

async function fetchUserBookings(userId) {
  try {
    const apiBase = window.API_CONFIG
      ? window.API_CONFIG.BASE_URL
      : "http://127.0.0.1:8000";
    const response = await fetch(
      `${apiBase}/user-dashboard/my-bookings?user_id=${userId}`,
    );
    if (!response.ok) throw new Error("Failed to load bookings");

    const bookings = await response.json();
    renderBookings(bookings);
  } catch (error) {
    console.error("Error:", error);
    const tbody = document.getElementById("bookingsTableBody");
    if (tbody) {
      tbody.innerHTML = `<tr><td colspan="4" class="no-data-cell text-error">Error loading data.</td></tr>`;
    }
  }
}

function renderBookings(bookings) {
  const tbody = document.getElementById("bookingsTableBody");
  if (!tbody) return;
  tbody.innerHTML = "";

  // Update Stats
  const totalRequests = document.getElementById("totalRequests");
  const pendingRequests = document.getElementById("pendingRequests");
  const confirmedRequests = document.getElementById("confirmedRequests");
  const rejectedRequests = document.getElementById("rejectedRequests");

  if (totalRequests) totalRequests.textContent = bookings.length;

  const requestedCount = bookings.filter((b) => {
    const s = (b.status || "").toLowerCase();
    return s === "requested" || s === "pending";
  }).length;
  if (pendingRequests) {
    pendingRequests.textContent = requestedCount;
  }

  const approvedCount = bookings.filter((b) => {
    const s = (b.status || "").toLowerCase();
    return s === "approved" || s === "confirmed";
  }).length;
  if (confirmedRequests) {
    confirmedRequests.textContent = approvedCount;
  }

  const rejectedCount = bookings.filter((b) => {
    const s = (b.status || "").toLowerCase();
    return s === "rejected";
  }).length;
  if (rejectedRequests) {
    rejectedRequests.textContent = rejectedCount;
  }

  if (bookings.length === 0) {
    tbody.innerHTML = `<tr><td colspan="4" class="no-data-cell">You haven't made any booking requests yet. <a href="find_room.html">Find a room now!</a></td></tr>`;
    return;
  }

  bookings.reverse().forEach((booking) => {
    const row = document.createElement("tr");
    const statusClass = `status-${booking.status.toLowerCase()}`;

    row.innerHTML = `
            <td><strong>${booking.room_title}</strong></td>
            <td>${booking.room_location}</td>
            <td><span class="status-badge ${statusClass}">${booking.status}</span></td>
            <td>
                <button class="btn-view-details" onclick="window.location.href='room_details.html?id=${booking.room_id}'">View Room</button>
                <button class="btn-cancel-request" onclick="cancelRequest(${booking.id})">Cancel</button>
            </td>
        `;
    tbody.appendChild(row);
  });
}
async function cancelRequest(bookingId) {
  if (!confirm("Are you sure you want to cancel this booking request?")) return;

  const userDataStr = localStorage.getItem("userData");
  if (!userDataStr) return;
  const userData = JSON.parse(userDataStr);

  try {
    const apiBase = window.API_CONFIG
      ? window.API_CONFIG.BASE_URL
      : "http://127.0.0.1:8000";
    const response = await fetch(
      `${apiBase}/booking/${bookingId}?user_id=${userData.id}`,
      {
        method: "DELETE",
      },
    );

    if (response.ok) {
      alert("Booking request cancelled successfully!");
      location.reload(); // Refresh to show updated list
    } else {
      const data = await response.json();
      alert("Error: " + (data.detail || "Failed to cancel request"));
    }
  } catch (error) {
    console.error("Error:", error);
    alert("Connection error.");
  }
}
window.cancelRequest = cancelRequest;
