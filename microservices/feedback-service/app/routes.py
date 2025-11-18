from flask import Blueprint, request, jsonify

def init_routes(feedback_model):
    feedback_bp = Blueprint("feedback_bp", __name__)

    @feedback_bp.route("/health", methods=["GET"])
    def health():
        return jsonify({"service": "feedback-service", "status": "ok"}), 200

    @feedback_bp.route("/feedback", methods=["POST"])
    def submit_feedback():
        data = request.get_json() or {}

        user_id = data.get("user_id")
        business_id = data.get("business_id")
        rating = data.get("rating")
        comment = data.get("comment", "")

        if not all([user_id, business_id, rating]):
            return jsonify({"error": "user_id, business_id, and rating required"}), 400

        fb = feedback_model.create_feedback(user_id, business_id, rating, comment)
        return jsonify(fb), 201

    @feedback_bp.route("/feedback/business/<int:business_id>", methods=["GET"])
    def business_feedback(business_id):
        feedback_list = feedback_model.get_feedback_for_business(business_id)
        return jsonify({"feedback": feedback_list}), 200

    @feedback_bp.route("/feedback/business/<int:business_id>/average", methods=["GET"])
    def average_rating(business_id):
        stats = feedback_model.get_average_rating_for_business(business_id)
        return jsonify(stats), 200

    return feedback_bp
