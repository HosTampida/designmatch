const state = {
    designers: [],
    filteredDesigners: [],
    skills: [],
    styles: [],
    stats: null,
    info: null,
    currentUser: null,
    selectedDesignerId: null,
    heroCarousel: {
        activeIndex: 0,
        timerId: null,
    },
    projectTitle: '',
};


function contactDesigner(phone, name, projectTitle) {
    if (!phone) {
        alert("Este diseñador aún no tiene número disponible");
        return;
    
    }

    const cleanPhone = phone.toString().replace(/[\s+\-()]/g, '');

    const message = `Hola ${name}, vi tu perfil en DesignMatch 🚀  
Estoy interesado en trabajar contigo en: "${projectTitle}"  
¿Tienes disponibilidad?`;

    const url = `https://wa.me/${cleanPhone}?text=${encodeURIComponent(message)}`;

    window.open(url, '_blank');
}


document.addEventListener("DOMContentLoaded", async () => {
    restoreSession();
    bindEvents();
    initHeroCarousel();
    await Promise.all([loadHealth(), loadInfo(), loadStats(), loadReferenceData(), loadDesigners()]);
});


function bindEvents() {
    document.getElementById("projectForm").addEventListener("submit", handleProjectSubmit);
    document.getElementById("registerForm").addEventListener("submit", handleRegister);
    document.getElementById("loginForm").addEventListener("submit", handleLogin);
    document.getElementById("applyFilters").addEventListener("click", applyFilters);
    document.getElementById("clearFilters").addEventListener("click", clearFilters);
    document.getElementById("logoutButton").addEventListener("click", handleLogout);

    document.getElementById("closeProfileDialog").addEventListener("click", () => closeDialog("profileDialog"));
    document.getElementById("closeInfoDialog").addEventListener("click", () => closeDialog("infoDialog"));
    document.getElementById("closeAccessDialog").addEventListener("click", () => closeDialog("accessDialog"));

    document.querySelectorAll("[data-open-access]").forEach((button) => {
        button.addEventListener("click", () => openAccessDialog(button.dataset.openAccess));
    });

    document.querySelectorAll("[data-action]").forEach((button) => {
        button.addEventListener("click", () => handleAction(button.dataset.action));
    });

    // Toggle auth forms
    document.querySelectorAll("[data-toggle]").forEach(btn => {
        btn.addEventListener("click", (e) => {
            e.preventDefault();
            openAccessDialog(e.target.dataset.toggle);
        });
    });

    // Handle role toggle for conditional fields
    document.getElementById("roleSelect").addEventListener("change", toggleRoleFields);

    document.querySelectorAll("dialog").forEach((dialog) => {
        dialog.addEventListener("click", (event) => {
            const rect = dialog.getBoundingClientRect();
            const inside =
                event.clientX >= rect.left &&
                event.clientX <= rect.right &&
                event.clientY >= rect.top &&
                event.clientY <= rect.bottom;

            if (!inside) {
                dialog.close();
            }
        });
    });
}

