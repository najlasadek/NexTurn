/**
 * Ticket-related JavaScript functions
 * Uses api-config.js utilities
 */

let currentTicket = null;

/**
 * Load ticket information
 * @param {string|null} ticketId - Optional ticket ID from URL parameter
 */
async function loadTicket(ticketId = null) {
  requireAuth();
  const token = getToken();

  try {
    // Try to get ticket from URL parameter first
    if (ticketId) {
      try {
        const data = await apiRequest(API.ticket.detail(ticketId), {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });

        if (data.success && data.data.ticket) {
          currentTicket = data.data.ticket;
          displayTicket(currentTicket);
          return;
        }
      } catch (error) {
        console.error("Error loading ticket by ID:", error);
      }
    }

    // If no ticket_id in URL, try to get active ticket
    const activeData = await apiRequest(API.ticket.myActive, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    if (activeData.success && activeData.data.ticket) {
      currentTicket = activeData.data.ticket;
      displayTicket(currentTicket);
    } else {
      document.getElementById("ticketInfo").innerHTML = `
        <div class="text-center py-8">
          <p class="text-gray-500 mb-4">No active ticket found.</p>
          <a href="/businesses" class="text-primary hover:underline">Browse Businesses</a>
        </div>
      `;
    }
  } catch (error) {
    console.error("Error loading ticket:", error);
    document.getElementById("ticketInfo").innerHTML = `
      <div class="text-center py-8">
        <p class="text-red-500">Error loading ticket. Please try again.</p>
      </div>
    `;
  }
}

/**
 * Display ticket information
 * @param {object} ticket - Ticket object
 */
function displayTicket(ticket) {
  const ticketInfo = document.getElementById("ticketInfo");
  const eta = ticket.eta !== undefined ? ticket.eta : 0;
  ticketInfo.innerHTML = `
    <p class="text-gray-600">Ticket ID: <span class="font-medium">${
      ticket.ticket_id || ticket.id
    }</span></p>
    <p class="text-gray-600">Position: <span class="font-medium">#${
      ticket.position
    }</span></p>
    <p class="text-gray-600">Estimated Wait Time: <span class="font-medium">${eta} minutes</span></p>
  `;

  // Show alert settings
  const alertSettings = document.getElementById("alertSettings");
  if (alertSettings) {
    alertSettings.classList.remove("hidden");
  }
}

/**
 * Leave the queue (cancel ticket)
 */
async function leaveQueue() {
  if (!confirm("Are you sure you want to leave the queue?")) {
    return;
  }

  if (!currentTicket) {
    showToast("No active ticket found", "error");
    return;
  }

  requireAuth();

  try {
    const data = await apiRequest(API.ticket.cancel(currentTicket.ticket_id), {
      method: "POST",
      headers: {
        Authorization: `Bearer ${getToken()}`,
      },
    });

    if (data.success) {
      showToast("Successfully left the queue", "success");
      window.location.href = "/home";
    } else {
      showToast(
        data.message || "Failed to leave queue. Please try again.",
        "error"
      );
    }
  } catch (error) {
    console.error("Error leaving queue:", error);
    showToast(
      "An error occurred while leaving the queue. Please try again.",
      "error"
    );
  }
}

/**
 * Get ticket ID from URL query parameter
 */
function getTicketIdFromURL() {
  const urlParams = new URLSearchParams(window.location.search);
  return urlParams.get("ticket_id");
}
