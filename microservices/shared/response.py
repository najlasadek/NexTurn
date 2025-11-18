"""
Shared response utilities for consistent API responses
"""
from flask import jsonify


def success_response(data=None, message=None, status_code=200):
    """Return a success response"""
    response = {
        'success': True,
        'data': data,
        'message': message
    }
    return jsonify(response), status_code


def error_response(message, status_code=400, errors=None):
    """Return an error response"""
    response = {
        'success': False,
        'message': message,
        'errors': errors
    }
    return jsonify(response), status_code


def validation_error(errors):
    """Return a validation error response"""
    return error_response(
        message='Validation failed',
        status_code=422,
        errors=errors
    )
