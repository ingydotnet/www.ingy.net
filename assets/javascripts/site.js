(() => {
  const projectMenus = document.querySelectorAll("[data-project-menu]");

  for (const menu of projectMenus) {
    const summary = menu.querySelector("summary");

    document.addEventListener("click", (event) => {
      if (!menu.contains(event.target)) {
        menu.removeAttribute("open");
      }
    });

    menu.addEventListener("keydown", (event) => {
      if (event.key === "Escape" && menu.open) {
        menu.removeAttribute("open");
        summary.focus();
      }
    });
  }

  const heroIntro = document.querySelector("[data-hero-intro]");
  const heroDismiss = document.querySelector("[data-hero-dismiss]");

  if (heroIntro && heroDismiss) {
    heroDismiss.addEventListener("click", () => {
      heroIntro.classList.add("is-dismissed");
      heroIntro.setAttribute("aria-hidden", "true");
      window.setTimeout(() => {
        heroIntro.hidden = true;
      }, 180);
    });
  }

  const slideshow = document.querySelector("[data-slideshow]");
  if (!slideshow) return;

  const slides = [...slideshow.querySelectorAll("[data-slide]")];
  const previous = slideshow.querySelector("[data-slide-previous]");
  const next = slideshow.querySelector("[data-slide-next]");
  const toggle = slideshow.querySelector("[data-slide-toggle]");
  const status = slideshow.querySelector("[data-slide-status]");
  const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
  const interval = 7000;
  let current = 0;
  let timer = null;
  let manuallyPaused = false;
  let interactionPaused = false;

  const show = (index) => {
    current = (index + slides.length) % slides.length;
    slides.forEach((slide, slideIndex) => {
      const active = slideIndex === current;
      slide.classList.toggle("is-active", active);
      slide.setAttribute("aria-hidden", String(!active));
    });
    status.textContent = `${current + 1} / ${slides.length}`;
  };

  const stop = () => {
    if (timer !== null) {
      window.clearInterval(timer);
      timer = null;
    }
  };

  const start = () => {
    stop();
    if (
      slides.length > 1 &&
      !manuallyPaused &&
      !interactionPaused &&
      !reducedMotion.matches &&
      !document.hidden
    ) {
      timer = window.setInterval(() => show(current + 1), interval);
    }
  };

  const updateToggle = () => {
    if (reducedMotion.matches) {
      toggle.textContent = "Autoplay off";
      toggle.setAttribute(
        "aria-label",
        "Automatic slideshow disabled by reduced motion preference",
      );
      toggle.disabled = true;
      return;
    }

    toggle.disabled = false;
    toggle.textContent = manuallyPaused ? "Play" : "Pause";
    toggle.setAttribute(
      "aria-label",
      manuallyPaused ? "Play slideshow" : "Pause slideshow",
    );
  };

  previous.addEventListener("click", () => {
    show(current - 1);
    start();
  });

  next.addEventListener("click", () => {
    show(current + 1);
    start();
  });

  toggle.addEventListener("click", () => {
    manuallyPaused = !manuallyPaused;
    updateToggle();
    start();
  });

  slideshow.addEventListener("pointerenter", () => {
    interactionPaused = true;
    stop();
  });

  slideshow.addEventListener("pointerleave", () => {
    interactionPaused = false;
    start();
  });

  slideshow.addEventListener("focusin", () => {
    interactionPaused = true;
    stop();
  });

  slideshow.addEventListener("focusout", (event) => {
    if (!slideshow.contains(event.relatedTarget)) {
      interactionPaused = false;
      start();
    }
  });

  document.addEventListener("visibilitychange", start);
  reducedMotion.addEventListener("change", () => {
    updateToggle();
    start();
  });

  if (slides.length < 2) {
    slideshow.querySelector(".slideshow-controls").hidden = true;
  }

  show(0);
  updateToggle();
  start();
})();
