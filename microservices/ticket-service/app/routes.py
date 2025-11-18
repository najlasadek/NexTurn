from flask import Blueprint, request, jsonify


def init_routes(ticket_model):
    bp = Blueprint("ticket_bp", __name__)

    @bp.route("/health", methods=["GET"])
    def health():
        return jsonify({"service": "ticket-service", "status": "ok"}), 200

    # Optional helper for testing ticket creation
    @bp.route("/tickets", methods=["POST"])
    def create_ticket():
        data = request.get_json() or {}
        queue_id = data.get("queue_id")
        user_id = data.get("user_id")

        if queue_id is None or user_id is None:
            return jsonify({"error": "queue_id and user_id required"}), 400

        ticket = ticket_model.create_ticket(int(queue_id), int(user_id))
        return jsonify(ticket), 201

    # GET /tickets/{ticketId}
    @bp.route("/tickets/<ticket_id>", methods=["GET"])
    def get_ticket(ticket_id):
        ticket = ticket_model.get_ticket_by_ticket_id(ticket_id)
        if not ticket:
            return jsonify({"error": "Ticket not found"}), 404
        return jsonify(ticket), 200

    # PUT /tickets/{ticketId}/alerts
    @bp.route("/tickets/<ticket_id>/alerts", methods=["PUT"])
    def update_alerts(ticket_id):
        data = request.get_json() or {}
        email = bool(data.get("alert_email", False))
        sms = bool(data.get("alert_sms", False))
        push = bool(data.get("alert_push", False))

        ticket = ticket_model.update_alerts(ticket_id, email, sms, push)
        if not ticket:
            return jsonify({"error": "Ticket not found"}), 404
        return jsonify(ticket), 200

    # GET /tickets/user/{userId}
    @bp.route("/tickets/user/<int:user_id>", methods=["GET"])
    def user_tickets(user_id):
        tickets = ticket_model.get_tickets_for_user(user_id)
        return jsonify({"tickets": tickets}), 200

    return bp
