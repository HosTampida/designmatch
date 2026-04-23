document.addEventListener("DOMContentLoaded", () => {
    const state = {
        currentView: "login",
        sliderIndex: 0,
        sliderTimer: null,
        token: localStorage.getItem("token") || "",
        user: parseStoredUser(),
    };

    const elements = {
        authModal: document.getElementById("authModal"),
        closeAuthModal: document.getElementById("closeAuthModal"),
        guestActions: document.getElementById("guestActions"),
        sessionMenu: document.getElementById("sessionMenu"),
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
        dashboardSection: document.getElementById("dashboardSection"),
        dashboardGreeting: document.getElementById("dashboardGreeting"),
        dashboardRole: document.getElementById("dashboardRole"),
        dashboardSummary: document.getElementById("dashboardSummary"),
        dashboardName: document.getElementById("dashboardName"),
        dashboardEmail: document.getElementById("dashboardEmail"),
        dashboardPhone: document.getElementById("dashboardPhone"),
        sessionStatus: document.getElementById("sessionStatus"),
        copyTokenButton: document.getElementById("copyTokenButton"),
        switchAccountButton: document.getElementById("switchAccountButton"),
        authTabs: Array.from(document.querySelectorAll("[data-auth-view]")),
        authTriggers: Array.from(document.querySelectorAll("[data-open-auth]")),
        loginView: document.getElementById("loginView"),
        registerView: document.getElementById("registerView"),
        toastStack: document.getElementById("toastStack"),
        designersCount: document.getElementById("designersCount"),
        projectsCount: document.getElementById("projectsCount"),
        healthStatus: document.getElementById("healthStatus"),
        sliderPrev: document.getElementById("sliderPrev"),
        sliderNext: document.getElementById("sliderNext"),
        slides: Array.from(document.querySelectorAll(".slide")),
        sliderDots: Array.from(document.querySelectorAll(".slider-dot")),
    };

    bindEvents();
    setAuthView(state.currentView);
    toggleDesignerFields();
    updateSessionUI();
    startSlider();
    loadStats();
    loadHealth();

    function bindEvents() {
        elements.authTriggers.forEach((trigger) => {
            trigger.addEventListener("click", () => {
                const view = trigger.dataset.openAuth || "login";
                if (trigger.id === "switchAccountButton") {
                    clearSession();
                    updateSessionUI();
                }
                openAuthModal(view);
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
            if (event.key === "Escape" && elements.authModal && !elements.authModal.classList.contains("is-hidden")) {
                closeAuthModal();
            }
        });

        elements.authTabs.forEach((tab) => {
            tab.addEventListener("click", () => setAuthView(tab.dataset.authView));
        });

        if (elements.loginForm) {
            elements.loginForm.addEventListener("submit", handleLogin);
        }

        if (elements.registerForm) {
            elements.registerForm.addEventListener("submit", handleRegister);
        }

        if (elements.registerRole) {
            elements.registerRole.addEventListener("change", toggleDesignerFields);
        }

        if (elements.logoutButton) {
            elements.logoutButton.addEventListener("click", () => {
                clearSession();
                updateSessionUI();
                showToast("You have been logged out.", "success");
            });
        }

        if (elements.copyTokenButton) {
            elements.copyTokenButton.addEventListener("click", handleCopyToken);
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
                const index = Number(dot.dataset.slideTarget || 0);
                showSlide(index);
                restartSlider();
            });
        });
    }

    function openAuthModal(view) {
        if (!elements.authModal) {
            return;
        }

        setAuthView(view);
        elements.authModal.classList.remove("is-hidden");
        elements.authModal.setAttribute("aria-hidden", "false");
        document.body.style.overflow = "hidden";
    }

    function closeAuthModal() {
        if (!elements.authModal) {
            return;
        }

        elements.authModal.classList.add("is-hidden");
        elements.authModal.setAttribute("aria-hidden", "true");
        document.body.style.overflow = "";
        clearFormMessage(elements.loginMessage);
        clearFormMessage(elements.registerMessage);
    }

    function setAuthView(view) {
        state.currentView = view === "register" ? "register" : "login";
        const isLogin = state.currentView === "login";

        if (elements.loginView) {
            elements.loginView.classList.toggle("is-hidden", !isLogin);
        }

        if (elements.registerView) {
            elements.registerView.classList.toggle("is-hidden", isLogin);
        }

        elements.authTabs.forEach((tab) => {
            const active = tab.dataset.authView === state.currentView;
            tab.classList.toggle("is-active", active);
            tab.setAttribute("aria-selected", String(active));
        });
    }

    function toggleDesignerFields() {
        const isDesigner = elements.registerRole && elements.registerRole.value === "designer";
        if (elements.designerBioField) {
            elements.designerBioField.classList.toggle("is-hidden", !isDesigner);
        }
        if (elements.designerPortfolioField) {
            elements.designerPortfolioField.classList.toggle("is-hidden", !isDesigner);
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
            showFormMessage(elements.loginMessage, "Email and password are required.", "error");
            return;
        }

        setButtonLoading(elements.loginSubmit, true, "Signing in...");

        try {
            const response = await apiRequest("/api/auth/login", {
                method: "POST",
                body: JSON.stringify(payload),
            });

            persistSession(response.data);
            updateSessionUI();
            elements.loginForm.reset();
            showToast("Login successful.", "success");
            closeAuthModal();
        } catch (error) {
            showFormMessage(elements.loginMessage, error.message || "Unable to log in.", "error");
        } finally {
            setButtonLoading(elements.loginSubmit, false, "Log in");
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
            showFormMessage(elements.registerMessage, "Name, email, and password are required.", "error");
            return;
        }

        setButtonLoading(elements.registerSubmit, true, "Creating account...");

        try {
            const response = await apiRequest("/api/auth/register", {
                method: "POST",
                body: JSON.stringify(payload),
            });

            persistSession(response.data);
            updateSessionUI();
            elements.registerForm.reset();
            toggleDesignerFields();
            showToast("Account created successfully.", "success");
            closeAuthModal();
        } catch (error) {
            showFormMessage(elements.registerMessage, error.message || "Unable to create account.", "error");
        } finally {
            setButtonLoading(elements.registerSubmit, false, "Create account");
        }
    }

    async function loadStats() {
        try {
            const response = await apiRequest("/api/stats");
            if (elements.designersCount) {
                elements.designersCount.textContent = String(response.data?.designers ?? 0);
            }
            if (elements.projectsCount) {
                elements.projectsCount.textContent = String(response.data?.projects ?? 0);
            }
        } catch (error) {
            if (elements.designersCount) {
                elements.designersCount.textContent = "N/A";
            }
            if (elements.projectsCount) {
                elements.projectsCount.textContent = "N/A";
            }
        }
    }

    async function loadHealth() {
        try {
            const response = await apiRequest("/api/health");
            const status = response.data?.status || response.status || "healthy";
            if (elements.healthStatus) {
                elements.healthStatus.textContent = String(status).replace(/^./, (letter) => letter.toUpperCase());
            }
        } catch (error) {
            if (elements.healthStatus) {
                elements.healthStatus.textContent = "Offline";
            }
        }
    }

    function updateSessionUI() {
        const isLoggedIn = Boolean(state.token && state.user);

        if (elements.guestActions) {
            elements.guestActions.classList.toggle("is-hidden", isLoggedIn);
        }

        if (elements.sessionMenu) {
            elements.sessionMenu.classList.toggle("is-hidden", !isLoggedIn);
        }

        if (elements.dashboardSection) {
            elements.dashboardSection.classList.toggle("is-hidden", !isLoggedIn);
        }

        if (!isLoggedIn) {
            return;
        }

        const user = state.user || {};
        const role = formatRole(user.role);
        const firstName = String(user.name || "there").split(" ")[0];

        if (elements.sessionUserName) {
            elements.sessionUserName.textContent = user.name || "User";
        }
        if (elements.dashboardGreeting) {
            elements.dashboardGreeting.textContent = `Welcome back, ${firstName}`;
        }
        if (elements.dashboardRole) {
            elements.dashboardRole.textContent = role;
        }
        if (elements.dashboardSummary) {
            elements.dashboardSummary.textContent = `${role} session active. Your token is stored and ready to be sent as a Bearer authorization header.`;
        }
        if (elements.dashboardName) {
            elements.dashboardName.textContent = user.name || "--";
        }
        if (elements.dashboardEmail) {
            elements.dashboardEmail.textContent = user.email || "--";
        }
        if (elements.dashboardPhone) {
            elements.dashboardPhone.textContent = user.phone || "Not provided";
        }
        if (elements.sessionStatus) {
            elements.sessionStatus.textContent = "Active";
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

    async function handleCopyToken() {
        if (!state.token) {
            showToast("No token available to copy.", "error");
            return;
        }

        try {
            await navigator.clipboard.writeText(state.token);
            showToast("Token copied to clipboard.", "success");
        } catch (error) {
            showToast("Unable to copy token.", "error");
        }
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

    function setButtonLoading(button, isLoading, label) {
        if (!button) {
            return;
        }

        if (!button.dataset.defaultLabel) {
            button.dataset.defaultLabel = button.textContent || "";
        }

        button.disabled = isLoading;
        button.textContent = isLoading ? label : button.dataset.defaultLabel;
    }

    function showFormMessage(target, message, type) {
        if (!target) {
            return;
        }

        target.textContent = message;
        target.classList.remove("is-hidden", "is-error", "is-success");
        target.classList.add(type === "success" ? "is-success" : "is-error");
    }

    function clearFormMessage(target) {
        if (!target) {
            return;
        }

        target.textContent = "";
        target.classList.add("is-hidden");
        target.classList.remove("is-error", "is-success");
    }

    function showToast(message, type) {
        if (!elements.toastStack) {
            return;
        }

        const toast = document.createElement("div");
        toast.className = `toast ${type === "error" ? "toast-error" : "toast-success"}`;
        toast.textContent = message;
        elements.toastStack.appendChild(toast);

        window.setTimeout(() => {
            toast.remove();
        }, 3200);
    }

    async function apiRequest(url, options = {}) {
        const headers = {
            "Content-Type": "application/json",
            ...(state.token ? { Authorization: `Bearer ${state.token}` } : {}),
            ...(options.headers || {}),
        };

        const response = await fetch(url, {
            ...options,
            headers,
        });

        const payload = await response.json().catch(() => ({}));

        if (!response.ok) {
            throw new Error(payload.message || payload.error || `Request failed with status ${response.status}`);
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

    function formatRole(role) {
        if (!role) {
            return "User";
        }

        return String(role).charAt(0).toUpperCase() + String(role).slice(1);
    }
});