function initHeroCarousel() {
    const carousel = document.getElementById("heroCarousel");
    if (!carousel) {
        return;
    }

    const slides = Array.from(carousel.querySelectorAll(".hero-slide"));
    const dots = Array.from(document.querySelectorAll("[data-slide-target]"));
    const prevButton = document.getElementById("heroPrev");
    const nextButton = document.getElementById("heroNext");

    if (!slides.length) {
        return;
    }

    const SLIDE_DURATION = 5000; // 5 seconds

    const renderCarousel = (index) => {
        state.heroCarousel.activeIndex = index;

        slides.forEach((slide, slideIndex) => {
            slide.classList.toggle("is-active", slideIndex === index);
        });

        dots.forEach((dot, dotIndex) => {
            dot.classList.toggle("is-active", dotIndex === index);
            dot.setAttribute("aria-current", dotIndex === index ? "true" : "false");
        });
    };

    const goToSlide = (index) => {
        const totalSlides = slides.length;
        const nextIndex = (index % totalSlides + totalSlides) % totalSlides;
        renderCarousel(nextIndex);
    };

    const restartAutoplay = () => {
        window.clearInterval(state.heroCarousel.timerId);
        state.heroCarousel.timerId = window.setInterval(() => {
            goToSlide(state.heroCarousel.activeIndex + 1);
        }, SLIDE_DURATION);
    };

    const handlePrev = () => {
        goToSlide(state.heroCarousel.activeIndex - 1);
        restartAutoplay();
    };

    const handleNext = () => {
        goToSlide(state.heroCarousel.activeIndex + 1);
        restartAutoplay();
    };

    const handleDotClick = (dot) => {
        goToSlide(Number(dot.dataset.slideTarget));
        restartAutoplay();
    };

    prevButton.addEventListener("click", handlePrev);
    nextButton.addEventListener("click", handleNext);

    dots.forEach((dot) => {
        dot.addEventListener("click", () => handleDotClick(dot));
    });

    // Pause on hover, resume on leave
    carousel.addEventListener("mouseenter", () => window.clearInterval(state.heroCarousel.timerId));
    carousel.addEventListener("mouseleave", restartAutoplay);

    // Keyboard navigation
    document.addEventListener("keydown", (event) => {
        if (event.key === "ArrowLeft") handlePrev();
        if (event.key === "ArrowRight") handleNext();
    });

    renderCarousel(0);
    restartAutoplay();
}

async function toggleRoleFields() {
    const role = document.getElementById("roleSelect").value;
    const designerFields = document.querySelectorAll(".designer-fields");
    const clientFields = document.querySelectorAll(".client-fields");

    if (role === "designer") {
        designerFields.forEach((field) => {
            field.style.display = "block";
        });
        clientFields.forEach((field) => {
            field.style.display = "none";
        });
        await loadRegSkills();
    } else {
        designerFields.forEach((field) => {
            field.style.display = "none";
        });
        clientFields.forEach((field) => {
            field.style.display = "block";
        });
    }
}

async function loadRegSkills() {
    try {
        const response = await api("/api/skills");
        renderChipOptions("regSkillsOptions", response.data, "reg_skill_ids");
    } catch (error) {
        console.error("Failed to load skills for reg:", error);
    }
}

async function loadHealth() {
    try {
        const response = await api("/api/health");
        document.getElementById("metricStatus").textContent = response.data.status === "ok" ? "Activo" : "Revisar";
    } catch (_error) {
        document.getElementById("metricStatus").textContent = "Caido";
    }
}


async function loadInfo() {
    const response = await api("/api/info");
    state.info = response.data;
}


async function loadStats() {
    const response = await api("/api/stats");
    state.stats = response.data;
    document.getElementById("metricProjects").textContent = String(state.stats.projects || 0);
}


async function loadReferenceData() {
    const [skillsResponse, stylesResponse] = await Promise.all([
        api("/api/skills"),
        api("/api/styles"),
    ]);

    state.skills = skillsResponse.data;
    state.styles = stylesResponse.data;

    renderChipOptions("skillsOptions", state.skills, "skill_ids");
    renderChipOptions("stylesOptions", state.styles, "style_ids");
    populateFilterSelect("filterSkill", state.skills);
    populateFilterSelect("filterStyle", state.styles);
}


async function loadDesigners() {
    const response = await api("/api/designers");
    state.designers = response.data;
    state.filteredDesigners = [...state.designers];

    document.getElementById("metricDesigners").textContent = String(state.designers.length);
    renderDesigners();
}


function renderChipOptions(containerId, items, fieldName) {
    const container = document.getElementById(containerId);
    container.innerHTML = items
        .map(
            (item, index) => `
                <label class="chip-option">
                    <input type="checkbox" name="${fieldName}" value="${item.id}" ${index < 2 ? "checked" : ""}>
                    <span>${item.name}</span>
                </label>
            `
        )
        .join("");
}


