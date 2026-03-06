const bachelorTab = document.getElementById("bachelorTab");
const ownerTab = document.getElementById("ownerTab");
const userRoleInput = document.getElementById("userRole");

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

const signupForm = document.getElementById("signupForm");
if (signupForm) {
  signupForm.addEventListener("submit", async (e) => {
    e.preventDefault();

    const selectedRole = document.getElementById("userRole").value;

    const phone = document.getElementById("phone").value;
    if (!/^\d{10}$/.test(phone)) {
      alert("Phone number must be exactly 10 digits (0-9)!");
      return;
    }

    const userData = {
      fullName: document.getElementById("fullName").value,
      phone: phone,
      email: document.getElementById("email").value,
      gender: document.getElementById("gender").value,
      password: document.getElementById("password").value,
      role: selectedRole,
    };

    try {
      // Using window.API_CONFIG from api-config.js
      let url = window.API_CONFIG
        ? window.API_CONFIG.SIGNUP.USER
        : "http://127.0.0.1:8000/user/";
      if (selectedRole === "Owner") {
        url = window.API_CONFIG
          ? window.API_CONFIG.SIGNUP.OWNER
          : "http://127.0.0.1:8000/owner/";
      }

      // Adjust payload keys to match Backend Expectation
      let payload = {};
      if (selectedRole === "Owner") {
        payload = {
          owner_name: userData.fullName, // Backend expects owner_name
          phone: userData.phone,
          email: userData.email,
          gender: userData.gender,
          password: userData.password,
        };
      } else {
        payload = {
          name: userData.fullName, // Backend expects name
          phone: userData.phone,
          email: userData.email,
          gender: userData.gender,
          password: userData.password,
        };
      }

      const response = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (response.ok) {
        alert("Account Created! Now login.");
        window.location.href = "login.html";
      } else {
        const errorData = await response.json();
        let errorMsg = "Registration failed";

        if (errorData.detail) {
          if (Array.isArray(errorData.detail)) {
            // FastAPI validation error detail is an array
            errorMsg = errorData.detail.map(err => `${err.loc.join('.')}: ${err.msg}`).join("\n");
          } else {
            errorMsg = errorData.detail;
          }
        }
        alert("Error:\n" + errorMsg);
      }
    } catch (error) {
      console.error(error);
      alert("Connection Error. Is the backend running?");
    }
  });
}
