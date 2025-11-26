/**
 * API Configuration for NexTurn Frontend
 * This file provides utility functions for making API calls to the microservices
 */

// API Base URL - empty string means same origin (frontend gateway)
const API_BASE_URL = "";

// API Endpoints
const API = {
  // Auth endpoints
  auth: {
    signup: "/auth/signup",
    login: "/auth/login",
    logout: "/auth/logout",
    verify: "/auth/verify",
    profile: "/auth/profile",
  },
  // Business endpoints
  business: {
    create: "/api/businesses",
    list: "/api/businesses",
    detail: (id) => `/api/businesses/${id}`,
    myBusinesses: "/api/businesses/my-businesses",
    stats: (id) => `/api/businesses/${id}/stats`,
  },
  // Queue endpoints
  queue: {
    create: "/api/queues",
    detail: (id) => `/api/queues/${id}`,
    businessQueues: (businessId) => `/api/queues/business/${businessId}`,
    join: (id) => `/api/queues/${id}/join`,
    serveNext: (id) => `/api/queues/${id}/serve-next`,
  },
  // Ticket endpoints
  ticket: {
    detail: (id) => `/api/tickets/${id}`,
    cancel: (id) => `/api/tickets/${id}/cancel`,
    myActive: "/api/tickets/my-active",
    myHistory: "/api/tickets/my-history",
  },
  // Feedback endpoints
  feedback: {
    businessFeedback: (businessId) => `/api/feedback/business/${businessId}`,
    businessAverage: (businessId) =>
      `/api/feedback/business/${businessId}/average`,
  },
};

/**
 * Make an API request
 * @param {string} url - The API endpoint URL
 * @param {object} options - Fetch options (method, body, headers, etc.)
 * @returns {Promise} - Response data
 */
async function apiRequest(url, options = {}) {
  const defaultOptions = {
    headers: {
      "Content-Type": "application/json",
    },
  };

  // Extract body if present (needs special handling)
  const { body, ...restOptions } = options;

  const config = {
    ...defaultOptions,
    ...restOptions,
    headers: {
      ...defaultOptions.headers,
      ...restOptions.headers,
    },
  };

  // Add body if provided (for POST, PUT, etc.)
  if (body) {
    config.body = typeof body === "string" ? body : JSON.stringify(body);
  }

  try {
    const response = await fetch(`${API_BASE_URL}${url}`, config);

    // Handle empty responses
    const contentType = response.headers.get("content-type");
    let data;
    if (contentType && contentType.includes("application/json")) {
      const text = await response.text();
      data = text ? JSON.parse(text) : {};
    } else {
      const text = await response.text();
      data = text ? { message: text } : {};
    }

    if (!response.ok) {
      throw new Error(data.message || data.error || "Request failed");
    }

    return data;
  } catch (error) {
    console.error("API Request Error:", error);
    throw error;
  }
}

/**
 * Show toast notification
 * @param {string} message - Message to display
 * @param {string} type - Type of notification (success, error, info)
 */
function showToast(message, type = "info") {
  // Create toast element
  const toast = document.createElement("div");
  toast.className = `fixed top-4 right-4 px-6 py-3 rounded-lg shadow-lg text-white z-50 animate-slide-in`;

  const colors = {
    success: "bg-green-500",
    error: "bg-red-500",
    info: "bg-blue-500",
  };

  toast.classList.add(colors[type] || colors.info);
  toast.textContent = message;

  document.body.appendChild(toast);

  // Remove after 3 seconds
  setTimeout(() => {
    toast.style.opacity = "0";
    setTimeout(() => toast.remove(), 300);
  }, 3000);
}

/**
 * Get stored token from localStorage
 * @returns {string|null} - JWT token or null
 */
function getToken() {
  return localStorage.getItem("token");
}

/**
 * Store token in localStorage
 * @param {string} token - JWT token
 */
function setToken(token) {
  localStorage.setItem("token", token);
}

/**
 * Remove token from localStorage
 */
function removeToken() {
  localStorage.removeItem("token");
  localStorage.removeItem("user");
}

/**
 * Get stored user from localStorage
 * @returns {object|null} - User object or null
 */
function getUser() {
  const userStr = localStorage.getItem("user");
  return userStr ? JSON.parse(userStr) : null;
}

/**
 * Store user in localStorage
 * @param {object} user - User object
 */
function setUser(user) {
  localStorage.setItem("user", JSON.stringify(user));
}

/**
 * Check if user is authenticated
 * @returns {boolean}
 */
function isAuthenticated() {
  return !!getToken();
}

/**
 * Redirect to login if not authenticated
 */
function requireAuth() {
  if (!isAuthenticated()) {
    window.location.href = "/login";
  }
}

/**
 * Handle logout
 */
async function handleLogout() {
  try {
    await apiRequest("/auth/logout", { method: "POST" });
    removeToken();
    window.location.href = "/login";
  } catch (error) {
    console.error("Logout error:", error);
    removeToken();
    window.location.href = "/login";
  }
}

// Add CSS for toast animations
const style = document.createElement("style");
style.textContent = `
    @keyframes slide-in {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    .animate-slide-in {
        animation: slide-in 0.3s ease-out;
    }
`;
document.head.appendChild(style);
