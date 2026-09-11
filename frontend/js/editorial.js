/* Editorial interactions — lightbox, reveal, nav */

(function () {
  const header = document.getElementById("main-header");
  const loader = document.getElementById("page-loader");

  function onScrollNav() {
    if (!header) return;
    const y = window.scrollY || 0;
    if (y < 60) {
      header.classList.add("is-top");
      header.classList.remove("is-scrolled");
    } else {
      header.classList.remove("is-top");
      header.classList.add("is-scrolled");
    }
  }

  window.addEventListener("scroll", onScrollNav, { passive: true });
  onScrollNav();

  window.addEventListener("load", () => {
    if (loader) {
      setTimeout(() => loader.classList.add("is-done"), 400);
    }
  });

  // Scroll reveal (también para nodos inyectados por app.js)
  let revealIo = null;
  function observeReveals() {
    const nodes = document.querySelectorAll(".reveal:not(.is-visible)");
    if (!nodes.length) return;

    if (!("IntersectionObserver" in window)) {
      nodes.forEach((el) => el.classList.add("is-visible"));
      return;
    }

    if (!revealIo) {
      revealIo = new IntersectionObserver(
        (entries) => {
          entries.forEach((entry) => {
            if (entry.isIntersecting) {
              entry.target.classList.add("is-visible");
              revealIo.unobserve(entry.target);
            }
          });
        },
        { threshold: 0.12, rootMargin: "0px 0px -40px 0px" }
      );
    }
    nodes.forEach((el) => revealIo.observe(el));
  }

  observeReveals();
  document.addEventListener("content:ready", observeReveals);

  // Lightbox (delegación: funciona tras cargar fotos desde la API)
  const lightbox = document.getElementById("lightbox");
  if (!lightbox) return;

  const imgEl = document.getElementById("lightbox-img");
  const titleEl = document.getElementById("lightbox-title");
  const metaEl = document.getElementById("lightbox-meta");
  const btnClose = document.getElementById("lightbox-close");
  const btnPrev = document.getElementById("lightbox-prev");
  const btnNext = document.getElementById("lightbox-next");
  let index = 0;

  function items() {
    return Array.from(document.querySelectorAll("[data-lightbox]"));
  }

  function openAt(i) {
    const list = items();
    if (!list.length) return;
    index = (i + list.length) % list.length;
    const el = list[index];
    imgEl.src = el.dataset.full || el.querySelector("img")?.src || "";
    imgEl.alt = el.dataset.title || "";
    titleEl.textContent = el.dataset.title || "";
    metaEl.textContent = [el.dataset.category, el.dataset.location]
      .filter(Boolean)
      .join(" · ");
    lightbox.classList.add("is-open");
    document.body.style.overflow = "hidden";
  }

  function closeLb() {
    lightbox.classList.remove("is-open");
    document.body.style.overflow = "";
  }

  document.addEventListener("click", (e) => {
    const el = e.target.closest("[data-lightbox]");
    if (!el) return;
    openAt(items().indexOf(el));
  });

  document.addEventListener("keydown", (e) => {
    const el = e.target.closest?.("[data-lightbox]");
    if (el && (e.key === "Enter" || e.key === " ")) {
      e.preventDefault();
      openAt(items().indexOf(el));
    }
  });

  btnClose?.addEventListener("click", closeLb);
  btnPrev?.addEventListener("click", () => openAt(index - 1));
  btnNext?.addEventListener("click", () => openAt(index + 1));
  lightbox.addEventListener("click", (e) => {
    if (e.target === lightbox) closeLb();
  });

  document.addEventListener("keydown", (e) => {
    if (!lightbox.classList.contains("is-open")) return;
    if (e.key === "Escape") closeLb();
    if (e.key === "ArrowLeft") openAt(index - 1);
    if (e.key === "ArrowRight") openAt(index + 1);
  });
})();
