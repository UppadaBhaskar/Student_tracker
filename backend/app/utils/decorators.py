from functools import wraps

from flask_jwt_extended import get_jwt, verify_jwt_in_request

from app.exceptions import ForbiddenException, UnauthorizedException


def role_required(*roles: str):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            if claims.get("role") not in roles:
                raise ForbiddenException("Insufficient permissions")
            return fn(*args, **kwargs)

        return wrapper

    return decorator


def get_jwt_claims() -> dict:
    verify_jwt_in_request()
    return get_jwt()
