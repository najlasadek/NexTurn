from flask import Blueprint, jsonify


def init_routes(analytics_model):
    bp = Blueprint("analytics_bp", __name__)

    @bp.route("/health", methods=["GET"])
    def health():
        return jsonify({"service": "analytics-service", "status": "ok"}), 200

    # GET /analytics/queue/{queueId}
    @bp.route("/analytics/queue/<int:queue_id>", methods=["GET"])
    def queue_analytics(queue_id):
        data = analytics_model.get_queue_analytics(queue_id)
        return jsonify(data), 200

    # GET /analytics/business/{businessId}
    @bp.route("/analytics/business/<int:business_id>", methods=["GET"])
    def business_analytics(business_id):
        data = analytics_model.get_business_analytics(business_id)
        return jsonify(data), 200

    # GET /analytics/wait-times
    @bp.route("/analytics/wait-times", methods=["GET"])
    def wait_times():
        data = analytics_model.get_wait_time_stats()
        return jsonify(data), 200

    return bp
