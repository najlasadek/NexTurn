/**
 * Queue-related JavaScript functions
 * Uses api-config.js utilities
 */

/**
 * Join a queue
 * @param {number} queueId - The ID of the queue to join
 */
async function joinQueue(queueId) {
  requireAuth();
  const token = getToken();

  // Check if user already has an active ticket
  try {
    const activeData = await apiRequest(API.ticket.myActive, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    if (activeData.success && activeData.data.ticket) {
      const confirmLeave = confirm(
        "You already have an active ticket. Would you like to leave your current queue and join this one?"
      );
      if (!confirmLeave) {
        // Redirect to existing ticket
        window.location.href = `/ticket?ticket_id=${activeData.data.ticket.ticket_id}`;
        return;
      }
      // Cancel existing ticket first
      try {
        await apiRequest(API.ticket.cancel(activeData.data.ticket.ticket_id), {
          method: "POST",
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });
      } catch (error) {
        console.error("Error canceling existing ticket:", error);
      }
    }
  } catch (error) {
    console.error("Error checking active ticket:", error);
  }

  try {
    const data = await apiRequest(API.queue.join(queueId), {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    if (data.success) {
      showToast("Successfully joined the queue!", "success");
      // Redirect to ticket page
      window.location.href = `/ticket?ticket_id=${data.data.ticket_id}`;
    } else {
      // Show the actual error message from the API
      const errorMsg =
        data.message || data.error || "Failed to join queue. Please try again.";
      showToast(errorMsg, "error");
      console.error("Join queue error:", data);
    }
  } catch (error) {
    console.error("Error joining queue:", error);
    showToast(
      "An error occurred while joining the queue. Please try again.",
      "error"
    );
  }
}
