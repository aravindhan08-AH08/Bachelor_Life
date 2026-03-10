document.addEventListener("DOMContentLoaded", () => {
  const isLoggedIn = localStorage.getItem("isLoggedIn");
  const userRole = localStorage.getItem("currentUserRole");

  if (!isLoggedIn || userRole !== "Owner") {
    alert("Access Denied! You must be logged in as an Owner.");
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

  renderDashboard();
});

async function renderDashboard() {
  const userEmail = localStorage.getItem("userEmail");
  if (!userEmail) return;

  try {
    const apiBase = window.API_CONFIG
      ? window.API_CONFIG.BASE_URL
      : "http://127.0.0.1:8000";
    const response = await fetch(
      `${apiBase}/owner/dashboard?owner_email=${userEmail}`,
    );
    if (!response.ok) throw new Error("Failed to load dashboard data");

    const data = await response.json();

    // Update Stats
    document.getElementById("ownerName").textContent =
      data.owner_name || "Owner";
    document.getElementById("totalRooms").textContent = data.total_rooms;
    document.getElementById("activeListings").textContent = data.rooms.filter(
      (r) => r.is_available,
    ).length;
    document.getElementById("totalBookings").textContent =
      data.bookings_received.length;

    // Render Rooms
    const listingsContainer = document.getElementById("listingsContainer");
    listingsContainer.innerHTML = "";

    if (data.rooms.length === 0) {
      listingsContainer.innerHTML = `<div class="empty-state-container">
                <h3>No properties yet!</h3>
                <a href="post_room.html" class="post-new-btn">Post Now</a>
            </div>`;
    } else {
      data.rooms.forEach((room) => {
        const card = document.createElement("div");
        card.classList.add("listing-card");
        let imgSrc = "https://placehold.co/340x200?text=No+Image";
        // Robust parsing for image_url (handles arrays, JSON strings, Python strings)
        let images = [];
        try {
          const rawImages = room.image_url;
          if (Array.isArray(rawImages)) {
            images = rawImages;
          } else if (typeof rawImages === 'string' && rawImages.trim() !== '') {
            let str = rawImages.trim();
            if (str.startsWith('[') && str.endsWith(']')) {
              try {
                images = JSON.parse(str);
              } catch (e) {
                try {
                  images = JSON.parse(str.replace(/'/g, '"'));
                } catch (e2) {
                  try {
                    const content = str.substring(1, str.length - 1);
                    images = content.split(',').map(s => s.trim().replace(/^['"]|['"]$/g, ''));
                  } catch (e3) { images = [str]; }
                }
              }
            } else {
              images = [str];
            }
          }
        } catch (err) {
          images = [];
        }

        const getCleanPath = (path) => {
          if (!path) return "";
          let pathStr = path.toString().trim();
          // Remove extra quotes or escaped quotes
          pathStr = pathStr.replace(/^['"]|['"]$/g, '').replace(/\\"/g, '"');

          if (pathStr.startsWith("data:")) return pathStr;
          if (pathStr.startsWith("http")) return pathStr;

          // Remove any accidental folder prefixes if they exist in the path string
          let cleanP = pathStr.replace(/\\/g, "/");
          cleanP = cleanP.replace(/^Bachelor_life_backend\//, "")
            .replace(/^Bachelor_life_frontend\//, "")
            .replace(/^\/+/, "");

          // Final absolute URL construction
          // Handle spaces with encodeURI
          let finalUrl = `${apiBase}/${cleanP}`;
          finalUrl = encodeURI(finalUrl);
          console.log("DEBUG: Final Image URL (Dashboard):", finalUrl);
          return finalUrl;
        };

        imgSrc = getCleanPath(images[0] || "");

        card.innerHTML = `
                    <div class="listing-image">
                        <img src="${imgSrc}" onerror="this.src='https://placehold.co/340x200?text=Image+Not+Found'">
                    </div>
                    <div class="listing-content">
                        <h3 class="listing-title">${room.title}</h3>
                        <div class="listing-details">
                            <span>${room.location}</span>
                            <span class="listing-price">₹${room.rent}/mo</span>
                        </div>
                        <div class="listing-details">
                             <span>${room.room_type}</span>
                             <span>Gender: ${room.gender || "Any"}</span>
                             <span class="status-badge ${room.is_available ? "status-confirmed" : "status-rejected"}">
                                 ${room.is_available ? "Active" : "Full"}
                             </span>
                        </div>
                        <div class="listing-actions">
                            <button class="btn-action btn-edit" onclick="window.location.href='post_room.html?id=${room.id}'">Edit</button>
                            <button class="btn-action btn-delete" onclick="deleteRoom(${room.id})">Delete</button>
                        </div>
                    </div>
                `;
        listingsContainer.appendChild(card);
      });
    }

    // Render Bookings
    const bookingsBody = document.getElementById("bookingsTableBody");
    bookingsBody.innerHTML = "";

    if (data.bookings_received.length === 0) {
      bookingsBody.innerHTML = `<tr><td colspan="4" class="no-data-cell">No requests found.</td></tr>`;
    } else {
      data.bookings_received.forEach((booking) => {
        const room = data.rooms.find((r) => r.id === booking.room_id) || {
          title: "Unknown Room",
        };

        const row = document.createElement("tr");
        let actionHtml = "";

        if (booking.status === "Requested") {
          actionHtml = `
                        <div class="d-flex-gap-5">
                            <button class="btn-approve-small" onclick="approveBooking(${booking.id})">Approve</button>
                            <button class="btn-reject-small" onclick="rejectBooking(${booking.id})">Reject</button>
                            <button class="btn-contact-small" onclick="viewContact('${booking.user_name}', '${booking.user_phone}', '${booking.user_email}')">Contact</button>
                        </div>
                    `;
        } else {
          actionHtml = `<button class="btn-contact-small" onclick="viewContact('${booking.user_name}', '${booking.user_phone}', '${booking.user_email}')">Contact</button>`;
        }

        row.innerHTML = `
                    <td><strong>${room.title}</strong></td>
                    <td>${booking.user_name}</td>
                    <td><span class="status-badge status-${booking.status.toLowerCase()}">${booking.status}</span></td>
                    <td>${actionHtml}</td>
                `;
        bookingsBody.appendChild(row);
      });
    }
  } catch (error) {
    console.error("Dashboard error:", error);
    document.getElementById("listingsContainer").innerHTML =
      `<p class="text-error-center">Error loading dashboard data. Please check if the backend is running.</p>`;
  }
}

async function deleteRoom(id) {
  if (!confirm("Delete this listing?")) return;
  const userEmail = localStorage.getItem("userEmail");
  try {
    const apiBase = window.API_CONFIG
      ? window.API_CONFIG.BASE_URL
      : "http://127.0.0.1:8000";
    const response = await fetch(
      `${apiBase}/rooms/${id}?owner_email=${userEmail}`,
      {
        method: "DELETE",
      },
    );
    if (response.ok) {
      alert("Room deleted!");
      renderDashboard();
    } else {
      alert("Failed to delete room");
    }
  } catch (e) {
    console.error(e);
    alert("Error deleting room");
  }
}

async function approveBooking(id) {
  if (!confirm("Approve this request?")) return;
  const userEmail = localStorage.getItem("userEmail");

  try {
    const apiBase = window.API_CONFIG
      ? window.API_CONFIG.BASE_URL
      : "http://127.0.0.1:8000";
    const response = await fetch(
      `${apiBase}/owner/dashboard/approve-booking/${id}?owner_email=${userEmail}`,
      {
        method: "PUT",
      },
    );
    if (response.ok) {
      const resData = await response.json();
      alert(resData.message || "Request Approved!");
      renderDashboard();
    } else {
      const err = await response.json();
      alert("Error: " + err.detail);
    }
  } catch (e) {
    console.error(e);
    alert("Error approving booking");
  }
}

async function rejectBooking(id) {
  if (!confirm("Reject this request?")) return;
  const userEmail = localStorage.getItem("userEmail");

  try {
    const apiBase = window.API_CONFIG
      ? window.API_CONFIG.BASE_URL
      : "http://127.0.0.1:8000";
    const response = await fetch(
      `${apiBase}/owner/dashboard/reject-booking/${id}?owner_email=${userEmail}`,
      {
        method: "PUT",
      },
    );
    if (response.ok) {
      alert("Request Rejected!");
      renderDashboard();
    } else {
      const err = await response.json();
      alert("Error: " + err.detail);
    }
  } catch (e) {
    console.error(e);
    alert("Error rejecting booking");
  }
}

function viewContact(name, phone, email) {
  alert(`Tenant Details:\n\nName: ${name}\nPhone: ${phone}\nEmail: ${email}`);
}
