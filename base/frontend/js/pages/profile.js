const profileForm = document.getElementById("profile-form");
const passwordForm = document.getElementById("password-form");

async function loadProfile() {
  try {
    const me = await api.get("/profile");
    document.getElementById("profile-email").value = me.email;
    profileForm.full_name.value = me.full_name || "";
    profileForm.phone.value = me.phone || "";
  } catch (err) {
    showToast(err.message, "error");
  }
}

profileForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  try {
    await api.put("/profile", {
      full_name: profileForm.full_name.value.trim(),
      phone: profileForm.phone.value.trim() || null,
    });
    showToast("Đã cập nhật hồ sơ");
  } catch (err) {
    showToast(err.message, "error");
  }
});

passwordForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  try {
    await api.put("/profile/password", {
      current_password: passwordForm.current_password.value,
      new_password: passwordForm.new_password.value,
    });
    passwordForm.reset();
    showToast("Đã đổi mật khẩu");
  } catch (err) {
    showToast(err.message, "error");
  }
});

loadProfile();