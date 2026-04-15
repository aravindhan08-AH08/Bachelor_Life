document.addEventListener("DOMContentLoaded", () => {
  const isLoggedIn = localStorage.getItem("isLoggedIn");
  const userRole = localStorage.getItem("currentUserRole");
  const loginBtn = document.querySelector(".login-btn");
  const navLinks = document.querySelector(".nav-links");

  // 1. Show Dashboard link for Owners/Bachelors
  if (isLoggedIn && navLinks) {
    const dashboardLink = document.createElement("a");
    if (userRole === "Owner") {
      dashboardLink.href = "./pages/HTML/owner_dashboard.html";
    } else if (userRole === "Bachelor") {
      dashboardLink.href = "./pages/HTML/bachelor_dashboard.html";
    }
    dashboardLink.textContent = "Dashboard";
    navLinks.appendChild(dashboardLink);
  }

  // 2. Handle Login/Logout Button Text
  if (isLoggedIn && loginBtn) {
    loginBtn.textContent = "Logout";
    loginBtn.href = "#";
    loginBtn.addEventListener("click", (e) => {
      e.preventDefault();
      localStorage.clear();
      alert("Logged out successfully");
      window.location.href = "./pages/HTML/login.html";
    });
  }

  // 3. Price Slider + / - Buttons
  const priceSlider = document.getElementById("price");
  const priceLabel = document.getElementById("price-label");
  const priceDecrease = document.getElementById("price-decrease");
  const priceIncrease = document.getElementById("price-increase");

  function formatPrice(value) {
    return `Max: ₹${parseInt(value).toLocaleString("en-IN")}`;
  }

  if (priceSlider && priceLabel) {
    priceSlider.addEventListener("input", () => {
      priceLabel.textContent = formatPrice(priceSlider.value);
    });
  }

  if (priceDecrease && priceSlider) {
    priceDecrease.addEventListener("click", () => {
      const step = parseInt(priceSlider.step) || 1000;
      const min = parseInt(priceSlider.min) || 1000;
      const newVal = Math.max(min, parseInt(priceSlider.value) - step);
      priceSlider.value = newVal;
      if (priceLabel) priceLabel.textContent = formatPrice(newVal);
    });
  }

  if (priceIncrease && priceSlider) {
    priceIncrease.addEventListener("click", () => {
      const step = parseInt(priceSlider.step) || 1000;
      const max = parseInt(priceSlider.max) || 50000;
      const newVal = Math.min(max, parseInt(priceSlider.value) + step);
      priceSlider.value = newVal;
      if (priceLabel) priceLabel.textContent = formatPrice(newVal);
    });
  }

  // 4. Search Logic Redirect
  const searchBtn = document.querySelector(".search-btn");
  if (searchBtn) {
    searchBtn.addEventListener("click", () => {
      const location = document.querySelector(
        ".search-input[placeholder='Enter location']",
      ).value;
      const type = document.querySelector("select.search-input").value;
      const budget = document.getElementById("price").value;

      let query = `location=${encodeURIComponent(location)}`;
      if (type !== "All Room Types") {
        const typeVal = type.toLowerCase().includes("single")
          ? "single"
          : type.toLowerCase().includes("shared")
            ? "shared"
            : type.toLowerCase().includes("bachelor")
              ? "1bhk"
              : "";
        query += `&type=${typeVal}`;
      }
      query += `&budget=${budget}`;

      window.location.href = `./pages/HTML/find_room.html?${query}`;
    });
  }

  const protectedLinks = document.querySelectorAll(
    'a[href*="find_room.html"], a[href*="post_room.html"], .search-btn',
  );

  protectedLinks.forEach((element) => {
    if (element.classList.contains("search-btn")) return; // handled above
    element.addEventListener("click", (e) => {
      if (!isLoggedIn) {
        e.preventDefault();
        alert("Please login to access this feature!");
        window.location.href = "./pages/HTML/login.html";
      }
    });
  });
});
