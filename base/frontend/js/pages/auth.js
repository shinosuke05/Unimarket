const loginForm = document.getElementById("login-form");
const registerForm = document.getElementById("register-form");
const loginError = document.getElementById("login-error");
const registerError = document.getElementById("register-error");

loginForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  loginError.textContent = "";
  try {
    const res = await api.post("/auth/login", {
      email: loginForm.email.value.trim(),
      password: loginForm.password.value,
    });
    localStorage.setItem("token", res.access_token);
    showToast("Đăng nhập thành công");
    window.location.href = res.user.role === "ADMIN"
  ? "../admin/index.html"
  : "profile.html";
  } catch (err) {
    loginError.textContent = err.message;
  }
});

registerForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  registerError.textContent = "";
  try {
    await api.post("/auth/register", {
      full_name: registerForm.full_name.value.trim(),
      email: registerForm.email.value.trim(),
      phone: registerForm.phone.value.trim() || null,
      password: registerForm.password.value,
    });
    registerForm.reset();
    showToast("Đăng ký thành công, hãy đăng nhập");
  } catch (err) {
    registerError.textContent = err.message;
  }
});
