document.addEventListener("DOMContentLoaded", async () => {
  const isLoggedIn = localStorage.getItem("isLoggedIn");
  const userRole = localStorage.getItem("currentUserRole");
  const loginBtn = document.querySelector(".login-btn");
  const navLinks = document.querySelector(".nav-links");

  // 1. Auth Guard & Role Check
  if (!isLoggedIn || userRole !== "Owner") {
    alert("Access Denied! Only Owners can post rooms.");
    window.location.href = "login.html";
    return;
  }

  // Image Compression Utility (Speeds up upload & reduces Vercel payload)
  async function compressImage(file) {
    return new Promise((resolve) => {
      const reader = new FileReader();
      reader.readAsDataURL(file);
      reader.onload = (event) => {
        const img = new Image();
        img.src = event.target.result;
        img.onload = () => {
          const canvas = document.createElement("canvas");
          const MAX_WIDTH = 1024; // Standard HD width
          const MAX_HEIGHT = 1024;
          let width = img.width;
          let height = img.height;

          if (width > height) {
            if (width > MAX_WIDTH) {
              height *= MAX_WIDTH / width;
              width = MAX_WIDTH;
            }
          } else {
            if (height > MAX_HEIGHT) {
              width *= MAX_HEIGHT / height;
              height = MAX_HEIGHT;
            }
          }
          canvas.width = width;
          canvas.height = height;
          const ctx = canvas.getContext("2d");
          ctx.drawImage(img, 0, 0, width, height);
          canvas.toBlob(
            (blob) => {
              resolve(new File([blob], file.name, { type: "image/jpeg" }));
            },
            "image/jpeg",
            0.7, // 70% Quality (Significant size reduction)
          );
        };
      };
    });
  }

  // 2. Dynamic Navbar Logic
  if (loginBtn) {
    loginBtn.textContent = "Logout";
    loginBtn.href = "#";
    loginBtn.addEventListener("click", (e) => {
      e.preventDefault();
      localStorage.clear();
      alert("Logged out successfully");
      window.location.href = "login.html";
    });
  }

  if (navLinks && !navLinks.querySelector('a[href*="dashboard"]')) {
    const dashboardLink = document.createElement("a");
    dashboardLink.href =
      userRole === "Owner" ? "owner_dashboard.html" : "bachelor_dashboard.html";
    dashboardLink.textContent = "Dashboard";
    navLinks.appendChild(dashboardLink);
  }

  // Preview Logic
  const imageInput = document.getElementById("file-upload");
  const imagePreviewContainer = document.getElementById(
    "image-preview-container",
  );

  function displayImagePreviews(files) {
    imagePreviewContainer.innerHTML = "";
    Array.from(files).forEach((file) => {
      const reader = new FileReader();
      reader.onload = (e) => {
        const img = document.createElement("img");
        img.src = e.target.result;
        img.className = "preview-img";
        imagePreviewContainer.appendChild(img);
      };
      reader.readAsDataURL(file);
    });
  }

  if (imageInput) {
    imageInput.addEventListener("change", (e) =>
      displayImagePreviews(e.target.files),
    );
  }

  const videoInput = document.getElementById("video-upload");
  const videoPreviewContainer = document.getElementById(
    "video-preview-container",
  );

  if (videoInput) {
    videoInput.addEventListener("change", function (e) {
      videoPreviewContainer.innerHTML = "";
      const file = e.target.files[0];
      if (file) {
        const video = document.createElement("video");
        video.src = URL.createObjectURL(file);
        video.width = 200;
        video.controls = true;
        videoPreviewContainer.appendChild(video);
      }
    });
  }

  // Handle Room Type Change
  const roomTypeSelect = document.getElementById("room-type");
  if (roomTypeSelect) {
    roomTypeSelect.addEventListener("change", function () {
      const capacityInput = document.getElementById("sharing-capacity");
      const map = {
        shared: 2,
        single: 1,
        "1bhk": 2,
        studio: 4,
        "3bhk": 6,
        pg: 1,
      };
      if (map[this.value]) capacityInput.value = map[this.value];
    });
  }

  // 3. EDIT MODE CHECK
  const urlParams = new URLSearchParams(window.location.search);
  const editRoomId = urlParams.get("id");
  let isEditMode = false;

  if (editRoomId) {
    isEditMode = true;
    document.querySelector(".form-title").textContent = "Edit Room Details";
    document.querySelector(".btn-submit").textContent = "Save Changes";

    try {
      const apiBase = window.API_CONFIG
        ? window.API_CONFIG.BASE_URL
        : "http://127.0.0.1:8000";
      const res = await fetch(`${apiBase}/rooms/${editRoomId}`);
      if (!res.ok) throw new Error("Room not found");
      const room = await res.json();

      // Fill Form
      document.getElementById("room-title").value = room.title;
      document.getElementById("room-type").value = room.room_type;
      document.getElementById("monthly-rent").value = room.rent;
      document.getElementById("deposit").value = room.deposit;
      document.getElementById("location").value = room.location;
      document.getElementById("description").value = room.description;
      document.getElementById("sharing-capacity").value = room.max_persons;
      document.getElementById("gender-preference").value = room.gender || "Any";

      // Amenities
      const checkboxes = document.querySelectorAll(
        ".amenities-grid input[type='checkbox']",
      );
      const keys = [
        "wifi",
        "ac",
        "attached_bath",
        "kitchen_access",
        "parking",
        "laundry",
        "security",
        "gym",
        "cctv",
        "semi_furnished",
      ];
      keys.forEach((key, i) => (checkboxes[i].checked = !!room[key]));

      document.querySelector(".bachelor-friendly-check input").checked =
        !!room.bachelor_allowed;

      // Show existing images preview
      if (room.image_url) {
        let images = room.image_url;
        if (typeof images === "string") {
          try {
            images = JSON.parse(images);
          } catch (e) {
            images = [images];
          }
        }
        if (Array.isArray(images)) {
          images.forEach((path) => {
            if (!path) return;
            const img = document.createElement("img");
            const pathStr = path.toString().trim();
            if (pathStr.startsWith("data:")) {
              img.src = pathStr;
            } else {
              const cleanP = pathStr.replace(/\\/g, "/").replace(/^\/+/, "");
              img.src = cleanP.startsWith("http")
                ? cleanP
                : `${apiBase}/${cleanP}`;
            }
            img.className = "preview-img";
            imagePreviewContainer.appendChild(img);
          });
        }
      }
    } catch (err) {
      console.error(err);
      alert("Error loading room data");
    }
  }

  // FORM SUBMISSION
  const form = document.querySelector(".post-form");
  if (form) {
    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      const currentUserEmail = localStorage.getItem("userEmail");

      const formData = new FormData();
      formData.append("owner_email", currentUserEmail);
      formData.append("title", document.getElementById("room-title").value);
      formData.append("room_type", document.getElementById("room-type").value);
      formData.append("rent", document.getElementById("monthly-rent").value);
      formData.append("deposit", document.getElementById("deposit").value);
      formData.append("location", document.getElementById("location").value);
      formData.append(
        "description",
        document.getElementById("description").value,
      );
      formData.append(
        "sharing_capacity",
        document.getElementById("sharing-capacity").value,
      );
      formData.append(
        "gender",
        document.getElementById("gender-preference").value,
      );
      formData.append(
        "bachelor_allowed",
        document.querySelector(".bachelor-friendly-check input").checked,
      );

      const keys = [
        "wifi",
        "ac",
        "attached_bath",
        "kitchen_access",
        "parking",
        "laundry",
        "security",
        "gym",
        "cctv",
        "semi_furnished",
      ];
      const checkboxes = document.querySelectorAll(
        ".amenities-grid input[type='checkbox']",
      );
      keys.forEach((key, i) => formData.append(key, checkboxes[i].checked));

      // Files (Compressed for speed)
      const submitBtn = document.querySelector(".btn-submit");
      const originalBtnText = submitBtn.textContent;
      submitBtn.disabled = true;
      submitBtn.textContent = "Processing Images...";

      if (imageInput.files.length > 0) {
        for (const f of Array.from(imageInput.files)) {
          if (f.type.startsWith("image/")) {
            const compressed = await compressImage(f);
            formData.append("files", compressed);
          } else {
            formData.append("files", f);
          }
        }
      } else if (!isEditMode) {
        alert("Please upload at least one image");
        submitBtn.disabled = false;
        submitBtn.textContent = originalBtnText;
        return;
      }

      submitBtn.textContent = isEditMode
        ? "Saving Changes..."
        : "Listing Room...";
      if (videoInput.files[0]) {
        formData.append("video_file", videoInput.files[0]);
      }

      const apiBase = window.API_CONFIG
        ? window.API_CONFIG.BASE_URL
        : "http://127.0.0.1:8000";
      const url = isEditMode
        ? `${apiBase}/rooms/${editRoomId}`
        : `${apiBase}/rooms/`;
      const method = isEditMode ? "PUT" : "POST";

      try {
        const res = await fetch(url, { method, body: formData });
        if (res.ok) {
          alert(
            isEditMode
              ? "Room Updated Successfully!"
              : "Room Listed Successfully!",
          );
          window.location.href = "owner_dashboard.html";
        } else {
          // Try to parse error as JSON first
          let errorMsg = "Action failed";
          try {
            const err = await res.json();
            errorMsg = err.detail || JSON.stringify(err);
          } catch (jsonErr) {
            // If not JSON, get raw text (could be Vercel's 413 or 504 page)
            const textErr = await res.text();
            errorMsg = `Server Error (${res.status}): ${textErr.substring(0, 100)}...`;
          }
          alert("Error: " + errorMsg);
        }
      } catch (err) {
        console.error(err);
        alert(
          "Request failed. Please check your internet connection or try with smaller image files.",
        );
      } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = originalBtnText;
      }
    });
  }

  const cancelBtn = document.querySelector(".btn-cancel");
  if (cancelBtn) {
    cancelBtn.addEventListener("click", () => {
      window.location.href = "owner_dashboard.html";
    });
  }
});