function populateFilterSelect(id, items) {
    const target = document.getElementById(id);
    target.innerHTML += items.map((item) => `<option value="${item.name}">${item.name}</option>`).join("");
}


function renderDesigners() {
    const grid = document.getElementById("designersGrid");

    if (!state.filteredDesigners.length) {
        grid.innerHTML = `
            <div class="empty-state">
                No encontramos disenadores con esos filtros. Prueba otro rango o limpia la busqueda.
            </div>
        `;
        return;
    }

    grid.innerHTML = state.filteredDesigners
        .map((designer) => {
            const isSelected = state.selectedDesignerId === designer.designer_id ? " selected" : "";

            return `
                <article class="designer-card${isSelected}" id="designer-${designer.designer_id}">
                    <div class="avatar-container">
                        <img class="designer-avatar" 
                             src="${designer.avatar_url || '/static/img/default-designer.svg'}" 
                             alt="${designer.name} avatar"
                             loading="lazy" 
                             onerror="this.src='/static/img/default-designer.svg'; this.onerror=null;">
                    </div>
                    <div class="designer-header">
                        <div>
                            <span class="designer-badge">Estudiante recomendado</span>
                            <h3 class="designer-name">${designer.name}</h3>
                            <p class="designer-email">${designer.email}</p>
                        </div>
                        <span class="rating-pill">${Number(designer.rating || 0).toFixed(1)} / 5</span>
                    </div>

                    <p class="designer-bio">${designer.bio || "Perfil sin descripcion."}</p>

                    <div class="designer-skills">
                        ${designer.skills.map((skill) => `<span class="tag">${skill}</span>`).join("")}
                    </div>

                    <div class="designer-styles">
                        ${designer.styles.map((style) => `<span class="tag tag-soft">${style}</span>`).join("")}
                    </div>

                    <div class="designer-meta">
                        <div class="designer-price">
                            <strong>$${Math.round(designer.price_min)} - $${Math.round(designer.price_max)}</strong>
                            <span>Rango estimado</span>
                        </div>
                        <a href="${designer.portfolio_url}" target="_blank" rel="noreferrer">Ver portafolio</a>
                    </div>

                    <div class="card-actions">
                        <button type="button" class="btn btn-outline" data-profile-id="${designer.designer_id}">Ver perfil</button>
                        ${designer.phone 
  ? `<button class="btn btn-primary btn-whatsapp" data-pick-id="${designer.designer_id}">📱 Contactar</button>`
  : `<button class="btn btn-outline" data-pick-id="${designer.designer_id}">Elegir</button>`
}
                    </div>
                </article>
            `;
        })
        .join("");


    grid.querySelectorAll("[data-profile-id]").forEach((button) => {
        button.addEventListener("click", () => openProfile(Number(button.dataset.profileId)));
    });

    grid.querySelectorAll("[data-pick-id]").forEach((button) => {
        button.addEventListener("click", () => {
            const id = Number(button.dataset.pickId);
            const designer = state.designers.find(d => d.designer_id === id);
            if (!designer) return;

            if (state.currentUser && state.currentUser.role === "admin") {
                if (confirm(`Delete designer ${designer.name}?`)) {
                    api(`/api/users/${id}`, {method: "DELETE"}).then(() => {
                        loadDesigners();
                        alert("Designer deleted");
                    }).catch(err => alert("Error: " + err.message));
                }
                return;
            }

            contactDesigner(
                designer.phone || null,
                designer.name,
                state.projectTitle || "mi proyecto"
            );
        });
    });
}


