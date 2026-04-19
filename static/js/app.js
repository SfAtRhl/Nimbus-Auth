document.addEventListener("DOMContentLoaded", () => {
  const root = document.documentElement;
  const storedTheme = localStorage.getItem("theme");
  if (storedTheme === "dark") {
    root.classList.add("dark");
  }

  const themeToggle = document.querySelector("[data-theme-toggle]");
  const toggleThemeIcons = () => {
    if (!themeToggle) return;
    const showSun = root.classList.contains("dark");
    const moonIcon = themeToggle.querySelector(".theme-icon-moon");
    const sunIcon = themeToggle.querySelector(".theme-icon-sun");
    if (moonIcon) {
      moonIcon.classList.toggle("hidden", showSun);
    }
    if (sunIcon) {
      sunIcon.classList.toggle("hidden", !showSun);
    }
  };
  const updateThemeLabel = () => {
    if (!themeToggle) return;
    const darkLabel = themeToggle.getAttribute("data-dark-label") || "Dark";
    const lightLabel = themeToggle.getAttribute("data-light-label") || "Light";
    const label = root.classList.contains("dark") ? lightLabel : darkLabel;
    themeToggle.setAttribute("aria-label", label);
  };

  if (themeToggle) {
    updateThemeLabel();
    toggleThemeIcons();
    themeToggle.addEventListener("click", () => {
      root.classList.toggle("dark");
      const nextTheme = root.classList.contains("dark") ? "dark" : "light";
      localStorage.setItem("theme", nextTheme);
      updateThemeLabel();
      toggleThemeIcons();
    });
  }

  const toggles = document.querySelectorAll("[data-toggle='password']");
  toggles.forEach((toggle) => {
    toggle.addEventListener("click", () => {
      const targetId = toggle.getAttribute("data-target");
      const input = document.getElementById(targetId);
      if (!input) return;
      const showLabel = toggle.getAttribute("data-show-label") || "Show";
      const hideLabel = toggle.getAttribute("data-hide-label") || "Hide";
      const isPassword = input.getAttribute("type") === "password";
      input.setAttribute("type", isPassword ? "text" : "password");
      toggle.textContent = isPassword ? hideLabel : showLabel;
    });
  });
});
