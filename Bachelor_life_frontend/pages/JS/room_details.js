document.addEventListener("DOMContentLoaded", async () => {
  // 1. Auth & Navbar Logic
  const isLoggedIn = localStorage.getItem("isLoggedIn");
  const userRole = localStorage.getItem("currentUserRole");
  const loginBtn = document.querySelector(".login-btn");
  const navLinks = document.querySelector(".nav-links");

  // Strict Login Check
  if (!isLoggedIn) {
    alert("You must be logged in to view room details.");
    window.location.href = "login.html";
    return;
  }

  if (loginBtn) {
    loginBtn.textContent = "Logout";
    loginBtn.href = "#";
    loginBtn.addEventListener("click", (e) => {
      e.preventDefault();
      localStorage.clear();
      window.location.href = "login.html";
    });
  }

  if (navLinks) {
    const dashboardLink = document.createElement("a");
    if (userRole === "Owner") {
      dashboardLink.href = "owner_dashboard.html";
    } else if (userRole === "Bachelor") {
      dashboardLink.href = "bachelor_dashboard.html";
    }
    dashboardLink.textContent = "Dashboard";
    navLinks.appendChild(dashboardLink);
  }

  // 2. Fetch Room Details
  const urlParams = new URLSearchParams(window.location.search);
  const roomId = urlParams.get("id");

  if (!roomId) {
    alert("No room specified!");
    window.location.href = "find_room.html";
    return;
  }

  try {
    const apiBase = window.API_CONFIG
      ? window.API_CONFIG.BASE_URL
      : "http://127.0.0.1:8000";
    const response = await fetch(`${apiBase}/rooms/${roomId}`);

    if (!response.ok) {
      throw new Error("Room not found");
    }

    const room = await response.json();
    renderRoomDetails(room);

    // 3. Persistent Booking Status Check
    if (userRole === "Bachelor") {
      const userData = JSON.parse(localStorage.getItem("userData"));
      if (userData && userData.id) {
        try {
          const statusRes = await fetch(`${apiBase}/booking/check-status/${roomId}?user_id=${userData.id}`);
          if (statusRes.ok) {
            const statusData = await statusRes.json();
            if (statusData.status === "Pending" || statusData.status === "Confirmed") {
              const btn = document.getElementById("book-now-btn");
              if (btn) {
                btn.textContent = statusData.status === "Confirmed" ? "Booked" : "Request Sent";
                btn.disabled = true;
                btn.style.backgroundColor = "#ccc";
                btn.style.cursor = "not-allowed";
              }
            }
          }
        } catch (err) {
          console.error("Error checking booking status:", err);
        }
      }
    }
  } catch (error) {
    const loadingEl = document.getElementById("loading");
    if (loadingEl) loadingEl.textContent = "Error loading details.";
  }
});

