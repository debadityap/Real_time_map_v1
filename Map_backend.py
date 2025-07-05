# backend_app.py

from flask import Flask, render_template, jsonify
import requests
from threading import Thread
import time
import math
import webbrowser

app = Flask(__name__)

# ✅ Replace this with the IP printed by your ESP32 (e.g., 192.168.0.102)
esp32_ip = "http://your ip address/"

gps_points = []

def haversine(lat1, lon1, lat2, lon2):
    from math import radians, sin, cos, sqrt, atan2
    R = 6371  # Earth radius in km
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c

def fetch_gps_data():
    while True:
        try:
            response = requests.get(esp32_ip, timeout=5)
            if response.status_code == 200:
                data = response.text.strip()

                try:
                    lat_lng = dict(item.split("=") for item in data.split("&"))
                    lat = float(lat_lng["lat"])
                    lng = float(lat_lng["lng"])
                except:
                    try:
                        lat, lng = map(float, data.split(","))
                    except:
                        try:
                            lines = data.split("\n")
                            lat = float(lines[0].split(":")[1].strip())
                            lng = float(lines[1].split(":")[1].strip())
                        except:
                            continue

                if not gps_points or (gps_points[-1] != [lat, lng]):
                    gps_points.append([lat, lng])
                    print(f"New GPS point: {lat}, {lng}")
        except:
            pass
        time.sleep(5)

@app.route('/')
def index():
    return render_template('map.html')

@app.route('/data')
def data():
    total_distance = 0
    for i in range(1, len(gps_points)):
        total_distance += haversine(
            gps_points[i-1][0], gps_points[i-1][1],
            gps_points[i][0], gps_points[i][1]
        )
    return jsonify({
        "points": gps_points,
        "distance": round(total_distance, 3)
    })

if __name__ == '__main__':
    Thread(target=fetch_gps_data, daemon=True).start()
    webbrowser.open("http://127.0.0.1:5000")  # Auto open map page
    app.run(debug=True, port=5000)