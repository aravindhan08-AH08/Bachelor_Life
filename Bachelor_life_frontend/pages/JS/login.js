const bachelorTab = document.getElementById("bachelorTab");
const ownerTab = document.getElementById("ownerTab");
const userRoleInput = document.getElementById("userRole");

// Tab Logic
if (bachelorTab && ownerTab && userRoleInput) {
  bachelorTab.onclick = () => {
    bachelorTab.classList.add("active");
    ownerTab.classList.remove("active");
    userRoleInput.value = "Bachelor";
  };

  ownerTab.onclick = () => {
    ownerTab.classList.add("active");
    bachelorTab.classList.remove("active");
    userRoleInput.value = "Owner";
  };
}

const loginForm = document.getElementById("loginForm");
if (loginForm) {
  loginForm.addEventListener("submit", async function (e) {
    e.preventDefault();
    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;
    const role = userRoleInput.value;

    try {
      // Using window.API_CONFIG from api-config.js
      let url = window.API_CONFIG
        ? window.API_CONFIG.LOGIN.USER
        : "http://127.0.0.1:8000/user/login";
      if (role === "Owner") {
        url = window.API_CONFIG
          ? window.API_CONFIG.LOGIN.OWNER
          : "http://127.0.0.1:8000/owner/login";
      }

      const response = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email: email, password: password }),
      });

      if (response.ok) {
        const data = await response.json();

        localStorage.setItem("isLoggedIn", "true");
        localStorage.setItem("userEmail", email);
        localStorage.setItem("currentUserRole", role);
        if (data.user) {
          localStorage.setItem("userData", JSON.stringify(data.user));
        }

        alert("Login Successful as " + role);

        if (role === "Owner") {
          window.location.href = "owner_dashboard.html";
        } else {
          window.location.href = "find_room.html";
        }
      } else {
        const contentType = response.headers.get("content-type");
        let errorMsg = "Invalid credentials";
        if (contentType && contentType.includes("application/json")) {
          const error = await response.json();
          errorMsg = error.detail || errorMsg;
        } else {
          errorMsg = `Server error (${response.status})`;
        }
        alert("Login Failed: " + errorMsg);
      }
    } catch (err) {
      console.error(err);
      alert("Login Failed: Server connection error");
    }
  });
}
