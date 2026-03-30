// Global Variables
let allRooms = [];

// Auth Check Logic (Global)
async function checkAuth(roleRequired = null) {
  const isLoggedIn = localStorage.getItem("isLoggedIn");
  const userRole = localStorage.getItem("currentUserRole");

  if (!isLoggedIn) {
    alert("Please login to access this page!");
    window.location.href = "login.html";
    return false;
  }

  if (roleRequired && userRole !== roleRequired) {
    alert(`Access Denied! This feature is only for ${roleRequired}s.`);
    window.location.href = "../../index.html";
    return false;
  }
  return true;
}

// Handle Dynamic Logic
document.addEventListener("DOMContentLoaded", async () => {
  // 0. Auth Guard — Bachelor-only page
  const isLoggedIn = localStorage.getItem("isLoggedIn");
  const userRole = localStorage.getItem("currentUserRole");

  if (!isLoggedIn) {
    alert("Please login to browse rooms!");
    window.location.href = "login.html";
    return;
  }

  if (userRole === "Owner") {
    alert("Owners cannot browse rooms. Redirecting to your Dashboard.");
    window.location.href = "owner_dashboard.html";
    return;
  }

  // 1. Navbar Logic
  const loginBtn = document.querySelector(".login-btn");
  const navLinks = document.querySelector(".nav-links");

  if (isLoggedIn && loginBtn) {
    loginBtn.textContent = "Logout";
    loginBtn.href = "#";
    loginBtn.addEventListener("click", (e) => {
      e.preventDefault();
      localStorage.clear();
      alert("Logged out successfully");
      window.location.href = "login.html";
    });
  }

  if (isLoggedIn && navLinks) {
    const dashboardLink = document.createElement("a");
    if (userRole === "Owner") {
      dashboardLink.href = "owner_dashboard.html";
    } else if (userRole === "Bachelor") {
      dashboardLink.href = "bachelor_dashboard.html";
    }
    dashboardLink.textContent = "Dashboard";
    navLinks.appendChild(dashboardLink);
  }

  // 2. Load Rooms from API
  await fetchRooms();

  // 3. Check for URL Filters
  const urlParams = new URLSearchParams(window.location.search);
  const urlLocation = urlParams.get("location");
  const urlType = urlParams.get("type");
  const urlBudget = urlParams.get("budget");

  if (urlLocation)
    document.querySelector(".search-location input").value = urlLocation;
  if (urlType) document.querySelector(".dropdown-room select").value = urlType;
  if (urlBudget) {
    document.getElementById("budgetRange").value = urlBudget;
    document.querySelector(".max-budget").textContent =
      `Max Budget: ₹${urlBudget}`;
  }

  if (urlLocation || urlType || urlBudget) {
    filterRooms();
  }

  // 4. Attach Filter Listeners
  const locationInput = document.querySelector(".search-location input");
  const roomTypeSelect = document.querySelector(".dropdown-room select");
  const budgetInput = document.getElementById("budgetRange");
  const applyBtn = document.querySelector(".apply-filters-btn");
  const maxBudgetSpan = document.querySelector(".max-budget");

  if (budgetInput) {
    budgetInput.addEventListener("input", (e) => {
      maxBudgetSpan.textContent = `Max Budget: ₹${e.target.value}`;
    });
  }

  if (applyBtn) {
    applyBtn.addEventListener("click", () => {
      filterRooms();
    });
  }
});

async function fetchRooms() {
  const roomContainer = document.querySelector(".room-container");
  if (!roomContainer) return;

  // Caching Logic: 5 mins cache
  const cachedData = sessionStorage.getItem("allRoomsCache");
  const cacheTime = sessionStorage.getItem("allRoomsCacheTime");
  const now = Date.now();

  if (cachedData && cacheTime && now - cacheTime < 300000) {
    allRooms = JSON.parse(cachedData);
    renderRooms(allRooms);
    return;
  }

  roomContainer.innerHTML =
    '<p style="text-align:center; width:100%;">Loading rooms...</p>';

  try {
    const url = window.API_CONFIG
      ? `${window.API_CONFIG.BASE_URL}/rooms/`
      : "http://127.0.0.1:8000/rooms/";
    const response = await fetch(url);
    if (!response.ok) throw new Error("Failed to fetch rooms");

    allRooms = await response.json(); // Store globally

    // Set Cache
    sessionStorage.setItem("allRoomsCache", JSON.stringify(allRooms));
    sessionStorage.setItem("allRoomsCacheTime", now.toString());

    renderRooms(allRooms);
  } catch (error) {
    console.error("Error loading rooms:", error);
    roomContainer.innerHTML =
      '<p style="text-align:center; width:100%; color:red;">Failed to load rooms from server.</p>';
  }
}

