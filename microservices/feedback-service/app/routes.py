from flask import Blueprint, request
from shared.database import db
from shared.response import success, fail
from shared.auth_middleware import token_required
from app.models import Feedback

feedback_bp = Blueprint("feedback", __name__)

# POST /feedback
@feedback_bp.route("/", methods=["POST"])
@token_required
def submit_feedback(current_user):
    data = request.get_json()

    required = ["user_id", "business_id", "rating"]
    if not all(k in data for k in required):
        return fail("Missing fields: user_id, business_id, rating", 400)

    fb = Feedback(
        user_id=data["user_id"],
        business_id=data["business_id"],
        rating=data["rating"],
        comment=data.get("comment", "")
    )

    db.session.add(fb)
    db.session.commit()
    return success(fb.to_dict(), 201)


# GET /feedback/business/<businessId>
@feedback_bp.route("/business/<int:business_id>", methods=["GET"])
def get_business_feedback(business_id):
    feedback_list = Feedback.query.filter_by(business_id=business_id).all()
    return success([f.to_dict() for f in feedback_list])


# GET /feedback/<id>
@feedback_bp.route("/<int:feedback_id>", methods=["GET"])
def get_feedback(feedback_id):
    fb = Feedback.query.get(feedback_id)
    if not fb:
        return fail("Feedback not found", 404)
    return success(fb.to_dict())


# GET /feedback/business/<id>/average
@feedback_bp.route("/business/<int:business_id>/average", methods=["GET"])
def get_average_rating(business_id):
    from sqlalchemy import func
    avg = db.session.query(func.avg(Feedback.rating)).filter_by(business_id=business_id).scalar()
    count = Feedback.query.filter_by(business_id=business_id).count()

    return success({
        "business_id": business_id,
        "average_rating": float(avg) if avg else None,
        "count": count
    })