async function applyFilters() {
    const skillValue = document.getElementById("filterSkill").value;
    const styleValue = document.getElementById("filterStyle").value;
    const budgetValue = document.getElementById("filterBudget").value;

    let queryUrl = "/api/designers";
    const params = [];

    if (skillValue) params.push(`skill=${encodeURIComponent(skillValue)}`);
    if (styleValue) params.push(`style=${encodeURIComponent(styleValue)}`);
    if (budgetValue) params.push(`max_price=${budgetValue}`);

    if (params.length > 0) {
        queryUrl += `?${params.join("&")}`;
    }

    try {
        const response = await api(queryUrl);
        state.filteredDesigners = response.data;
        renderDesigners();
    } catch (error) {
        console.error("Filter failed:", error);
        renderError("Error al aplicar filtros. Intentando cargar todos...");
        await loadDesigners();
    }
}


function clearFilters() {
    document.getElementById("filterSkill").value = "";
    document.getElementById("filterStyle").value = "";
    document.getElementById("filterBudget").value = "";
    state.filteredDesigners = [...state.designers];
    renderDesigners();
}


async function handleProjectSubmit(event) {
    event.preventDefault();

    const button = document.getElementById("submitProject");
    const hint = document.getElementById("resultsHint");
    button.disabled = true;
    button.textContent = "Buscando matches...";

    try {
        const form = event.currentTarget;
        const payload = formToProjectPayload(form);
        state.projectTitle = payload.title;
        const createResponse = await api("/api/projects", {
            method: "POST",
            body: JSON.stringify(payload),
        });

        const matchesResponse = await api(`/api/projects/${createResponse.data.project_id}/matches`);
        renderMatches(matchesResponse.data);
        hint.textContent = `Resultados para "${createResponse.data.title}" listos para presentar.`;
        await loadStats();
    } catch (error) {
        renderError(error.message || "No fue posible procesar el proyecto.");
    } finally {
        button.disabled = false;
        button.textContent = "Encontrar mejores disenadores";
    }
}


function formToProjectPayload(form) {
    const data = new FormData(form);

    return {
        title: String(data.get("title") || "").trim(),
        description: String(data.get("description") || "").trim(),
        budget_min: Number(data.get("budget_min") || 0),
        budget_max: Number(data.get("budget_max") || 0),
        urgency: String(data.get("urgency") || "medium"),
        skill_ids: collectCheckedValues("skill_ids"),
        style_ids: collectCheckedValues("style_ids"),
    };
}


function collectCheckedValues(fieldName) {
    return Array.from(document.querySelectorAll(`input[name="${fieldName}"]:checked`))
        .map((input) => Number(input.value))
        .filter((value) => Number.isInteger(value));
}


function renderMatches(matches) {
    const container = document.getElementById("resultsContainer");

    if (!matches.length) {
        container.className = "results-list empty-state";
        container.textContent = "No se encontraron disenadores para este proyecto.";
        return;
    }

    container.className = "results-list";
    container.innerHTML = matches
        .map(
            (match, index) => `
                <article class="match-card">
                    <div style="display: flex; align-items: center; gap: 12px;">
                        <div class="match-avatar-container">
                            <img class="designer-avatar" style="width: 60px; height: 60px; border-radius: 12px; object-fit: cover;" 
                                 src="${match.avatar_url || '/static/img/default-designer.svg'}" 
                                 alt="${match.name} avatar"
                                 loading="lazy" 
                                 onerror="this.src='/static/img/default-designer.svg'; this.onerror=null;">
                        </div>
                        <div>
                            <div class="match-rank">Top ${index + 1}</div>
                            <h3 class="match-name">${match.name}</h3>
                            <p class="match-score">${match.score.toFixed(1)} / 100 de compatibilidad</p>
                            <p class="match-price">Rango: $${Math.round(match.price_min)} - $${Math.round(match.price_max)}</p>
                        </div>
                    </div>
                    <div class="match-actions">
                        <a class="btn btn-outline" href="${match.portfolio_url}" target="_blank" rel="noreferrer">Portafolio</a>
                        <button type="button" class="btn btn-primary" data-match-profile="${match.designer_id}">Ver perfil</button>
                    </div>
                </article>
            `
        )

        .join("");

    container.querySelectorAll("[data-match-profile]").forEach((button) => {
        button.addEventListener("click", () => openProfile(Number(button.dataset.matchProfile)));
    });

    if (matches[0]) {
        pickDesigner(matches[0].designer_id, false);
    }
}


