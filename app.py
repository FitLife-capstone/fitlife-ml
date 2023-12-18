import os
import tensorflow as tf

from flask import Flask, request, jsonify, Response


app = Flask(__name__)

@app.route("/")
def hello_world():
    name = os.environ.get("NAME", "World")
    return "Hello {}!".format(name)

@app.route("/recommend-by-bodypart", methods=["POST"])
def recommend_by_bodypart():
    #TODO: Add response object from database, add user data in request body, filter by user equipment
    data = request.json
    body_part = data.get("body_part")

    if body_part:
        try:
            model = tf.saved_model.load('./model')
            _, titles = model([body_part])

            # Format the output as needed
            exercise_recommendations = titles[:10]
            exercise_recommendations = exercise_recommendations.numpy()
            exercise_recommendations = [item.decode('utf-8') for item in exercise_recommendations[0]]

            return jsonify({"error": False, "message": "SUCCESS", "data": exercise_recommendations}), 201

        except Exception as e:
            print(e)
            return jsonify({"error": True, "message": "INTERNAL_SERVER_ERROR", "data": []}), 400
    else:
        return jsonify({"error": True, "message": "INVALID_REQUEST_BODY", "data": []}), 500

if __name__ == '__main__':
    app.run(debug=True)

