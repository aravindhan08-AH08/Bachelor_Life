document.addEventListener("DOMContentLoaded", () => {
  const isLoggedIn = localStorage.getItem("isLoggedIn");
  const loginBtn = document.querySelector(".login-btn");

  // 1. Dynamic Navbar Toggle
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

  // 2. Feedback Submission Logic
  const contactForm = document.querySelector(".contact-form");
  if (contactForm) {
    contactForm.addEventListener("submit", async (e) => {
      e.preventDefault();

      const payload = {
        name: contactForm.querySelector('input[name="name"]').value,
        email: contactForm.querySelector('input[name="email"]').value,
        message: contactForm.querySelector('textarea[name="message"]').value,
      };

      try {
        const apiBase = window.API_CONFIG
          ? window.API_CONFIG.BASE_URL
          : "http://127.0.0.1:8000";
        const response = await fetch(`${apiBase}/contact/`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        });

        if (response.ok) {
          alert(
            "Your feedback has been sent successfully! Thank you for reaching out.",
          );
          contactForm.reset();
        } else {
          alert("Failed to send message. Please try again.");
        }
      } catch (err) {
        console.error(err);
        alert("Network error. Is the backend running?");
      }
    });
  }
});