function renderError(message) {
    const container = document.getElementById("resultsContainer");
    container.className = "results-list empty-state error-state";
    container.textContent = message;
}


function openProfile(designerId) {
    const designer = state.designers.find((item) => item.designer_id === designerId);
    if (!designer) {
        return;
    }

    document.getElementById("profileContent").innerHTML = `
        <div style="display: flex; align-items: center; gap: 20px; margin-bottom: 20px;">
            <div class="avatar-container">
                <img class="designer-avatar designer-avatar--large" 
                     src="${designer.avatar_url || '/static/img/default-designer.svg'}" 
                     alt="${designer.name} avatar"
                     loading="lazy" 
                     onerror="this.src='/static/img/default-designer.svg'; this.onerror=null;">
            </div>
            <div>
                <p class="panel-kicker">Perfil del disenador</p>
                <h2 class="panel-title">${designer.name}</h2>
            </div>
        </div>
        <p class="modal-copy">${designer.bio}</p>
        <div class="profile-grid">
            <div>
                <span class="profile-label">Rango de precio</span>
                <strong>$${Math.round(designer.price_min)} - $${Math.round(designer.price_max)}</strong>
            </div>
            <div>
                <span class="profile-label">Calificacion</span>
                <strong>${Number(designer.rating || 0).toFixed(1)} / 5</strong>
            </div>
        </div>
        <div class="designer-skills">
            ${designer.skills.map((skill) => `<span class="tag">${skill}</span>`).join("")}
        </div>
        <div class="designer-styles">
            ${designer.styles.map((style) => `<span class="tag tag-soft">${style}</span>`).join("")}
        </div>
        <div class="profile-actions">
            <a class="btn btn-primary" href="${designer.portfolio_url}" target="_blank" rel="noreferrer">Abrir portafolio</a>
            <button type="button" class="btn btn-outline" id="profilePickButton">Elegir para mi proyecto</button>
        </div>
    `;


    showDialog("profileDialog");
    document.getElementById("profilePickButton").addEventListener("click", () => {
        closeDialog("profileDialog");
        pickDesigner(designerId);
    });
}


function pickDesigner(designerId, scrollToProject = true) {
    state.selectedDesignerId = designerId;
    renderDesigners();

    const designer = state.designers.find((item) => item.designer_id === designerId);
    document.getElementById("pickedDesigner").textContent = designer
        ? `Disenador elegido: ${designer.name}. Puedes usarlo como referencia mientras presentas el ranking.`
        : "Ningun disenador elegido manualmente.";

    if (scrollToProject) {
        document.getElementById("proyecto").scrollIntoView({ behavior: "smooth", block: "start" });
    }
}


function handleAction(action) {
    if (action === "refresh") {
        clearFilters();
        return;
    }

    if (action === "como-funciona") {
        document.getElementById("como-funciona").scrollIntoView({ behavior: "smooth", block: "start" });
        return;
    }

    if (action === "estado") {
        openInfoDialog(buildStatusHtml());
        return;
    }

    if (action === "info") {
        openInfoDialog(buildInfoHtml());
        return;
    }

    if (action === "soporte") {
        openInfoDialog(`
            <p class="panel-kicker">Soporte demo</p>
            <h2 class="panel-title">Todo listo para mostrar</h2>
            <p class="modal-copy">Puedes navegar el catalogo, crear un proyecto, abrir perfiles y explicar el ranking sin salir de la pagina.</p>
            <ul class="modal-list">
                <li>Catalogo con disenadores sembrados</li>
                <li>Formulario simple de proyecto</li>
                <li>Ranking visible y entendible</li>
                <li>Acciones demo para acceso y soporte</li>
            </ul>
        `);
    }
}


