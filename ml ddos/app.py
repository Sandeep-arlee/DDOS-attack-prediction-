from flask import Flask, render_template, jsonify
import threading
import time
from collections import deque
from datetime import datetime, timedelta
import random
import pickle
import numpy as np

app = Flask(__name__)

data_lock = threading.Lock()
packet_deque = deque(maxlen=60) 
attack_status = {"detected": False, "attacker_ip": None}
attack_running = True  
MAX_REQUESTS_PER_SECOND = 30  
with open('ddos_model.pkl', 'rb') as model_file:
    model = pickle.load(model_file)

NORMAL_TRAFFIC = 30  
ATTACK_TRAFFIC = 500  
ATTACK_INTERVAL = 5  

def generate_traffic():
    """Simulate traffic with regular attack bursts"""
    last_attack_time = time.time()
    attacker_ip = f"192.168.1.{random.randint(100, 200)}"
    
    while True:
        current_time = time.time()
        timestamp = datetime.now()
        
        with data_lock:
            
            for _ in range(NORMAL_TRAFFIC):
                source_ip = f"192.168.1.{random.randint(1, 50)}"
                packet_deque.append((timestamp, source_ip))
            
            if current_time - last_attack_time > ATTACK_INTERVAL:
                last_attack_time = current_time
                attacker_ip = f"192.168.1.{random.randint(100, 200)}"
                for _ in range(ATTACK_TRAFFIC):
                    packet_deque.append((timestamp, attacker_ip))
                attack_status.update({
                    "detected": True,
                    "attacker_ip": attacker_ip,
                    "start_time": timestamp.strftime("%H:%M:%S")
                })
            else:
                attack_status["detected"] = False

        time.sleep(1)

def detect_ddos():
    """Check for DDoS conditions using ML model every second"""
    while True:
        with data_lock:
            current_time = datetime.now()
            time_threshold = current_time - timedelta(seconds=1)
            
            ip_counts = {}
            for ts, ip in packet_deque:
                if ts > time_threshold:
                    ip_counts[ip] = ip_counts.get(ip, 0) + 1
            
            packet_count = sum(ip_counts.values())
            unique_ips = len(ip_counts)
            
            features = np.array([[packet_count, unique_ips]])
            prediction = model.predict(features)[0]

            if prediction == 1:  
                attack_status.update({
                    "detected": True,
                    "attacker_ip": max(ip_counts, key=ip_counts.get),
                    "start_time": time_threshold.strftime("%H:%M:%S")
                })
            else:
                attack_status["detected"] = False
        
        time.sleep(1)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/data')
def get_data():
    with data_lock:
        time_window = datetime.now() - timedelta(seconds=60)
        counts = [0] * 60
        
        for ts, _ in packet_deque:
            seconds_ago = (datetime.now() - ts).seconds
            if seconds_ago < 60:
                counts[59 - seconds_ago] += 1
        
        return jsonify({
            "packet_counts": counts,
            "attack": attack_status
        })

@app.route('/stop_attack', methods=['POST'])
def stop_attack():
    global attack_running
    attack_running = False  
    return jsonify({"message": "Attack stopped. Normal traffic generation resumed."})

def generate_limited_traffic():
    """Generate traffic with a limit after attack is stopped"""
    last_attack_time = time.time()
    attacker_ip = f"192.168.1.{random.randint(100, 200)}"
    
    while True:
        current_time = time.time()
        timestamp = datetime.now()
        
        with data_lock:
            for _ in range(NORMAL_TRAFFIC):
                source_ip = f"192.168.1.{random.randint(1, 50)}"
                packet_deque.append((timestamp, source_ip))
            
            if not attack_running:  
                for _ in range(MAX_REQUESTS_PER_SECOND):
                    source_ip = f"192.168.1.{random.randint(1, 50)}"
                    packet_deque.append((timestamp, source_ip))

            if attack_running and current_time - last_attack_time > ATTACK_INTERVAL:
                last_attack_time = current_time
                attacker_ip = f"192.168.1.{random.randint(100, 200)}"
                for _ in range(ATTACK_TRAFFIC):
                    packet_deque.append((timestamp, attacker_ip))
                attack_status.update({
                    "detected": True,
                    "attacker_ip": attacker_ip,
                    "start_time": timestamp.strftime("%H:%M:%S")
                })
            else:
                attack_status["detected"] = False

        time.sleep(1)

if __name__ == '__main__':
    threading.Thread(target=generate_limited_traffic, daemon=True).start()
    threading.Thread(target=detect_ddos, daemon=True).start()
    app.run(debug=True)
