document.addEventListener("DOMContentLoaded", () => {
    const fallbackDesigners = [
        {
            name: "Valentina R.",
            email: "valentina@designmatch.com",
            phone: "573001112233",
            bio: "Disenadora de branding y contenido visual para marcas emergentes.",
            avatar_url: null,
            price_min: 180,
            price_max: 420,
            rating: 4.9,
            portfolio_url: "#",
            skills: ["Branding", "Redes Sociales"],
            styles: ["Minimalista", "Editorial"],
        },
        {
            name: "Kenneth J.",
            email: "kenneth@designmatch.com",
            phone: "573001223344",
            bio: "Enfocado en interfaces, sistemas visuales y presentaciones para producto digital.",
            avatar_url: null,
            price_min: 220,
            price_max: 520,
            rating: 4.8,
            portfolio_url: "#",
            skills: ["UI Design", "Prototipos"],
            styles: ["Moderno", "Tecnologico"],
        },
        {
            name: "Michelle L.",
            email: "michelle@designmatch.com",
            phone: "",
            bio: "Especialista en piezas publicitarias, campanas y storytelling visual.",
            avatar_url: null,
            price_min: 160,
            price_max: 390,
            rating: 4.7,
            portfolio_url: "#",
            skills: ["Publicidad", "Ilustracion"],
            styles: ["Colorido", "Creativo"],
        },
    ];

    const state = {
        sliderIndex: 0,
        sliderTimer: null,
        currentAuthView: "login",
        token: localStorage.getItem("token") || "",
        user: parseStoredUser(),
    };

    const elements = {
        authModal: document.getElementById("authModal"),
        closeAuthModal: document.getElementById("closeAuthModal"),
        guestActions: document.getElementById("guestActions"),
        sessionActions: document.getElementById("sessionActions"),
        sessionUserName: document.getElementById("sessionUserName"),
        logoutButton: document.getElementById("logoutButton"),
        loginForm: document.getElementById("loginForm"),
        registerForm: document.getElementById("registerForm"),
        loginSubmit: document.getElementById("loginSubmit"),
        registerSubmit: document.getElementById("registerSubmit"),
        loginMessage: document.getElementById("loginMessage"),
        registerMessage: document.getElementById("registerMessage"),
        registerRole: document.getElementById("registerRole"),
        designerBioField: document.getElementById("designerBioField"),
        designerPortfolioField: document.getElementById("designerPortfolioField"),
        authTabs: Array.from(document.querySelectorAll("[data-auth-view]")),
        authTriggers: Array.from(document.querySelectorAll("[data-open-auth]")),
        loginView: document.getElementById("loginView"),
        registerView: document.getElementById("registerView"),
        toastContainer: document.getElementById("toastContainer"),
        metricDesigners: document.getElementById("metricDesigners"),
        metricProjects: document.getElementById("metricProjects"),
        metricHealth: document.getElementById("metricHealth"),
        sliderPrev: document.getElementById("sliderPrev"),
        sliderNext: document.getElementById("sliderNext"),
        slides: Array.from(document.querySelectorAll(".slide")),
        sliderDots: Array.from(document.querySelectorAll(".slider-dot")),
        designersGrid: document.getElementById("designersGrid"),
        designersFeedback: document.getElementById("designersFeedback"),
        refreshDesigners: document.getElementById("refreshDesigners"),
        dashboardSection: document.getElementById("dashboardSection"),
        dashboardTitle: document.getElementById("dashboardTitle"),
        dashboardMessage: document.getElementById("dashboardMessage"),
        dashboardName: document.getElementById("dashboardName"),
        dashboardEmail: document.getElementById("dashboardEmail"),
        dashboardRole: document.getElementById("dashboardRole"),
    };

    bindEvents();
    setAuthView("login");
    toggleDesignerFields();
    updateSessionUI();
    startSlider();
    loadInitialData();

    function bindEvents() {
        elements.authTriggers.forEach((button) => {
            button.addEventListener("click", () => {
                openAuthModal(button.dataset.openAuth || "login");
            });
        });

        if (elements.closeAuthModal) {
            elements.closeAuthModal.addEventListener("click", closeAuthModal);
        }

        if (elements.authModal) {
            elements.authModal.addEventListener("click", (event) => {
                if (event.target === elements.authModal) {
                    closeAuthModal();
                }
            });
        }

        document.addEventListener("keydown", (event) => {
            if (event.key === "Escape" && elements.authModal && !elements.authModal.classList.contains("hidden")) {
                closeAuthModal();
            }
        });

        elements.authTabs.forEach((tab) => {
            tab.addEventListener("click", () => {
                setAuthView(tab.dataset.authView || "login");
            });
        });

        if (elements.registerRole) {
            elements.registerRole.addEventListener("change", toggleDesignerFields);
        }

        if (elements.loginForm) {
            elements.loginForm.addEventListener("submit", handleLogin);
        }

        if (elements.registerForm) {
            elements.registerForm.addEventListener("submit", handleRegister);
        }

        if (elements.logoutButton) {
            elements.logoutButton.addEventListener("click", handleLogout);
        }

        if (elements.refreshDesigners) {
            elements.refreshDesigners.addEventListener("click", loadDesigners);
        }

        if (elements.designersGrid) {
            elements.designersGrid.addEventListener("click", (event) => {
                const whatsappButton = event.target.closest("[data-whatsapp]");
                if (!whatsappButton) {
                    return;
                }

                contactarDisenador({
                    name: whatsappButton.dataset.name || "disenador",
                    phone: whatsappButton.dataset.phone || "",
                    email: whatsappButton.dataset.email || "",
                });
            });
        }

        if (elements.sliderPrev) {
            elements.sliderPrev.addEventListener("click", () => {
                showSlide(state.sliderIndex - 1);
                restartSlider();
            });
        }

        if (elements.sliderNext) {
            elements.sliderNext.addEventListener("click", () => {
                showSlide(state.sliderIndex + 1);
                restartSlider();
            });
        }

        elements.sliderDots.forEach((dot) => {
            dot.addEventListener("click", () => {
                showSlide(Number(dot.dataset.slide || 0));
                restartSlider();
            });
        });
    }

    async function loadInitialData() {
        await Promise.all([loadHealth(), loadStats(), loadDesigners()]);
    }

    async function loadDesigners() {
        setFeedback("Cargando disenadores...");

        try {
            const response = await apiRequest("/api/designers");
            const designers = Array.isArray(response.data) && response.data.length ? response.data : fallbackDesigners;
            renderDesigners(designers);
            setFeedback("");
        } catch (error) {
            renderDesigners(fallbackDesigners);
            setFeedback("No fue posible cargar los disenadores desde la API. Se muestran perfiles de referencia.");
        }
    }

    function renderDesigners(designers) {
        if (!elements.designersGrid) {
            return;
        }

        elements.designersGrid.innerHTML = designers.map((designer) => {
            const avatar = getAvatar(designer);
            const skills = Array.isArray(designer.skills) ? designer.skills.slice(0, 2) : [];
            const styles = Array.isArray(designer.styles) ? designer.styles.slice(0, 2) : [];
            const tags = [...skills, ...styles].slice(0, 4);
            const role = styles.length ? styles.join(" / ") : "Disenador creativo";
            const priceText = designer.price_min || designer.price_max
                ? `$${formatNumber(designer.price_min || 0)} - $${formatNumber(designer.price_max || designer.price_min || 0)}`
                : "Tarifa a convenir";
            const sanitizedPhone = sanitizePhone(designer.phone);
            const hasWhatsapp = Boolean(sanitizedPhone);

            return `
                <article class="designer-card">
                    <div class="designer-top">
                        <img src="${escapeHtml(avatar)}" alt="Foto de ${escapeHtml(designer.name || "Disenador")}" class="designer-avatar">
                        <div>
                            <h3 class="designer-name">${escapeHtml(designer.name || "Disenador")}</h3>
                            <p class="designer-role">${escapeHtml(role)}</p>
                        </div>
                    </div>
                    <p class="designer-bio">${escapeHtml(designer.bio || "Perfil creativo disponible para proyectos visuales y colaboraciones.")}</p>
                    <div class="designer-tags">
                        ${tags.length ? tags.map((tag) => `<span class="tag">${escapeHtml(tag)}</span>`).join("") : '<span class="tag">Perfil verificado</span>'}
                    </div>
                    <div class="designer-footer">
                        <div>
                            <div class="designer-price">${escapeHtml(priceText)}</div>
                            <div class="designer-rating">Calificacion: ${escapeHtml(String(designer.rating || "4.8"))}</div>
                        </div>
                        <div class="designer-actions">
                            <a class="designer-link" href="${designer.portfolio_url && designer.portfolio_url !== "#" ? escapeHtml(designer.portfolio_url) : "#"}" ${designer.portfolio_url && designer.portfolio_url !== "#" ? 'target="_blank" rel="noopener noreferrer"' : ""}>Ver perfil</a>
                            ${hasWhatsapp ? `<button type="button" class="designer-whatsapp" data-whatsapp="true" data-name="${escapeHtml(designer.name || "Disenador")}" data-phone="${escapeHtml(sanitizedPhone)}" data-email="${escapeHtml(designer.email || "")}">Contactar por WhatsApp</button>` : ""}
                        </div>
                    </div>
                </article>
            `;
        }).join("");
    }

    function getAvatar(user) {
        if (!user || !user.avatar_url || String(user.avatar_url).trim() === "") {
            const seed = user?.email || user?.name || "designmatch";
            return `https://api.dicebear.com/7.x/initials/svg?seed=${encodeURIComponent(seed)}`;
        }
        return user.avatar_url;
    }

    function contactarDisenador(user, proyecto = "tu proyecto") {
        const phone = sanitizePhone(user?.phone);
        if (!phone) {
            showToast("Este disenador no tiene WhatsApp disponible.", "error");
            return;
        }

        const mensaje = `Hola ${user.name || "disenador"}, vi tu perfil en DesignMatch y me interesa trabajar contigo en ${proyecto}.`;
        const url = `https://wa.me/${phone}?text=${encodeURIComponent(mensaje)}`;
        window.open(url, "_blank", "noopener");
    }

    async function loadStats() {
        try {
            const response = await apiRequest("/api/stats");
            if (elements.metricDesigners) {
                elements.metricDesigners.textContent = String(response.data?.designers ?? 0);
            }
            if (elements.metricProjects) {
                elements.metricProjects.textContent = String(response.data?.projects ?? 0);
            }
        } catch (error) {
            if (elements.metricDesigners) {
                elements.metricDesigners.textContent = String(fallbackDesigners.length);
            }
            if (elements.metricProjects) {
                elements.metricProjects.textContent = "0";
            }
        }
    }

    async function loadHealth() {
        try {
            const response = await apiRequest("/api/health");
            const status = response.data?.status || response.status || "activo";
            if (elements.metricHealth) {
                elements.metricHealth.textContent = capitalize(String(status));
            }
        } catch (error) {
            if (elements.metricHealth) {
                elements.metricHealth.textContent = "Offline";
            }
        }
    }

    function openAuthModal(view) {
        if (!elements.authModal) {
            return;
        }

        setAuthView(view);
        elements.authModal.classList.remove("hidden");
        elements.authModal.setAttribute("aria-hidden", "false");
        document.body.style.overflow = "hidden";
    }

    function closeAuthModal() {
        if (!elements.authModal) {
            return;
        }

        elements.authModal.classList.add("hidden");
        elements.authModal.setAttribute("aria-hidden", "true");
        document.body.style.overflow = "";
        clearFormMessage(elements.loginMessage);
        clearFormMessage(elements.registerMessage);
    }

    function setAuthView(view) {
        state.currentAuthView = view === "register" ? "register" : "login";
        const showLogin = state.currentAuthView === "login";

        if (elements.loginView) {
            elements.loginView.classList.toggle("hidden", !showLogin);
        }

        if (elements.registerView) {
            elements.registerView.classList.toggle("hidden", showLogin);
        }

        elements.authTabs.forEach((tab) => {
            const isActive = tab.dataset.authView === state.currentAuthView;
            tab.classList.toggle("is-active", isActive);
        });
    }

    function toggleDesignerFields() {
        const isDesigner = elements.registerRole && elements.registerRole.value === "designer";
        if (elements.designerBioField) {
            elements.designerBioField.classList.toggle("hidden", !isDesigner);
        }
        if (elements.designerPortfolioField) {
            elements.designerPortfolioField.classList.toggle("hidden", !isDesigner);
        }
    }

    async function handleLogin(event) {
        event.preventDefault();
        clearFormMessage(elements.loginMessage);

        const formData = new FormData(elements.loginForm);
        const payload = {
            email: String(formData.get("email") || "").trim().toLowerCase(),
            password: String(formData.get("password") || "").trim(),
        };

        if (!payload.email || !payload.password) {
            showFormMessage(elements.loginMessage, "Debes ingresar correo y contrasena.", "error");
            return;
        }

        setButtonLoading(elements.loginSubmit, true, "Ingresando...");

        try {
            const response = await apiRequest("/api/auth/login", {
                method: "POST",
                body: JSON.stringify(payload),
            });

            persistSession(response.data);
            updateSessionUI();
            elements.loginForm.reset();
            showToast("Sesion iniciada correctamente.", "success");
            closeAuthModal();
        } catch (error) {
            showFormMessage(elements.loginMessage, error.message || "No se pudo iniciar sesion.", "error");
        } finally {
            setButtonLoading(elements.loginSubmit, false);
        }
    }

    async function handleRegister(event) {
        event.preventDefault();
        clearFormMessage(elements.registerMessage);

        const formData = new FormData(elements.registerForm);
        const role = String(formData.get("role") || "client").trim().toLowerCase();
        const payload = {
            name: String(formData.get("name") || "").trim(),
            email: String(formData.get("email") || "").trim().toLowerCase(),
            phone: String(formData.get("phone") || "").trim(),
            password: String(formData.get("password") || "").trim(),
            role,
            project_description: String(formData.get("project_description") || "").trim(),
        };

        if (role === "designer") {
            payload.bio = String(formData.get("bio") || "").trim();
            payload.portfolio_url = String(formData.get("portfolio_url") || "").trim();
            payload.price_min = 100;
            payload.price_max = 500;
        }

        if (!payload.name || !payload.email || !payload.password) {
            showFormMessage(elements.registerMessage, "Nombre, correo y contrasena son obligatorios.", "error");
            return;
        }

        setButtonLoading(elements.registerSubmit, true, "Creando cuenta...");

        try {
            const response = await apiRequest("/api/auth/register", {
                method: "POST",
                body: JSON.stringify(payload),
            });

            persistSession(response.data);
            updateSessionUI();
            elements.registerForm.reset();
            toggleDesignerFields();
            showToast("Cuenta creada con exito.", "success");
            closeAuthModal();
        } catch (error) {
            showFormMessage(elements.registerMessage, error.message || "No se pudo crear la cuenta.", "error");
        } finally {
            setButtonLoading(elements.registerSubmit, false);
        }
    }

    function handleLogout() {
        clearSession();
        updateSessionUI();
        showToast("Sesion cerrada.", "success");
    }

    function updateSessionUI() {
        const isLoggedIn = Boolean(state.token && state.user);

        if (elements.guestActions) {
            elements.guestActions.classList.toggle("hidden", isLoggedIn);
        }

        if (elements.sessionActions) {
            elements.sessionActions.classList.toggle("hidden", !isLoggedIn);
        }

        if (elements.dashboardSection) {
            elements.dashboardSection.classList.toggle("hidden", !isLoggedIn);
        }

        if (!isLoggedIn) {
            return;
        }

        const user = state.user || {};
        const role = user.role === "designer" ? "Disenador" : "Cliente";

        if (elements.sessionUserName) {
            elements.sessionUserName.textContent = user.name || "Usuario";
        }
        if (elements.dashboardTitle) {
            elements.dashboardTitle.textContent = `Bienvenido, ${user.name || "usuario"}`;
        }
        if (elements.dashboardMessage) {
            elements.dashboardMessage.textContent = `Tu cuenta de ${role.toLowerCase()} esta activa y el token ya quedo guardado para futuras solicitudes autenticadas.`;
        }
        if (elements.dashboardName) {
            elements.dashboardName.textContent = user.name || "-";
        }
        if (elements.dashboardEmail) {
            elements.dashboardEmail.textContent = user.email || "-";
        }
        if (elements.dashboardRole) {
            elements.dashboardRole.textContent = role;
        }
    }

    function persistSession(data) {
        state.token = data?.token || "";
        state.user = data?.user || null;
        localStorage.setItem("token", state.token);
        localStorage.setItem("currentUser", JSON.stringify(state.user));
    }

    function clearSession() {
        state.token = "";
        state.user = null;
        localStorage.removeItem("token");
        localStorage.removeItem("currentUser");
    }

    function startSlider() {
        if (elements.slides.length < 2) {
            return;
        }

        state.sliderTimer = window.setInterval(() => {
            showSlide(state.sliderIndex + 1);
        }, 5000);
    }

    function restartSlider() {
        if (state.sliderTimer) {
            window.clearInterval(state.sliderTimer);
        }
        startSlider();
    }

    function showSlide(index) {
        if (!elements.slides.length) {
            return;
        }

        const total = elements.slides.length;
        state.sliderIndex = (index + total) % total;

        elements.slides.forEach((slide, slideIndex) => {
            slide.classList.toggle("is-active", slideIndex === state.sliderIndex);
        });

        elements.sliderDots.forEach((dot, dotIndex) => {
            dot.classList.toggle("is-active", dotIndex === state.sliderIndex);
        });
    }

    function setButtonLoading(button, isLoading, loadingText) {
        if (!button) {
            return;
        }

        if (!button.dataset.defaultText) {
            button.dataset.defaultText = button.textContent || "";
        }

        button.disabled = isLoading;
        button.textContent = isLoading ? loadingText : button.dataset.defaultText;
    }

    function showFormMessage(target, message, type) {
        if (!target) {
            return;
        }

        target.textContent = message;
        target.classList.remove("hidden", "error", "success");
        target.classList.add(type === "success" ? "success" : "error");
    }

    function clearFormMessage(target) {
        if (!target) {
            return;
        }

        target.textContent = "";
        target.classList.add("hidden");
        target.classList.remove("error", "success");
    }

    function showToast(message, type) {
        if (!elements.toastContainer) {
            return;
        }

        const toast = document.createElement("div");
        toast.className = `toast ${type === "error" ? "toast-error" : "toast-success"}`;
        toast.textContent = message;
        elements.toastContainer.appendChild(toast);

        window.setTimeout(() => {
            toast.remove();
        }, 3200);
    }

    function setFeedback(message) {
        if (!elements.designersFeedback) {
            return;
        }

        elements.designersFeedback.textContent = message;
        elements.designersFeedback.classList.toggle("hidden", !message);
    }

    async function apiRequest(url, options = {}) {
        const response = await fetch(url, {
            ...options,
            headers: {
                "Content-Type": "application/json",
                ...(state.token ? { Authorization: `Bearer ${state.token}` } : {}),
                ...(options.headers || {}),
            },
        });

        const payload = await response.json().catch(() => ({}));
        if (!response.ok) {
            if (response.status === 401 && state.token) {
                clearSession();
                updateSessionUI();
                openAuthModal("login");
                showToast("Tu sesion expiro. Inicia sesion nuevamente.", "error");
            }
            throw new Error(payload.message || `Error ${response.status}`);
        }

        return payload;
    }

    function parseStoredUser() {
        try {
            return JSON.parse(localStorage.getItem("currentUser") || "null");
        } catch (error) {
            localStorage.removeItem("currentUser");
            return null;
        }
    }

    function escapeHtml(value) {
        return String(value)
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#39;");
    }

    function formatNumber(value) {
        return new Intl.NumberFormat("es-CO").format(Number(value) || 0);
    }

    function sanitizePhone(value) {
        return String(value || "").replace(/[^\d]/g, "");
    }

    function capitalize(value) {
        if (!value) {
            return "";
        }

        return value.charAt(0).toUpperCase() + value.slice(1);
    }
});
