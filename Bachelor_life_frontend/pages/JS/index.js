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

  // 3. Search Logic Redirect
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