function openInfoDialog(content) {
    document.getElementById("infoContent").innerHTML = content;
    showDialog("infoDialog");
}


function buildStatusHtml() {
    const stats = state.stats || {};

    return `
        <p class="panel-kicker">Estado del sistema</p>
        <h2 class="panel-title">MVP conectado</h2>
        <p class="modal-copy">La aplicacion esta corriendo sobre SQLite y responde con datos semilla automaticamente.</p>
        <div class="stats-grid">
            <article><strong>${stats.designers || 0}</strong><span>Disenadores</span></article>
            <article><strong>${stats.projects || 0}</strong><span>Proyectos</span></article>
            <article><strong>${stats.matches || 0}</strong><span>Matches</span></article>
            <article><strong>${stats.skills || 0}</strong><span>Skills</span></article>
        </div>
    `;
}


function buildInfoHtml() {
    const info = state.info || {};
    const items = (info.features || []).map((item) => `<li>${item}</li>`).join("");

    return `
        <p class="panel-kicker">Informacion del MVP</p>
        <h2 class="panel-title">${info.name || "DesignMatch MVP"}</h2>
        <p class="modal-copy">${info.description || ""}</p>
        <ul class="modal-list">${items}</ul>
        <p class="modal-copy">Base de datos: ${info.database || "sqlite:///designmatch.db"}</p>
    `;
}


async function openAccessDialog(mode) {
    const registerForm = document.getElementById("registerForm");
    const loginForm = document.getElementById("loginForm");
    const title = document.getElementById("accessTitle");
    const copy = document.getElementById("accessCopy");
    const toggleText = document.getElementById("toggleText");

    clearAuthErrors();

    if (mode === "login") {
        title.textContent = "Bienvenido de vuelta";
        copy.textContent = "Inicia sesión para continuar con tus proyectos creativos.";
        toggleText.textContent = "¿Necesitas una cuenta? ";
        registerForm.classList.add("hidden");
        loginForm.classList.remove("hidden");
    } else {
        title.textContent = "Únete a DesignMatch";
        copy.textContent = "Crea tu cuenta gratuita como cliente o diseñador.";
        toggleText.textContent = "¿Ya tienes cuenta? ";
        registerForm.classList.remove("hidden");
        loginForm.classList.add("hidden");
        document.getElementById("roleSelect").dispatchEvent(new Event("change"));
    }

    initAuthCarousel();
    showDialog("accessDialog");
}


async function handleRegister(event) {
    event.preventDefault();
    const data = new FormData(event.currentTarget);
    const role = data.get("role");

        const payload = {
            name: String(data.get("name") || "").trim(),
            email: String(data.get("email") || "").trim(),
            phone: String(data.get("phone") || "").trim(),
            password: "demo123",
            role: role,
            ...(role === "designer" && {
                bio: String(data.get("bio") || "").trim(),
                portfolio_url: String(data.get("portfolio_url") || "").trim(),
                skills: collectCheckedValues("reg_skill_ids"),
                price_min: 100,
                price_max: 500,
            }),
            ...(role === "client" && {
                project_description: String(data.get("project_description") || "").trim(),
            }),
        };

    try {
        const response = await api("/api/users", {
            method: "POST",
            body: JSON.stringify(payload),
        });
        setCurrentUser(response.data);
        closeDialog("accessDialog");
        openInfoDialog(`
            <p class="panel-kicker">¡Éxito!</p>
            <h2 class="panel-title">Cuenta creada</h2>
            <p class="modal-copy">${response.message}. Ya puedes usar la plataforma.</p>
        `);
        await loadStats();
    } catch (error) {
        openInfoDialog(`
            <p class="panel-kicker">Error</p>
            <h2 class="panel-title">No se pudo crear la cuenta</h2>
            <p class="modal-copy">${error.message}</p>
        `);
    }
}