function renderRoomDetails(room) {
  const loadingEl = document.getElementById("loading");
  const contentEl = document.getElementById("room-content");

  // Show content immediately once we have the data
  if (loadingEl) loadingEl.style.display = "none";
  if (contentEl) contentEl.style.display = "block";

  const setSafeText = (id, text, fallback = "N/A") => {
    const el = document.getElementById(id);
    if (el) el.textContent = text || fallback;
  };

  const setSafeHTML = (id, html) => {
    const el = document.getElementById(id);
    if (el) el.innerHTML = html;
  };

  // 1. Basic Room Info
  try {
    setSafeText("room-title", room.title, "Untitled Room");
    setSafeHTML(
      "room-location",
      `<i class="fas fa-map-marker-alt"></i> ${room.location || "Location not specified"}`,
    );
    setSafeText("room-rent", `₹${room.rent || 0} / month`);
    setSafeText("room-deposit", `Deposit: ₹${room.deposit || 0}`);
    setSafeText(
      "room-description",
      room.description,
      "No description available.",
    );

    let displayType = room.room_type || "Room";
    const typeMap = {
      "1bhk": "1 BHK",
      "studio": "2 BHK",
      "single": "Single Room",
      "shared": "Shared Room",
      "3bhk": "3 BHK",
      "pg": "PG / Hostel"
    };
    setSafeText("room-type", typeMap[displayType.toLowerCase()] || displayType);
    setSafeText("room-capacity", `${room.max_persons || 1} Person(s)`);
    setSafeText("room-bachelor", room.bachelor_allowed ? "Yes" : "No");
    setSafeText("room-gender", room.gender || "Any");
  } catch (e) { console.error("Error rendering basic info:", e); }

  // 2. Owner Information
  try {
    const ownerContainer = document.querySelector(".owner-info");
    if (ownerContainer) {
      const ownerName = room.owner_name || "Owner";
      const ownerPhone = room.owner_phone
        ? `<a href="tel:${room.owner_phone}">${room.owner_phone}</a>`
        : "Not Available";
      const ownerEmail = room.owner_email
        ? `<a href="mailto:${room.owner_email}">${room.owner_email}</a>`
        : "Not Available";

      ownerContainer.innerHTML = `
              <h4>Posted by: ${ownerName}</h4>
              <p class="owner-contact-item"><i class="fas fa-phone"></i> ${ownerPhone}</p>
              <p class="owner-contact-item"><i class="fas fa-envelope"></i> ${ownerEmail}</p>
          `;
    }
  } catch (e) { console.error("Error rendering owner info:", e); }

  // 3. Robust Image Gallery
  const gallery = document.getElementById("image-gallery");
  if (gallery) {
    gallery.innerHTML = "";

    const rawImages = room.image_url;
    console.log("DEBUG: rawImages from API:", rawImages);

    let images = [];
    try {
      if (Array.isArray(rawImages)) {
        images = rawImages;
      } else if (typeof rawImages === 'string' && rawImages.trim() !== '') {
        let str = rawImages.trim();
        if (str.startsWith('[') && str.endsWith(']')) {
          try {
            // Attempt JSON parse
            images = JSON.parse(str);
          } catch (e) {
            try {
              // Try fixing single quotes (Python style) but be careful with Base64
              // We only replace ' if it's followed by , or ] or preceded by [ or ,
              let fixedStr = str.replace(/'/g, '"');
              images = JSON.parse(fixedStr);
            } catch (e2) {
              console.warn("Manual parsing fallback for images string");
              const content = str.substring(1, str.length - 1);
              // Simple split by comma, then trim quotes. 
              // NOTE: If Base64 has commas in data (rare but possible in some formats), 
              // this might fail, but for standard data: URLs it works.
              images = content.split(',').map(s => s.trim().replace(/^['"]|['"]$/g, ''));
            }
          }
        } else {
          images = [str];
        }
      }
    } catch (err) {
      console.error("Error parsing images:", err);
      images = [];
    }

    const apiBase = window.API_CONFIG ? window.API_CONFIG.BASE_URL : "http://127.0.0.1:8000";

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
      const finalUrl = `${apiBase}/${cleanP}`;
      console.log("DEBUG: Final Image URL (Room Details):", finalUrl);
      return finalUrl;
    };

    // Main Image
    const mainImgContainer = document.createElement("div");
    mainImgContainer.className = "main-image-container";
    const mainImg = document.createElement("img");

    const fallbackImage = "https://placehold.co/600x400?text=No+Image";
    mainImg.src = images.length > 0 ? getCleanPath(images[0]) : fallbackImage;
    mainImg.className = "main-image";
    mainImg.id = "main-display-image";
    mainImg.onerror = () => {
      if (mainImg.src !== fallbackImage) {
        mainImg.src = "https://placehold.co/600x400?text=Image+Not+Found";
      }
    };
    mainImgContainer.appendChild(mainImg);
    gallery.appendChild(mainImgContainer);

    // Thumbnails
    if (images.length > 1) {
      const thumbContainer = document.createElement("div");
      thumbContainer.className = "thumbnails-container";
      images.forEach((path, index) => {
        if (!path) return;
        const thumb = document.createElement("img");
        thumb.src = getCleanPath(path);
        thumb.className = `thumb-image ${index === 0 ? "active-thumb" : ""}`;
        thumb.onclick = () => {
          document.getElementById("main-display-image").src = getCleanPath(path);
          document.querySelectorAll(".thumb-image").forEach(t => t.classList.remove("active-thumb"));
          thumb.classList.add("active-thumb");
        };
        thumb.onerror = () => (thumb.src = "https://placehold.co/100x100?text=Error");
        thumbContainer.appendChild(thumb);
      });
      gallery.appendChild(thumbContainer);
    }
  }

  // 4. Amenities List
  try {
    const amenityList = document.getElementById("amenities-list");
    if (amenityList) {
      amenityList.innerHTML = "";
      const amenities = [
        { key: "wifi", label: "Wifi", icon: "fa-wifi" },
        { key: "ac", label: "AC", icon: "fa-snowflake" },
        { key: "attached_bath", label: "Attached Bath", icon: "fa-bath" },
        { key: "kitchen_access", label: "Kitchen", icon: "fa-utensils" },
        { key: "parking", label: "Parking", icon: "fa-parking" },
        { key: "laundry", label: "Laundry", icon: "fa-tshirt" },
        { key: "security", label: "Security", icon: "fa-shield-alt" },
        { key: "gym", label: "Gym", icon: "fa-dumbbell" },
        { key: "cctv", label: "CCTV", icon: "fa-video" },
        { key: "semi_furnished", label: "Semi Furnished", icon: "fa-couch" },
      ];

      amenities.forEach((am) => {
        if (room[am.key]) {
          const div = document.createElement("div");
          div.className = "amenity-item";
          div.innerHTML = `<i class="fas ${am.icon}"></i> ${am.label}`;
          amenityList.appendChild(div);
        }
      });
    }
  } catch (e) { console.error("Error rendering amenities:", e); }

  // 5. Virtual Tour
  try {
    if (room.video_url) {
      const tourSection = document.getElementById("virtual-tour-section");
      const videoContainer = document.getElementById("video-container");
      if (tourSection && videoContainer) {
        tourSection.style.display = "block";
        const url = room.video_url;
        let videoHtml = "";

        if (url.includes("youtube.com") || url.includes("youtu.be")) {
          let videoId = "";
          if (url.includes("v=")) videoId = url.split("v=")[1].split("&")[0];
          else if (url.includes("youtu.be/")) videoId = url.split("youtu.be/")[1].split("?")[0];
          videoHtml = `<iframe width="100%" height="400" src="https://www.youtube.com/embed/${videoId}" frameborder="0" allowfullscreen class="video-frame"></iframe>`;
        } else if (url.startsWith("static/room_videos/")) {
          const apiBase = window.API_CONFIG ? window.API_CONFIG.BASE_URL : "http://127.0.0.1:8000";
          const videoPath = `${apiBase}/${url.replace(/\\/g, "/")}`;
          videoHtml = `<video class="video-player" controls><source src="${videoPath}" type="video/mp4">Your browser does not support the video tag.</video>`;
        } else if (url.trim() !== "") {
          videoHtml = `<p>Watch tour here: <a href="${url}" target="_blank" class="tour-link">${url}</a></p>`;
        }
        if (videoHtml) videoContainer.innerHTML = videoHtml;
      }
    }
  } catch (e) { console.error("Error rendering virtual tour:", e); }

  // 6. Booking Button
  const bookBtn = document.getElementById("book-now-btn");
  if (bookBtn) {
    const newBtn = bookBtn.cloneNode(true);
    bookBtn.parentNode.replaceChild(newBtn, bookBtn);
    newBtn.addEventListener("click", () => handleBooking(room.id));
  }
}

async function handleBooking(roomId) {
  const isLoggedIn = localStorage.getItem("isLoggedIn");
  const userDataStr = localStorage.getItem("userData");

  if (!isLoggedIn || !userDataStr) {
    alert("Please login to book a room!");
    window.location.href = "login.html";
    return;
  }

  const userRole = localStorage.getItem("currentUserRole");
  if (userRole === "Owner") {
    alert("Owners cannot book rooms! Login as Bachelor.");
    return;
  }

  const userData = JSON.parse(userDataStr);

  if (confirm("Do you want to send a booking request to the owner?")) {
    try {
      const apiBase = window.API_CONFIG
        ? window.API_CONFIG.BASE_URL
        : "http://127.0.0.1:8000";
      const payload = {
        room_id: parseInt(roomId),
        user_id: userData.id,
      };

      const res = await fetch(`${apiBase}/booking/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      const data = await res.json();

      if (res.ok) {
        alert("book success");
        const btn = document.getElementById("book-now-btn");
        if (btn) {
          btn.textContent = "Request Sent";
          btn.disabled = true;
        }
      } else {
        alert("Error: " + (data.detail || "Failed to book room"));
      }
    } catch (err) {
      console.error(err);
      alert("Network error while booking room.");
    }
  }
}