function renderRooms(roomsToRender) {
  const roomContainer = document.querySelector(".room-container");
  const countSpan = document.querySelector(".available-rooms");

  roomContainer.innerHTML = "";

  if (countSpan) {
    let textNode = null;
    countSpan.childNodes.forEach((node) => {
      if (
        node.nodeType === Node.TEXT_NODE &&
        node.textContent.includes("Available Rooms")
      ) {
        textNode = node;
      }
    });
    if (textNode) {
      textNode.textContent = `Available Rooms (${roomsToRender.length})`;
    } else {
      countSpan.innerText = `Available Rooms (${roomsToRender.length})`;
    }
  }

  if (roomsToRender.length === 0) {
    roomContainer.innerHTML =
      '<p style="text-align:center; width:100%;">No rooms match your criteria.</p>';
    return;
  }

  roomsToRender.forEach((room) => {
    let imgSrc = "https://placehold.co/340x200?text=No+Image";

    // ULTRA-ROBUST Image URL Parsing
    let images = [];
    try {
      const raw = room.image_url;
      if (Array.isArray(raw)) {
        images = raw;
      } else if (typeof raw === "string" && raw.trim() !== "") {
        let str = raw.trim();
        if (str.startsWith("[") && str.endsWith("]")) {
          try {
            // Try standard JSON parse
            images = JSON.parse(str);
          } catch (e) {
            try {
              // Try fixing small quotes
              images = JSON.parse(str.replace(/'/g, '"'));
            } catch (e2) {
              // Manual split as last resort
              const content = str.substring(1, str.length - 1);
              images = content
                .split(",")
                .map((s) => s.trim().replace(/^['"]|['"]$/g, ""));
            }
          }
        } else {
          images = [str];
        }
      } else if (raw && typeof raw === "object") {
        // If it's an object but not array, try to extract values
        images = Object.values(raw);
      }
    } catch (err) {
      console.error("Error parsing room images:", err);
      images = [];
    }

    if (images.length > 0) {
      const rawPath = images[0];
      const apiBase = window.API_CONFIG
        ? window.API_CONFIG.BASE_URL
        : "http://127.0.0.1:8000";

      const getCleanPath = (path) => {
        if (!path) return "";
        let pathStr = path.toString().trim();
        // Remove extra quotes or escaped quotes
        pathStr = pathStr.replace(/^['"]|['"]$/g, "").replace(/\\"/g, '"');

        if (pathStr.startsWith("data:")) return pathStr;
        if (pathStr.startsWith("http")) return pathStr;

        // Final absolute URL construction for relative paths only
        let finalUrl = `${apiBase}/${pathStr.replace(/\\/g, "/").replace(/^\/+/, "")}`;
        return encodeURI(finalUrl);
      };
      imgSrc = getCleanPath(rawPath);
    }

    const card = document.createElement("div");
    card.classList.add("room-card");
    card.innerHTML = `
      <div class="image-box">
        <img src="${imgSrc}" alt="${room.title}" class="room-img" loading="lazy" onerror="console.error('Image Load Error for ${room.title}:', this.src); this.onerror=null; this.src='https://placehold.co/600x400?text=Image+Not+Found';">
      </div>
      <div class="room-info">
          <h3>${room.title}</h3>
          <p><i class="fas fa-home"></i> <strong>${room.room_type}</strong></p>
          <p><i class="fas fa-tag"></i> <strong>₹${room.rent}/mo</strong> &nbsp; <span style="color:#999; font-size:0.8rem;">Dep: ₹${room.deposit}</span></p>
          <p><i class="fas fa-map-marker-alt"></i> ${room.location}</p>
          <p><i class="fas fa-users"></i> ${room.max_persons > 1 ? "Sharing" : "Single"} (${room.max_persons} Max)</p>
          <p><i class="fas fa-venus-mars"></i> Preferred: ${room.gender || "Any"}</p>
      </div>

      <div class="card-actions">
          <button class="view-details-btn" data-id="${room.id}">View Details</button>
      </div>
      <p class="posted">Posted recently</p>
    `;
    roomContainer.appendChild(card);
  });

  document.querySelectorAll(".view-details-btn").forEach((btn) => {
    btn.addEventListener("click", function () {
      const roomId = this.getAttribute("data-id");
      const isLoggedIn = localStorage.getItem("isLoggedIn");

      if (!isLoggedIn) {
        alert("Please Login to view room details!");
        window.location.href = "login.html";
        return;
      }

      window.location.href = `room_details.html?id=${roomId}`;
    });
  });
}

function filterRooms() {
  const locationVal = document
    .querySelector(".search-location input")
    .value.toLowerCase();
  const typeVal = document.querySelector(".dropdown-room select").value;
  const budgetVal = parseInt(document.getElementById("budgetRange").value);

  const filtered = allRooms.filter((room) => {
    const matchesLocation =
      room.location.toLowerCase().includes(locationVal) ||
      room.title.toLowerCase().includes(locationVal);
    let matchesType = true;
    if (typeVal) {
      matchesType = room.room_type.toLowerCase() === typeVal.toLowerCase();
      if (
        !matchesType &&
        typeVal === "single" &&
        room.room_type.toLowerCase().includes("single")
      )
        matchesType = true;
      if (
        !matchesType &&
        typeVal === "double" &&
        room.room_type.toLowerCase().includes("double")
      )
        matchesType = true;
    }
    const matchesBudget = room.rent <= budgetVal;
    const wifiReq = document.getElementById("filter-wifi").checked;
    const acReq = document.getElementById("filter-ac").checked;
    const parkingReq = document.getElementById("filter-parking").checked;
    const gymReq = document.getElementById("filter-gym").checked;
    const kitchenReq = document.getElementById("filter-kitchen").checked;
    const securityReq = document.getElementById("filter-security").checked;

    const matchesAmenities =
      (!wifiReq || room.wifi) &&
      (!acReq || room.ac) &&
      (!parkingReq || room.parking) &&
      (!gymReq || room.gym) &&
      (!kitchenReq || room.kitchen_access) &&
      (!securityReq || room.security);

    return matchesLocation && matchesType && matchesBudget && matchesAmenities;
  });

  renderRooms(filtered);
}
