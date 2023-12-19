import os
import tensorflow as tf

from flask import Flask, request, jsonify
from middleware import auth_middleware
from dotenv import load_dotenv


app = Flask(__name__)

@app.route("/")
def hello_world():
    name = os.environ.get("NAME", "World")
    return "Hello {}!".format(name)

@app.route("/recommend-by-bodypart", methods=["POST"])
@auth_middleware
def recommend_by_bodypart():
    data = request.json
    body_part = data.get("body_part")
    user_id = request.user['userId']
    role = request.user['role']

    if role == 'admin':
        return jsonify({"error": True, "message": "INVALID_REQUEST_BODY", "data": []}), 500
    
    #TODO: get user data from database using user_id

    if body_part:
        try:
            model = tf.saved_model.load('./model')
            _, titles = model([body_part])

            #TODO: filter by user equipment
            exercise_recommendations = titles[:10]
            exercise_recommendations = exercise_recommendations.numpy()
            exercise_recommendations = [item.decode('utf-8') for item in exercise_recommendations[0]]

            #TODO: get exercise details from database, then add to response object

            return jsonify({"error": False, "message": "SUCCESS", "data": exercise_recommendations}), 200

        except Exception as e:
            print(e)
            return jsonify({"error": True, "message": "INTERNAL_SERVER_ERROR", "data": []}), 400
    else:
        return jsonify({"error": True, "message": "INVALID_REQUEST_BODY", "data": []}), 500

if __name__ == '__main__':
    load_dotenv('.env', override=True)
    app.run(debug=True)

