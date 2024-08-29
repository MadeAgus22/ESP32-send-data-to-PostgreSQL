from flask import Flask, request, jsonify
import psycopg2

app = Flask(__name__)

# PostgreSQL connection configuration
conn = psycopg2.connect(
    host="localhost",
    database="sensor_db",
    user="sensor_ultrasonic_user",
    password="qwerty1234"
)
cursor = conn.cursor()

@app.route('/sensor-data', methods=['POST'])
def sensor_data():
    try:
        distance = request.form['distance']
        cursor.execute("INSERT INTO sensor_data (distance) VALUES (%s)", (distance,))
        conn.commit()
        return jsonify({"status": "success", "distance": distance}), 201
    except Exception as e:
        # Log error for debugging
        print(f"Error: {e}")
        conn.rollback()  # Rollback the transaction in case of error
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
