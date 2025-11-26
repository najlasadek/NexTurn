/**
 * Business-related JavaScript functions
 * Uses api-config.js utilities
 */

// Business Dashboard Functions
async function loadMyBusinesses() {
  requireAuth();
  const loadingMsg = document.getElementById("loadingMsg");
  const businessesContainer = document.getElementById("businessesContainer");
  const noBusinessesMsg = document.getElementById("noBusinessesMsg");

  try {
    const data = await apiRequest(API.business.myBusinesses, {
      headers: {
        Authorization: `Bearer ${getToken()}`,
      },
    });

    loadingMsg.classList.add("hidden");

    if (data.success && data.data.businesses && data.data.businesses.length > 0) {
      businessesContainer.classList.remove("hidden");
      renderMyBusinesses(data.data.businesses);
    } else {
      noBusinessesMsg.classList.remove("hidden");
    }
  } catch (error) {
    loadingMsg.classList.add("hidden");
    noBusinessesMsg.classList.remove("hidden");
    console.error("Error loading businesses:", error);
    showToast("Error loading businesses. Please try again.", "error");
  }
}

async function renderMyBusinesses(businesses) {
  const container = document.getElementById("businessesContainer");
  container.innerHTML = "";

  for (const business of businesses) {
    // Fetch queues for this business
    try {
      const queuesData = await apiRequest(API.queue.businessQueues(business.id));
      const queues = queuesData.success ? queuesData.data.queues : [];

      const businessCard = document.createElement("div");
      businessCard.className =
        "bg-white rounded-xl shadow-md p-6 hover:shadow-lg transition";

      businessCard.innerHTML = `
        <h2 class="text-xl font-bold text-gray-900 mb-2">${business.name}</h2>
        <p class="text-gray-600 mb-1">${business.category}</p>
        <p class="text-sm text-gray-500 mb-4">${business.address}</p>

        <div class="border-t pt-4 mt-4">
          <div class="flex justify-between items-center mb-3">
            <h3 class="text-sm font-semibold text-gray-700">Queues:</h3>
            <button onclick="openCreateQueueModal(${business.id})" 
                    class="px-3 py-1 text-xs bg-primary text-white rounded-lg hover:bg-accent1 transition">
              + Create Queue
            </button>
          </div>
          <div id="queues-${business.id}" class="space-y-2 mb-4"></div>
          <a href="/business/${business.id}/feedback-list"
             class="block w-full text-center px-4 py-2 bg-accent3 text-white rounded-lg hover:bg-primary transition">
            View Customer Feedback
          </a>
        </div>
      `;

      container.appendChild(businessCard);

      // Render queues
      const queuesDiv = document.getElementById(`queues-${business.id}`);
      if (queues.length > 0) {
        queues.forEach((queue) => {
          const queueLink = document.createElement("a");
          queueLink.href = `/business/${business.id}/queue/${queue.id}`;
          queueLink.className =
            "block px-4 py-2 bg-gray-100 hover:bg-accent2 hover:text-white rounded-lg transition";
          queueLink.innerHTML = `
            ${queue.name}
            <span class="text-xs">${queue.is_active ? "(Active)" : "(Inactive)"}</span>
          `;
          queuesDiv.appendChild(queueLink);
        });
      } else {
        queuesDiv.innerHTML =
          '<p class="text-sm text-gray-500 italic">No queues available</p>';
      }
    } catch (error) {
      console.error(`Error loading queues for business ${business.id}:`, error);
    }
  }
}

// Business List Functions
async function loadAllBusinesses() {
  const container = document.getElementById("businesses-container");

  try {
    const result = await apiRequest(API.business.list);

    if (result.success && result.data.businesses && result.data.businesses.length > 0) {
      const businesses = result.data.businesses;
      container.innerHTML = `
        <div class="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          ${businesses
            .map(
              (business) => `
            <div class="bg-white rounded-xl shadow-md p-6 hover:shadow-lg transition">
              <div class="mb-4">
                <span class="inline-block px-3 py-1 text-xs font-semibold rounded-full bg-accent2 text-white">
                  ${business.category || "General"}
                </span>
              </div>
              <h2 class="text-xl font-bold text-gray-900 mb-2">${business.name}</h2>
              <p class="text-gray-600 mb-2">${
                business.description || "No description available"
              }</p>
              <p class="text-sm text-gray-500 mb-4">${business.address || ""}</p>

              <div class="border-t pt-4 mt-4">
                <a href="/business/${business.id}/queues"
                   class="block w-full text-center px-4 py-2 bg-primary text-white rounded-lg hover:bg-accent1 transition">
                  View Queues
                </a>
              </div>
            </div>
          `
            )
            .join("")}
        </div>
      `;
    } else {
      container.innerHTML = `
        <div class="text-center py-12">
          <p class="text-gray-500 text-lg">No businesses available yet.</p>
        </div>
      `;
    }
  } catch (error) {
    console.error("Error loading businesses:", error);
    container.innerHTML = `
      <div class="text-center py-12">
        <p class="text-red-500 text-lg">Error loading businesses. Please try again later.</p>
      </div>
    `;
  }
}

