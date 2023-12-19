from flask import request, jsonify
import jwt
import os

def auth_middleware(func):
    def wrapper(*args, **kwargs):
        token = request.headers.get('Authorization')

        if not token:
            return jsonify({"error": "Unauthorized: Token is missing"}), 401

        try:
            try:
                # Assuming the token prefix is 'Bearer' as in: 'Bearer your_jwt_token'
                decoded = jwt.decode(token.split(" ")[1], os.environ.get('JWT_SECRET_USER'), algorithms=["HS256"], options={'verify_signature': False})
                request.user = {
                    'userId': decoded['userId'],
                    'role': 'user'
                }
            except jwt.ExpiredSignatureError as userError:
                # Handling expired tokens
                decoded = jwt.decode(token.split(" ")[1], os.environ.get('JWT_SECRET_ADMIN'), algorithms=["HS256"], options={'verify_signature': False})
                request.user = {
                    'userId': decoded['userId'],
                    'role': 'admin'
                }

            return func(*args, **kwargs)

        except jwt.PyJWTError as error:
            # Catch all other JWT errors
            print(f"Token verification error: {error}")
            return jsonify({"error": "Unauthorized: Invalid token"}), 401

    wrapper.__name__ = func.__name__
    return wrapper