async function handleLogin(event) {
    event.preventDefault();
    const data = new FormData(event.currentTarget);

    try {
        const response = await api("/api/login", {
            method: "POST",
            body: JSON.stringify({ 
                email: String(data.get("email") || "").trim().toLowerCase(),
                password: String(data.get("password") || "").trim()
            }),
        });
        setCurrentUser({ ...response.data.user, token: response.data.token });
        localStorage.setItem("token", response.data.token); // Bonus direct token
        closeDialog("accessDialog");
        openInfoDialog(`
            <p class="panel-kicker">Bienvenido</p>
            <h2 class="panel-title">Sesión iniciada</h2>
            <p class="modal-copy">Hola, ${response.data.user.name}. (${response.data.user.role})</p>
        `);
    } catch (error) {
        openInfoDialog(`
            <p class="panel-kicker">Error</p>
            <h2 class="panel-title">No se pudo iniciar sesión</h2>
            <p class="modal-copy">${error.message}</p>
        `);
    }
}


function setCurrentUser(user) {
    state.currentUser = user;
    window.localStorage.setItem("designmatch_user", JSON.stringify(user));
    syncSessionBadges();
    updateNavButtons();
}

function clearCurrentUser() {
    state.currentUser = null;
    window.localStorage.removeItem("designmatch_user");
    syncSessionBadges();
    updateNavButtons();
}

function syncSessionBadges() {
    const label = state.currentUser
        ? `${state.currentUser.name} (${state.currentUser.role === "admin" ? "👑 ADMIN" : state.currentUser.role === "designer" ? "disenador" : "cliente"})`
        : "Sin sesion";

    document.getElementById("sessionBadge").textContent = label;

    const headerSessionBadge = document.getElementById("headerSessionBadge");
    if (headerSessionBadge) {
        headerSessionBadge.textContent = label;
    }
}


function restoreSession() {
    const raw = window.localStorage.getItem("designmatch_user");
    if (!raw) {
        syncSessionBadges();
        updateNavButtons();
        return;
    }

    try {
        state.currentUser = JSON.parse(raw);
        syncSessionBadges();
        updateNavButtons();
    } catch (_error) {
        clearCurrentUser();
    }
}

function updateNavButtons() {
    const navActions = document.getElementById("guestActions");
    const sessionActions = document.getElementById("sessionActions");

    if (state.currentUser) {
        navActions.classList.add("hidden");
        sessionActions.classList.remove("hidden");
    } else {
        navActions.classList.remove("hidden");
        sessionActions.classList.add("hidden");
    }
}

function handleLogout() {
    localStorage.removeItem("token");
    clearCurrentUser();
    openInfoDialog(`
        <p class="panel-kicker">Hasta pronto</p>
        <h2 class="panel-title">Sesion cerrada</h2>
        <p class="modal-copy">Tu sesion se cerro correctamente.</p>
    `);
}

function showDialog(id) {
    const dialog = document.getElementById(id);
    if (!dialog.open) {
        dialog.showModal();
    }
}


function closeDialog(id) {
    const dialog = document.getElementById(id);
    if (dialog.open) {
        dialog.close();
    }
}


async function api(url, options = {}) {
    const stored = localStorage.getItem("designmatch_user");
    let token = null;
    if (stored) {
        try {
            token = JSON.parse(stored).token;
        } catch (e) {
            console.error("[api] Token parse error", e);
        }
    }
    console.log("[api] Token loaded:", !!token);

    const headers = {
        ...(options.headers || {}),
        "Content-Type": "application/json",
        ...(token ? { Authorization: `Bearer ${token}` } : {})
    };

    const response = await fetch(url, {
        headers,
        ...options,
    });

    const payload = await response.json().catch(() => ({}));
    if (!response.ok) {
        console.error("[api] Request failed", { url, status: response.status, payload });
        throw new Error(payload.message || "La solicitud fallo");
    }

    return payload;
}
