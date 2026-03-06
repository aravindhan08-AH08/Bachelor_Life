document.addEventListener("DOMContentLoaded", () => {
  const isLoggedIn = localStorage.getItem("isLoggedIn");
  const loginBtn = document.querySelector(".login-btn");

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
});
