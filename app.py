import os
import tensorflow as tf

from flask import Flask, request, jsonify
from middleware import auth_middleware
from db import get_connection
from dotenv import load_dotenv
import psycopg2 as pg


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
    
    conn = get_connection()
    cur = conn.cursor()
    query = f"SELECT * FROM users WHERE user_id = {user_id}"
    cur.execute(query)
    result = cur.fetchall()
    if len(result) == 0:
        return jsonify({"error": True, "message": "INVALID_REQUEST_BODY", "data": []}), 500
    column_names = [col[0].lower() for col in cur.description]
    user_data = dict(zip(column_names, result[0]))

    if body_part:
        try:
            model = tf.saved_model.load('./model')
            _, name = model([body_part])

            name = name.numpy()
            name = [item.decode('utf-8') for item in name[0]]
            exercise_recommendations = []
            while len(exercise_recommendations) < 10:
                for i in range(len(name)):
                    query = f"SELECT * FROM exercise WHERE exercise_name = '{name[i]}'"
                    cur.execute(query)
                    result = cur.fetchall()
                    if len(result) == 0:
                        continue
                    column_names = [col[0].lower() for col in cur.description]
                    exercise_data = dict(zip(column_names, result[0]))
                    have_equipment = True
                    for equipment in exercise_data['equipments']:
                        if equipment not in user_data['equipments']:
                            have_equipment = False
                            break
                    if have_equipment:
                        exercise_recommendations.append(exercise_data)

            return jsonify({"error": False, "message": "SUCCESS", "data": exercise_recommendations}), 200

        except Exception as e:
            print(e)
            return jsonify({"error": True, "message": "INTERNAL_SERVER_ERROR", "data": []}), 400
    else:
        return jsonify({"error": True, "message": "INVALID_REQUEST_BODY", "data": []}), 500
    
@app.route("/recommend-all", methods=["GET"])
@auth_middleware
def recommend_all():
    list_bodypart = ['Glutes', 'Shoulders', 'Chest', 'Middle Back', 'Lower Back', 'Calves', 'Abductors', 
                 'Forearms', 'Neck', 'Quadriceps', 'Adductors', 'Abdominals', 'Biceps', 'Triceps', 'Hamstrings',  'Traps', 'Lats']
    user_id = request.user['userId']
    role = request.user['role']

    if role == 'admin':
        return jsonify({"error": True, "message": "INVALID_REQUEST_BODY", "data": []}), 500
    
    conn = get_connection()
    cur = conn.cursor()
    query = f"SELECT * FROM users WHERE user_id = {user_id}"
    cur.execute(query)
    result = cur.fetchall()
    if len(result) == 0:
        return jsonify({"error": True, "message": "INVALID_REQUEST_BODY", "data": []}), 500
    column_names = [col[0].lower() for col in cur.description]
    user_data = dict(zip(column_names, result[0]))

    model = tf.saved_model.load('./model')
    exercise_recommendations = []
    for bodypart in list_bodypart:
        try:
            _, name = model([bodypart])

            name = name.numpy()
            name = [item.decode('utf-8') for item in name[0]]
            for i in range(len(name)):
                query = f"SELECT * FROM exercise WHERE exercise_name = '{name[i]}'"
                cur.execute(query)
                result = cur.fetchall()
                if len(result) == 0:
                    continue
                column_names = [col[0].lower() for col in cur.description]
                exercise_data = dict(zip(column_names, result[0]))
                have_equipment = True
                for equipment in exercise_data['equipments']:
                    if equipment not in user_data['equipments']:
                        have_equipment = False
                        break
                if have_equipment:
                    exercise_recommendations.append(exercise_data)
                    break
        except Exception as e:
            print(e)
            return jsonify({"error": True, "message": "INTERNAL_SERVER_ERROR", "data": []}), 400
        
    return jsonify({"error": False, "message": "SUCCESS", "data": exercise_recommendations}), 200

if __name__ == '__main__':
    load_dotenv('.env', override=True)
    app.run(debug=True, host='0.0.0.0', port=5000)

