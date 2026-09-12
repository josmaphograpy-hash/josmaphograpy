(() => {
  const API = (window.API_BASE || "/api").replace(/\/$/, "");

  const money = (n, currency = "COP") => {
    try {
      return new Intl.NumberFormat("es-CO", {
        style: "currency",
        currency,
        maximumFractionDigits: 0,
      }).format(Number(n) || 0);
    } catch {
      return `$ ${Math.round(Number(n) || 0).toLocaleString("es-CO")} ${currency}`;
    }
  };

  const stars = (n) =>
    Array.from({ length: 5 }, (_, i) =>
      i < n ? '<i class="fa-solid fa-star"></i>' : '<i class="fa-regular fa-star"></i>'
    ).join("");

  async function load() {
    const res = await fetch(`${API}/public`);
    if (!res.ok) throw new Error("No se pudo cargar el contenido");
    return res.json();
  }

  const SESSION_COPY = {
    all: {
      eyebrow: "Colección completa",
      title: "Historia visual en todas las facetas",
      text: "Un recorrido por el trabajo editorial: retratos, celebraciones y proyectos de marca con la misma sensibilidad fine art.",
    },
    personas: {
      eyebrow: "Sesión Personas",
      title: "Retratos con carácter y naturalidad",
      text: "Individuales, parejas y familia: presencia auténtica, luz cuidada y una dirección suave que transmite confianza.",
    },
    quince: {
      eyebrow: "Sesión Quinceañeros",
      title: "La celebración de una etapa",
      text: "Elegancia juvenil y emoción real: una narrativa visual que honra el momento sin excesos, con estilo editorial.",
    },
    empresas: {
      eyebrow: "Sesión Empresas",
      title: "Imagen corporativa con sensibilidad",
      text: "Marca, equipo y eventos: fotografía profesional que proyecta seriedad, calidez y versatilidad ante tus clientes.",
    },
    bodas: {
      eyebrow: "Sesión Bodas",
      title: "La poesía del día más importante",
      text: "Documental fine art: gestos íntimos, luz natural y una mirada que preserva la verdad emocional de la celebración.",
    },
  };

  function normalizeSession(category) {
    const c = (category || "").toLowerCase().normalize("NFD").replace(/\p{M}/gu, "");
    if (/quince|xv\b|15\s*anos|sweet\s*sixteen/.test(c)) return "quince";
    if (/empresa|corporativ|comercial|branding|negocios|headshot|equipo/.test(c)) return "empresas";
    if (/persona|retrato|portrait|familia|individual|lifestyle|personal/.test(c)) return "personas";
    if (/boda|wedding|matrimonio|pre.?boda|save.?the.?date|ceremonia|recepcion|novia/.test(c)) return "bodas";
    return "other";
  }

  function escapeAttr(str) {
    return String(str || "")
      .replace(/&/g, "&amp;")
      .replace(/"/g, "&quot;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;");
  }

  function setupSessionsGallery(photos) {
    const gallery = document.querySelector("[data-gallery]");
    const empty = document.querySelector("[data-gallery-empty]");
    const tabs = document.querySelectorAll("[data-session-tabs] [data-session]");
    const panel = document.querySelector("[data-session-panel]");
    const moreWrap = document.querySelector("[data-gallery-more-wrap]");
    const moreBtn = document.querySelector("[data-gallery-more]");
    const moreLabel = document.querySelector("[data-gallery-more-label]");
    if (!gallery) return;

    const PAGE_SIZE = 6;
    let currentSession = "all";
    let visibleCount = PAGE_SIZE;

    const items = (photos || []).map((p) => ({
      ...p,
      session: normalizeSession(p.category),
    }));

    const filteredItems = () =>
      currentSession === "all"
        ? items
        : items.filter((p) => p.session === currentSession);

    const cardHtml = (p) => `
      <figure class="gallery-item reveal" tabindex="0" role="button"
        data-lightbox data-full="${escapeAttr(p.image_url)}" data-title="${escapeAttr(p.title)}"
        data-category="${escapeAttr(p.category || "")}" data-location="${escapeAttr(p.location || "")}">
        <img src="${escapeAttr(p.image_url)}" alt="${escapeAttr(p.title)}" loading="lazy">
        <figcaption class="gallery-item__meta">
          ${p.category ? `<span class="text-[10px] uppercase tracking-widest text-brand-goldlight">${escapeAttr(p.category)}</span>` : ""}
          <h3 class="font-serif text-xl mt-1">${escapeAttr(p.title)}</h3>
          ${p.location ? `<p class="text-xs text-stone-300 mt-1">${escapeAttr(p.location)}</p>` : ""}
        </figcaption>
      </figure>`;

    const paint = ({ resetVisible = false } = {}) => {
      const copy = SESSION_COPY[currentSession] || SESSION_COPY.all;
      const eyebrow = document.querySelector("[data-session-eyebrow]");
      const title = document.querySelector("[data-session-title]");
      const text = document.querySelector("[data-session-text]");
      if (eyebrow) eyebrow.textContent = copy.eyebrow;
      if (title) title.textContent = copy.title;
      if (text) text.textContent = copy.text;

      if (resetVisible) visibleCount = PAGE_SIZE;

      const filtered = filteredItems();
      const shown = filtered.slice(0, visibleCount);
      const remaining = Math.max(0, filtered.length - shown.length);

      gallery.classList.add("is-switching");
      panel?.classList.add("is-switching");

      window.setTimeout(() => {
        gallery.innerHTML = shown.map(cardHtml).join("");

        if (empty) empty.classList.toggle("hidden", filtered.length > 0);
        if (moreWrap) {
          if (remaining > 0) {
            moreWrap.hidden = false;
            if (moreLabel) moreLabel.textContent = `Ver ${Math.min(PAGE_SIZE, remaining)} más`;
          } else {
            moreWrap.hidden = true;
          }
        }

        gallery.classList.remove("is-switching");
        panel?.classList.remove("is-switching");
        document.dispatchEvent(new CustomEvent("content:ready"));
      }, 180);
    };

    tabs.forEach((tab) => {
      tab.addEventListener("click", () => {
        currentSession = tab.getAttribute("data-session") || "all";
        tabs.forEach((t) => {
          const on = t === tab;
          t.classList.toggle("is-active", on);
          t.setAttribute("aria-selected", on ? "true" : "false");
        });
        paint({ resetVisible: true });
      });
    });

    moreBtn?.addEventListener("click", () => {
      visibleCount += PAGE_SIZE;
      paint();
    });

    paint({ resetVisible: true });
  }

  function render(data) {
    const s = data.settings || {};
    const currency = s.currency || "COP";
    document.title = `${s.brand_name || "Josman"} | Fotografía Fine Art`;

    const brandEls = document.querySelectorAll("[data-brand]");
    brandEls.forEach((el) => {
      el.textContent = s.brand_name || "Josman Sanchez";
    });
    document.querySelectorAll("[data-tagline]").forEach((el) => {
      el.textContent = s.tagline || "";
    });
    document.querySelectorAll("[data-location]").forEach((el) => {
      el.textContent = s.location || "";
    });
    document.querySelectorAll("[data-hero-title]").forEach((el) => {
      el.textContent = s.hero_title || "";
    });
    document.querySelectorAll("[data-hero-subtitle]").forEach((el) => {
      el.textContent = s.hero_subtitle || "";
    });
    document.querySelectorAll("[data-about-title]").forEach((el) => {
      el.textContent = s.about_title || "";
    });
    document.querySelectorAll("[data-about-text]").forEach((el) => {
      el.textContent = s.about_text || "";
    });

    const heroImg = document.querySelector("[data-hero-image]");
    if (heroImg && s.hero_image) heroImg.src = s.hero_image;

    const wa = (s.whatsapp || "").replace(/\D/g, "");
    document.querySelectorAll("[data-whatsapp-link]").forEach((a) => {
      a.href = wa ? `https://wa.me/${wa}` : "#";
    });

    // Social
    const socialWrap = document.querySelector("[data-socials]");
    if (socialWrap) {
      socialWrap.innerHTML = (data.socials || [])
        .map(
          (x) =>
            `<a href="${x.url}" target="_blank" rel="noopener" aria-label="${x.platform}" class="hover:text-white transition-colors"><i class="${x.icon}"></i></a>`
        )
        .join("");
    }

    // Gallery — sesiones filtrables
    setupSessionsGallery(data.photos || []);

    // Packages
    const pkgs = document.querySelector("[data-packages]");
    if (pkgs) {
      pkgs.innerHTML = (data.packages || [])
        .map((p) => {
          const featured = p.is_featured
            ? "bg-brand-dark text-white border-2 border-brand-gold lg:-translate-y-3"
            : "bg-brand-cream border border-brand-border/80";
          const features = (p.features || [])
            .map((f) => `<li class="flex gap-2"><i class="fa-solid fa-check text-brand-gold text-xs mt-1"></i><span>${f}</span></li>`)
            .join("");
          return `
          <article class="reveal rounded-2xl p-8 flex flex-col justify-between shadow-editorial ${featured}">
            ${p.is_featured ? `<div class="text-[10px] uppercase tracking-widest text-brand-gold mb-3">La más elegida</div>` : ""}
            ${p.badge ? `<span class="text-[10px] uppercase tracking-widest mb-3 inline-block opacity-80">${p.badge}</span>` : ""}
            <h3 class="font-serif text-2xl mb-2">${p.name}</h3>
            <p class="text-xs opacity-70 mb-4">${p.description || p.short_desc || ""}</p>
            <p class="font-serif text-3xl mb-6">${money(p.price, currency)}</p>
            <ul class="space-y-2 text-xs mb-8">${features}</ul>
            <button type="button" data-select-package="${p.key}" class="w-full py-3 rounded-full border border-brand-gold text-xs font-bold uppercase tracking-widest hover:bg-brand-gold hover:text-white transition">Seleccionar</button>
          </article>`;
        })
        .join("");
    }

    // Addons
    const addons = document.querySelector("[data-addons]");
    if (addons) {
      addons.innerHTML = (data.addons || [])
        .map(
          (a) => `
        <article class="reveal p-6 rounded-2xl bg-brand-cream border border-brand-border/80">
          <div class="w-10 h-10 rounded-xl bg-brand-sand border border-brand-border flex items-center justify-center text-brand-gold mb-4"><i class="${a.icon}"></i></div>
          <h4 class="font-serif text-lg mb-1">${a.name}</h4>
          <p class="text-xs text-brand-muted mb-4">${a.description || ""}</p>
          <p class="text-xs font-semibold">${money(a.price, currency)}</p>
        </article>`
        )
        .join("");
    }

    // Quote radios/checkboxes
    const quotePkgs = document.querySelector("[data-quote-packages]");
    if (quotePkgs) {
      quotePkgs.innerHTML = (data.packages || [])
        .map(
          (p) => `
        <label class="flex items-center justify-between p-4 rounded-xl border ${p.key === data.featured_key ? "border-2 border-brand-gold" : "border-brand-border/80"} bg-brand-sand cursor-pointer">
          <div class="flex items-center gap-3">
            <input type="radio" name="collection" value="${p.key}" data-price="${p.price}" data-name="${p.name}" ${p.key === data.featured_key ? "checked" : ""}>
            <div>
              <p class="font-serif text-sm font-semibold">${p.name}</p>
              <p class="text-[11px] text-brand-muted">${p.short_desc || ""}</p>
            </div>
          </div>
          <span class="font-serif text-xs font-bold">${money(p.price, currency)}</span>
        </label>`
        )
        .join("");
    }
    const quoteAddons = document.querySelector("[data-quote-addons]");
    if (quoteAddons) {
      quoteAddons.innerHTML = (data.addons || [])
        .map(
          (a) => `
        <label class="flex items-center justify-between p-3.5 rounded-xl border border-brand-border/80 bg-brand-sand cursor-pointer">
          <div class="flex items-center gap-2.5">
            <input type="checkbox" class="addon-check" value="${a.key}" data-price="${a.price}" data-name="${a.name}">
            <span class="text-xs font-medium">${a.name}</span>
          </div>
          <span class="text-[11px] font-semibold text-brand-muted">${money(a.price, currency)}</span>
        </label>`
        )
        .join("");
    }

    // Reviews
    const reviews = document.querySelector("[data-reviews]");
    if (reviews) {
      reviews.innerHTML = (data.reviews || [])
        .map(
          (r) => `
        <article class="reveal bg-brand-cream rounded-2xl p-8 border border-brand-border/80">
          <div class="text-brand-gold text-xs mb-3">${stars(r.rating)}</div>
          <p class="font-serif italic text-lg mb-6">"${r.comment}"</p>
          <h4 class="text-xs font-semibold uppercase tracking-wider">${r.author_name}</h4>
          <p class="text-[11px] text-brand-muted">${r.event_info || ""}</p>
        </article>`
        )
        .join("") || `<p class="text-center text-brand-muted">Sé el primero en dejar tu opinión.</p>`;
    }
    const ratingMeta = document.querySelector("[data-rating-meta]");
    if (ratingMeta && data.review_count) {
      ratingMeta.innerHTML = `<span class="text-brand-gold">${stars(Math.round(data.avg_rating || 0))}</span> ${data.avg_rating} / 5 · ${data.review_count} opiniones`;
    }

    // Wire quote calculator
    const recalc = () => {
      const pkg = document.querySelector('input[name="collection"]:checked');
      let total = pkg ? Number(pkg.dataset.price || 0) : 0;
      const lines = [];
      if (pkg) lines.push(`<div class="flex justify-between"><span>${pkg.dataset.name}</span><span>${money(total, currency)}</span></div>`);
      document.querySelectorAll(".addon-check:checked").forEach((el) => {
        const price = Number(el.dataset.price || 0);
        total += price;
        lines.push(`<div class="flex justify-between text-stone-400"><span>+ ${el.dataset.name}</span><span>${money(price, currency)}</span></div>`);
      });
      const box = document.querySelector("[data-quote-breakdown]");
      if (box) box.innerHTML = lines.join("") || `<p class="italic text-stone-500">Selecciona una colección</p>`;
      const totalEl = document.querySelector("[data-quote-total]");
      if (totalEl) totalEl.textContent = money(total, currency);
    };
    document.querySelectorAll('input[name="collection"], .addon-check').forEach((el) => {
      el.addEventListener("change", recalc);
    });
    document.querySelectorAll("[data-select-package]").forEach((btn) => {
      btn.addEventListener("click", () => {
        const key = btn.getAttribute("data-select-package");
        const radio = document.querySelector(`input[name="collection"][value="${key}"]`);
        if (radio) radio.checked = true;
        recalc();
        document.getElementById("cotizador")?.scrollIntoView({ behavior: "smooth" });
      });
    });
    recalc();

    // WhatsApp quote
    const sendBtn = document.querySelector("[data-send-quote]");
    if (sendBtn) {
      sendBtn.onclick = () => {
        const names = document.getElementById("input-names")?.value.trim();
        const phone = document.getElementById("input-phone")?.value.trim();
        const date = document.getElementById("input-date")?.value;
        const place = document.getElementById("input-location")?.value.trim();
        if (!names || !phone || !date || !place) {
          alert("Completa nombres, teléfono, fecha y lugar.");
          return;
        }
        const pkg = document.querySelector('input[name="collection"]:checked');
        let total = pkg ? Number(pkg.dataset.price || 0) : 0;
        let extras = "";
        document.querySelectorAll(".addon-check:checked").forEach((el) => {
          total += Number(el.dataset.price || 0);
          extras += `• ${el.dataset.name}\n`;
        });
        const msg =
          `Hola, quiero cotizar una cobertura:\n\nPareja: ${names}\nTel: ${phone}\nFecha: ${date}\nLugar: ${place}\nColección: ${pkg?.dataset.name || "-"}\nAdicionales:\n${extras || "Ninguno"}\nTotal estimado: ${money(total, currency)}`;
        window.open(`https://wa.me/${wa}?text=${encodeURIComponent(msg)}`, "_blank");
      };
    }

    // Review form
    const form = document.getElementById("review-form");
    if (form) {
      form.onsubmit = async (e) => {
        e.preventDefault();
        const payload = Object.fromEntries(new FormData(form).entries());
        const res = await fetch(`${API}/reviews`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        });
        const json = await res.json().catch(() => ({}));
        alert(json.message || json.error || (res.ok ? "Enviado" : "Error al enviar"));
        if (res.ok) form.reset();
      };
    }

    // Re-init lightbox/reveal if editorial.js exposes hooks
    document.dispatchEvent(new CustomEvent("content:ready"));
  }

  document.addEventListener("DOMContentLoaded", async () => {
    try {
      const data = await load();
      render(data);
      document.getElementById("page-loader")?.classList.add("is-done");
    } catch (err) {
      console.error(err);
      const loader = document.getElementById("page-loader");
      if (loader) loader.innerHTML = `<p style="color:#C59B74;font-family:serif;padding:2rem;text-align:center">No se pudo conectar con el servidor.<br><small>${err.message}</small></p>`;
    }
  });
})();
