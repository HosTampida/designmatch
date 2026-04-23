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

    const cleanPhone = phone.toString().replace(/[\\s+-()]/g, '');

    const message = `Hola ${name}, vi tu perfil en DesignMatch 🚀\nEstoy interesado en trabajar contigo en: "${projectTitle}"\n¿Tienes disponibilidad?`;

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
    const projectForm = document.getElementById("projectForm");
    const registerForm = document.getElementById("registerForm");
    const loginForm = document.getElementById("loginForm");
    
    if (projectForm) projectForm.addEventListener("submit", handleProjectSubmit);
    if (registerForm) registerForm.addEventListener("submit", handleRegister);
    if (loginForm) loginForm.addEventListener("submit", handleLogin);
    
    const applyFiltersBtn = document.getElementById("applyFilters");
    const clearFiltersBtn = document.getElementById("clearFilters");
    const logoutBtn = document.getElementById("logoutButton");
    
    if (applyFiltersBtn) applyFiltersBtn.addEventListener("submit", applyFilters);
    if (clearFiltersBtn) clearFiltersBtn.addEventListener("click", clearFilters);
    if (logoutBtn) logoutBtn.addEventListener("click", handleLogout);

    // Dialog closes
    ['closeProfileDialog', 'closeInfoDialog', 'closeAccessDialog'].forEach(id => {
        const el = document.getElementById(id);
        if (el) el.addEventListener("click", () => closeDialog(id.replace('close', '')));
    });

    // Data actions
    document.querySelectorAll("[data-open-access]").forEach(btn => {
        btn.addEventListener("click", () => openAccessDialog(btn.dataset.openAccess));
    });

    document.querySelectorAll("[data-action]").forEach(btn => {
        btn.addEventListener("click", () => handleAction(btn.dataset.action));
    });

    // Auth toggle
    document.querySelectorAll("[data-toggle]").forEach(btn => {
        btn.addEventListener("click", (e) => {
            e.preventDefault();
            openAccessDialog(e.target.dataset.toggle);
        });
    });

    // Role fields
    const roleSelect = document.getElementById("roleSelect");
    if (roleSelect) roleSelect.addEventListener("change", toggleRoleFields);

    // Dialog backdrop close
    document.querySelectorAll("dialog").forEach(dialog => {
        dialog.addEventListener("click", (event) => {
            const rect = dialog.getBoundingClientRect();
            const isInDialog = event.clientX >= rect.left && event.clientX <= rect.right && event.clientY >= rect.top && event.clientY <= rect.bottom;
            if (!isInDialog) dialog.close();
        });
    });
}

// ... (keep all other functions: initHeroCarousel, toggleRoleFields, loadRegSkills, etc. - truncated for brevity)

async function handleRegister(event) {
    event.preventDefault();
    const form = event.target;
    const submitBtn = form.querySelector('button[type="submit"]');
    const originalText = submitBtn.textContent;
    
    showLoading(submitBtn, "Creando...");
    
    try {
        const formData = new FormData(form);
        const payload = {
            name: formData.get("name").trim(),
            email: formData.get("email").trim().toLowerCase(),
            phone: formData.get("phone")?.trim() || null,
            password: formData.get("password").trim(),  // Real password from form!
            role: formData.get("role"),
        };
        
        if (payload.role === "designer") {
            payload.bio = formData.get("bio")?.trim() || "";
            payload.portfolio_url = formData.get("portfolio_url")?.trim() || "";
            payload.skills = collectCheckedValues("reg_skill_ids");
            payload.price_min = 100;
            payload.price_max = 500;
        } else {
            payload.project_description = formData.get("project_description")?.trim() || "";
        }

        const response = await api("/api/auth/register", {
            method: "POST",
            body: JSON.stringify(payload),
        });

        setCurrentUser(response.data.user);
        closeDialog("accessDialog");
        showSuccess("¡Cuenta creada! Bienvenido a DesignMatch.");
        await loadStats();
    } catch (error) {
        showError(form, "register-error", error.message || "Error al crear cuenta");
    } finally {
        hideLoading(submitBtn, originalText);
    }
}

async function handleLogin(event) {
    event.preventDefault();
    const form = event.target;
    const submitBtn = form.querySelector('button[type="submit"]');
    const originalText = submitBtn.textContent;
    
    showLoading(submitBtn, "Iniciando...");
    
    try {
        const formData = new FormData(form);
        const payload = {
            email: formData.get("email").trim().toLowerCase(),
            password: formData.get("password").trim(),
        };

        const response = await api("/api/auth/login", {
            method: "POST",
            body: JSON.stringify(payload),
        });

        localStorage.setItem("token", response.data.token);
        setCurrentUser(response.data.user);
        closeDialog("accessDialog");
        showSuccess(`¡Hola ${response.data.user.name}!`);
    } catch (error) {
        showError(form, "login-error", error.message || "Credenciales inválidas");
    } finally {
        hideLoading(submitBtn, originalText);
    }
}

function showLoading(btn, text) {
    btn.disabled = true;
    btn.innerHTML = `<span>${text}</span> <span class="spinner"></span>`;
}

function hideLoading(btn, text) {
    btn.disabled = false;
    btn.innerHTML = text;
}

function showError(form, errorId, message) {
    const errorEl = form.querySelector(`[data-error="${errorId}"]`) || document.createElement("div");
    errorEl.textContent = message;
    errorEl.className = "error-message";
    form.insertBefore(errorEl, form.firstElementChild);
}

function showSuccess(message) {
    // Simple toast for success
    const toast = document.createElement("div");
    toast.textContent = message;
    toast.className = "toast-success";
    document.body.appendChild(toast);
    setTimeout(() => toast.remove(), 3000);
}

// Fix api function with better error handling
async function api(url, options = {}) {
    try {
        const token = localStorage.getItem("token");
        const headers = {
            "Content-Type": "application/json",
            ...(token ? {"Authorization": `Bearer ${token}`} : {}),
            ...options.headers,
        };

        const response = await fetch(url, {
            ...options,
            headers,
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.message || `HTTP ${response.status}`);
        }

        return await response.json();
    } catch (error) {
        console.error("[API]", error);
        throw error;
    }
}

// Keep all other functions unchanged...


