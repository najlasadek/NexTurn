from flask import Blueprint, request, jsonify


def init_routes(notif_model):
    bp = Blueprint("notification_bp", __name__)

    @bp.route("/health", methods=["GET"])
    def health():
        return jsonify({"service": "notification-service", "status": "ok"}), 200

    # POST /notifications/send
    @bp.route("/notifications/send", methods=["POST"])
    def send_notification():
        data = request.get_json() or {}
        user_id = data.get("user_id")
        channel = data.get("channel", "email")
        message = data.get("message", "")

        if user_id is None or not message:
            return jsonify({"error": "user_id and message are required"}), 400

        notif = notif_model.send_notification(int(user_id), channel, message)
        return jsonify(notif), 201

    # POST /notifications/schedule
    @bp.route("/notifications/schedule", methods=["POST"])
    def schedule_notification():
        data = request.get_json() or {}
        user_id = data.get("user_id")
        channel = data.get("channel", "email")
        message = data.get("message", "")
        scheduled_for = data.get("scheduled_for")  # ISO string expected

        if user_id is None or not message or not scheduled_for:
            return jsonify({"error": "user_id, message, scheduled_for required"}), 400

        notif = notif_model.schedule_notification(int(user_id), channel, message, scheduled_for)
        return jsonify(notif), 201

    # GET /notifications/user/{userId}
    @bp.route("/notifications/user/<int:user_id>", methods=["GET"])
    def user_notifications(user_id):
        notifs = notif_model.get_notifications_for_user(user_id)
        return jsonify({"notifications": notifs}), 200

    return bp
