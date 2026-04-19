/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: "class",
  content: ["./templates/**/*.html", "./static/js/**/*.js"],
  theme: {
    extend: {
      colors: {
        ink: "#0f172a",
        mist: "#f1f5f9",
        electric: "#2563eb",
        coral: "#f97316",
      },
      boxShadow: {
        glow: "0 0 0 1px rgba(15, 23, 42, 0.08), 0 12px 50px rgba(15, 23, 42, 0.12)",
      },
    },
  },
  plugins: [],
};
