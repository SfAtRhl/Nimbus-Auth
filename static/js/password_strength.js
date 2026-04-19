document.addEventListener("DOMContentLoaded", () => {
  const fields = document.querySelectorAll("[data-strength='password']");
  fields.forEach((field) => {
    const meter = document.querySelector(field.dataset.meter);
    const label = document.querySelector(field.dataset.label);
    const rules = document.querySelectorAll("[data-rule]");

    const update = () => {
      const value = field.value || "";
      let score = 0;
      const checks = {
        length: value.length >= 8,
        upper: /[A-Z]/.test(value),
        lower: /[a-z]/.test(value),
        number: /[0-9]/.test(value),
        symbol: /[^A-Za-z0-9]/.test(value),
      };

      Object.entries(checks).forEach(([key, ok]) => {
        if (ok) score += 1;
        rules.forEach((rule) => {
          if (rule.dataset.rule === key) {
            rule.classList.toggle("text-emerald-600", ok);
            rule.classList.toggle("text-slate-400", !ok);
          }
        });
      });

      if (meter) {
        meter.value = score;
      }
      if (label) {
        let text = "Weak";
        if (score >= 5) text = "Strong";
        else if (score >= 3) text = "Medium";
        label.textContent = text;
      }
    };

    field.addEventListener("input", update);
    update();
  });
});