// Business Queues Page Functions
async function loadBusinessAndQueues(businessId) {
  try {
    // Load business info
    const businessData = await apiRequest(API.business.detail(businessId));

    if (businessData.success && businessData.data.business) {
      const business = businessData.data.business;
      const businessInfo = document.getElementById("businessInfo");
      businessInfo.innerHTML = `
        <div class="flex items-start justify-between">
          <div>
            <span class="inline-block px-3 py-1 text-xs font-semibold rounded-full bg-accent2 text-white mb-3">
              ${business.category || "General"}
            </span>
            <h1 class="text-3xl font-bold text-gray-900 mb-2">${business.name}</h1>
            <p class="text-gray-600 mb-2">${
              business.description || "No description available"
            }</p>
            <p class="text-sm text-gray-500">${business.address || ""}</p>
          </div>
          <a href="/feedback/${business.id}"
             class="px-4 py-2 border-2 border-accent3 text-accent3 rounded-lg hover:bg-accent3 hover:text-white transition">
            Leave Feedback
          </a>
        </div>
      `;
    }

    // Load queues
    const queuesData = await apiRequest(API.queue.businessQueues(businessId));
    const queuesContainer = document.getElementById("queuesContainer");

    if (queuesData.success && queuesData.data.queues && queuesData.data.queues.length > 0) {
      const queues = queuesData.data.queues;
      queuesContainer.innerHTML = queues
        .map((queue) => {
          const estimatedWait = queue.size * queue.avg_service_time;
          return `
            <div class="bg-white rounded-xl shadow-md p-6 hover:shadow-lg transition mb-6">
              <div class="flex items-center justify-between">
                <div class="flex-1">
                  <h3 class="text-xl font-bold text-gray-900 mb-2">${queue.name}</h3>
                  <div class="space-y-1 text-sm text-gray-600">
                    <p>Current queue size: <span class="font-semibold text-primary">${
                      queue.size || 0
                    } people</span></p>
                    <p>Average service time: <span class="font-semibold">${
                      queue.avg_service_time
                    } minutes</span></p>
                    <p>Estimated wait time: <span class="font-semibold text-accent2">~${estimatedWait} minutes</span></p>
                  </div>
                </div>
                <div class="ml-6">
                  <button onclick="joinQueue(${queue.id})"
                          class="px-6 py-3 bg-primary text-white rounded-lg hover:bg-accent1 transition">
                    Join Queue
                  </button>
                </div>
              </div>
            </div>
          `;
        })
        .join("");
    } else {
      queuesContainer.innerHTML = `
        <div class="text-center py-12 bg-white rounded-xl shadow-md">
          <p class="text-gray-500 text-lg">No active queues available at this business.</p>
        </div>
      `;
    }
  } catch (error) {
    console.error("Error loading business and queues:", error);
    document.getElementById("businessInfo").innerHTML = `
      <div class="text-center py-12">
        <p class="text-red-500 text-lg">Error loading business information. Please try again later.</p>
      </div>
    `;
    document.getElementById("queuesContainer").innerHTML = `
      <div class="text-center py-12 bg-white rounded-xl shadow-md">
        <p class="text-red-500 text-lg">Error loading queues. Please try again later.</p>
      </div>
    `;
  }
}

// Create Queue Modal Functions
let currentBusinessId = null;

function openCreateQueueModal(businessId) {
  currentBusinessId = businessId;
  document.getElementById("createQueueModal").classList.remove("hidden");
}

function closeCreateQueueModal() {
  document.getElementById("createQueueModal").classList.add("hidden");
  document.getElementById("queueForm").reset();
  currentBusinessId = null;
}

async function createQueue(event) {
  event.preventDefault();

  requireAuth();

  const form = event.target;
  const formData = new FormData(form);
  const queueName = formData.get("queueName");
  const avgServiceTime = parseInt(formData.get("avgServiceTime")) || 5;

  if (!queueName || queueName.trim() === "") {
    showToast("Please enter a queue name", "error");
    return;
  }

  try {
    const data = await apiRequest(API.queue.create, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${getToken()}`,
      },
      body: {
        business_id: currentBusinessId,
        name: queueName.trim(),
        avg_service_time: avgServiceTime,
      },
    });

    if (data.success) {
      closeCreateQueueModal();
      showToast("Queue created successfully!", "success");
      // Reload businesses to show the new queue
      if (typeof loadMyBusinesses === "function") {
        loadMyBusinesses();
      }
    } else {
      showToast(data.message || "Failed to create queue. Please try again.", "error");
    }
  } catch (error) {
    console.error("Error creating queue:", error);
    showToast("An error occurred while creating the queue. Please try again.", "error");
  }
}

// Helper function to get business ID from URL
function getBusinessIdFromURL() {
  const pathParts = window.location.pathname.split("/");
  return pathParts[pathParts.indexOf("business") + 1];
}

