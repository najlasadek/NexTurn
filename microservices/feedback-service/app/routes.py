from flask import Blueprint, request, jsonify

def init_routes(feedback_model):
    """
    Creates a Blueprint with all feedback-service routes wired to the Feedback model.
    """
    feedback_bp = Blueprint("feedback_bp", __name__)

    @feedback_bp.route("/health", methods=["GET"])
    def health():
        return jsonify({"status": "ok", "service": "feedback-service"}), 200

    # POST /feedback  – submit new feedback
    @feedback_bp.route("/feedback", methods=["POST"])
    def submit_feedback():
        data = request.get_json() or {}

        user_id = data.get("user_id")
        business_id = data.get("business_id")
        rating = data.get("rating")
        comment = data.get("comment", "")

        if user_id is None or business_id is None or rating is None:
            return jsonify({"error": "user_id, business_id, and rating are required"}), 400

        fb = feedback_model.create_feedback(
            user_id=int(user_id),
            business_id=int(business_id),
            rating=int(rating),
            comment=comment,
        )

        return jsonify(fb), 201

    # GET /feedback/business/<businessId> – list feedback for a business
    @feedback_bp.route("/feedback/business/<int:business_id>", methods=["GET"])
    def list_business_feedback(business_id):
        feedback_list = feedback_model.get_feedback_for_business(business_id)
        return jsonify({"feedback": feedback_list}), 200

    # GET /feedback/<id> – get one feedback
    @feedback_bp.route("/feedback/<int:feedback_id>", methods=["GET"])
    def get_feedback(feedback_id):
        fb = feedback_model.get_feedback_by_id(feedback_id)
        if not fb:
            return jsonify({"error": "Feedback not found"}), 404
        return jsonify(fb), 200

    # GET /feedback/business/<id>/average – average rating
    @feedback_bp.route("/feedback/business/<int:business_id>/average", methods=["GET"])
    def average_feedback(business_id):
        stats = feedback_model.get_average_rating_for_business(business_id)
        return jsonify(stats), 200

    return feedback_bp
