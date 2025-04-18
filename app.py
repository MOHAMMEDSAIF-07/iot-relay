from flask import Flask, render_template_string, request, jsonify
import pymongo
from bson.objectid import ObjectId

app = Flask(__name__)

# Database configuration - same as in main.py
MONGO_URI = "mongodb+srv://mdsaif123:22494008@iotusingrelay.vfu72n2.mongodb.net/"
DB_NAME = "test"
COLLECTION_NAME = "devices"

# Initialize MongoDB connection
try:
    mongo_client = pymongo.MongoClient(MONGO_URI)
    # Ping the server to verify the connection
    mongo_client.admin.command('ping')
    print("Successfully connected to MongoDB!")
    database = mongo_client[DB_NAME]
    device_collection = database[COLLECTION_NAME]
except Exception as e:
    print(f"MongoDB connection error: {e}")
    # Continue with app setup but we'll handle the error later
    mongo_client = None
    database = None
    device_collection = None

# Define the LED configuration
LED_CONFIG = [
    {"name": "LED 1", "pin": 17, "device_type": "led 1"},
    {"name": "LED 2", "pin": 27, "device_type": "led 2"},
    {"name": "LED 3", "pin": 22, "device_type": "led 3"},
    {"name": "LED 4", "pin": 18, "device_type": "led 4"}
]

# HTML template as a string
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Raspberry Pi LED Control</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        :root {
            --primary: #3498db;
            --primary-dark: #2980b9;
            --success: #2ecc71;
            --success-dark: #27ae60;
            --danger: #e74c3c;
            --danger-dark: #c0392b;
            --warning: #f39c12;
            --warning-dark: #e67e22;
            --purple: #9b59b6;
            --purple-dark: #8e44ad;
            --light: #f5f5f5;
            --dark: #333;
            --gray: #7f8c8d;
            --shadow: rgba(0, 0, 0, 0.1);
        }
        
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #f5f7fa 0%, #e2e7ed 100%);
            color: var(--dark);
            min-height: 100vh;
            padding: 0;
            margin: 0;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        
        header {
            background: linear-gradient(135deg, #2c3e50 0%, #1a252f 100%);
            color: white;
            padding: 1.5rem 0;
            margin-bottom: 2rem;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }
        
        .header-content {
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 20px;
            text-align: center;
        }
        
        h1 {
            font-weight: 700;
            font-size: 2.5rem;
            margin-bottom: 0.5rem;
            letter-spacing: -0.5px;
        }
        
        .subtitle {
            color: rgba(255,255,255,0.8);
            font-size: 1.1rem;
            font-weight: 300;
            margin-bottom: 0.5rem;
        }
        
        .control-panel {
            background: white;
            border-radius: 12px;
            box-shadow: 0 8px 30px rgba(0,0,0,0.1);
            padding: 2rem;
            margin-bottom: 2rem;
        }
        
        .button-row {
            display: flex;
            justify-content: center;
            gap: 1rem;
            margin-bottom: 1.5rem;
        }
        
        .btn {
            padding: 0.8rem 1.5rem;
            border: none;
            border-radius: 6px;
            font-weight: 600;
            font-size: 1rem;
            cursor: pointer;
            transition: all 0.2s ease;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
            color: white;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 8px rgba(0,0,0,0.15);
        }
        
        .btn:active {
            transform: translateY(0);
        }
        
        .btn-primary {
            background-color: var(--primary);
        }
        
        .btn-primary:hover {
            background-color: var(--primary-dark);
        }
        
        .btn-success {
            background-color: var(--success);
        }
        
        .btn-success:hover {
            background-color: var(--success-dark);
        }
        
        .btn-danger {
            background-color: var(--danger);
        }
        
        .btn-danger:hover {
            background-color: var(--danger-dark);
        }
        
        .btn-purple {
            background-color: var(--purple);
        }
        
        .btn-purple:hover {
            background-color: var(--purple-dark);
        }
        
        .device-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
            gap: 1.5rem;
        }
        
        .device-card {
            background: white;
            border-radius: 12px;
            padding: 1.5rem;
            box-shadow: 0 4px 12px rgba(0,0,0,0.08);
            text-align: center;
            transition: all 0.3s ease;
            border: 1px solid rgba(0,0,0,0.05);
            position: relative;
            overflow: hidden;
        }
        
        .device-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 24px rgba(0,0,0,0.12);
        }
        
        .device-card h2 {
            font-size: 1.4rem;
            margin: 1rem 0 0.5rem;
            color: var(--dark);
        }
        
        .led-indicator {
            width: 100px;
            height: 100px;
            border-radius: 50%;
            margin: 0 auto;
            background-color: #e0e0e0;
            position: relative;
            transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            border: 6px solid #f1f1f1;
            box-shadow: inset 0 0 15px rgba(0,0,0,0.1);
        }
        
        .led-indicator::after {
            content: "";
            position: absolute;
            top: 15%;
            left: 15%;
            width: 25%;
            height: 25%;
            border-radius: 50%;
            background-color: rgba(255,255,255,0.7);
            opacity: 0.8;
        }
        
        .led-on {
            background: radial-gradient(circle, #ffdd4b 0%, #ff9800 70%);
            box-shadow: 0 0 30px rgba(255, 152, 0, 0.7), 
                        inset 0 0 15px rgba(255, 255, 255, 0.4);
            border-color: #ffd04a;
        }
        
        .status {
            margin: 1rem 0;
            font-weight: 600;
            font-size: 1.1rem;
            color: var(--gray);
        }
        
        .status-on {
            color: var(--success);
        }
        
        .pin-info {
            font-size: 0.9rem;
            color: var(--gray);
            margin-bottom: 1rem;
            padding: 6px 10px;
            background-color: rgba(0,0,0,0.03);
            border-radius: 4px;
            display: inline-block;
        }
        
        .error-message {
            background-color: #fdeaea;
            border-left: 4px solid var(--danger);
            color: var(--danger-dark);
            padding: 1rem;
            margin: 1rem 0;
            border-radius: 4px;
            font-weight: 500;
        }
        
        footer {
            text-align: center;
            padding: 1.5rem;
            margin-top: 2rem;
            font-size: 0.9rem;
            color: var(--gray);
            background-color: rgba(255,255,255,0.7);
            border-top: 1px solid rgba(0,0,0,0.05);
        }
        
        @media (max-width: 768px) {
            .device-grid {
                grid-template-columns: 1fr;
            }
            .button-row {
                flex-direction: column;
            }
            .btn {
                width: 100%;
            }
        }
    </style>
</head>
<body>
    <header>
        <div class="header-content">
            <h1>Raspberry Pi LED Control</h1>
            <p class="subtitle">Control your Raspberry Pi LEDs remotely</p>
        </div>
    </header>

    <div class="container">
        {% if error %}
        <div class="error-message">
            {{ error }}
        </div>
        {% endif %}

        <div class="control-panel">
            <div class="button-row">
                <button class="btn btn-primary" onclick="toggleAll('on')">
                    <i class="fas fa-power-off"></i> Turn All On
                </button>
                <button class="btn btn-danger" onclick="toggleAll('off')">
                    <i class="fas fa-power-off"></i> Turn All Off
                </button>
            </div>

            <div class="device-grid">
                {% for device in devices %}
                <div class="device-card">
                    <div class="led-indicator {% if device.state %}led-on{% endif %}" id="led-{{ device._id }}"></div>
                    <h2>{{ device.name }}</h2>
                    <div class="pin-info">GPIO Pin: {{ device.pin }}</div>
                    <div class="status {% if device.state %}status-on{% endif %}" id="status-{{ device._id }}">
                        {{ "ON" if device.state else "OFF" }}
                    </div>
                    <button class="btn {% if device.state %}btn-danger{% else %}btn-success{% endif %}" 
                            onclick="toggleDevice('{{ device._id }}')">
                        <i class="fas fa-power-off"></i>
                        {{ "Turn Off" if device.state else "Turn On" }}
                    </button>
                </div>
                {% endfor %}
            </div>
        </div>
    </div>

    <footer>
        <p>Raspberry Pi LED Control System &copy; 2024</p>
    </footer>

    <script>
        function toggleDevice(deviceId) {
            fetch(`/api/toggle/${deviceId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    const led = document.getElementById(`led-${deviceId}`);
                    const status = document.getElementById(`status-${deviceId}`);
                    const button = led.parentElement.querySelector('button');
                    
                    if (data.state) {
                        led.classList.add('led-on');
                        status.textContent = 'ON';
                        status.classList.add('status-on');
                        button.textContent = 'Turn Off';
                        button.classList.remove('btn-success');
                        button.classList.add('btn-danger');
                    } else {
                        led.classList.remove('led-on');
                        status.textContent = 'OFF';
                        status.classList.remove('status-on');
                        button.textContent = 'Turn On';
                        button.classList.remove('btn-danger');
                        button.classList.add('btn-success');
                    }
                }
            })
            .catch(error => console.error('Error:', error));
        }

        function toggleAll(action) {
            fetch('/api/devices')
                .then(response => response.json())
                .then(devices => {
                    devices.forEach(device => {
                        if ((action === 'on' && !device.state) || (action === 'off' && device.state)) {
                            toggleDevice(device._id);
                        }
                    });
                })
                .catch(error => console.error('Error:', error));
        }
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    """Render the main control page"""
    if device_collection is None:
        return render_template_string(HTML_TEMPLATE, devices=[], error="Database connection failed")
    devices = list(device_collection.find())
    return render_template_string(HTML_TEMPLATE, devices=devices)

@app.route('/api/devices', methods=['GET'])
def get_devices():
    """API endpoint to get all devices"""
    if device_collection is None:
        return jsonify({"error": "Database connection failed"}), 500
    devices = list(device_collection.find())
    # Convert ObjectId to string for JSON serialization
    for device in devices:
        device['_id'] = str(device['_id'])
    return jsonify(devices)

@app.route('/api/toggle/<device_id>', methods=['POST'])
def toggle_device(device_id):
    """Toggle the state of an LED"""
    if device_collection is None:
        return jsonify({"error": "Database connection failed"}), 500
    try:
        # Find the device
        device = device_collection.find_one({"_id": ObjectId(device_id)})
        if not device:
            return jsonify({"error": "Device not found"}), 404
            
        # Toggle the state
        current_state = device.get("state", False)
        new_state = not current_state
        
        # Update the database
        device_collection.update_one(
            {"_id": ObjectId(device_id)},
            {"$set": {"state": new_state}}
        )
        
        return jsonify({"success": True, "device_id": device_id, "state": new_state})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/update/<device_id>', methods=['POST'])
def update_device(device_id):
    """Update the state of an LED to a specific value"""
    if device_collection is None:
        return jsonify({"error": "Database connection failed"}), 500
    try:
        data = request.json
        new_state = data.get('state', False)
        
        # Update the database
        device_collection.update_one(
            {"_id": ObjectId(device_id)},
            {"$set": {"state": new_state}}
        )
        
        return jsonify({"success": True, "device_id": device_id, "state": new_state})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/update-all-names', methods=['GET'])
def update_all_names():
    """Update all device names to ensure they are LED 1, LED 2, etc."""
    if device_collection is None:
        return jsonify({"error": "Database connection failed"}), 500
    try:
        # Get all devices
        devices = list(device_collection.find())
        
        # Match devices with LED_CONFIG by pin number and update names
        updated_count = 0
        for device in devices:
            pin = device.get('pin')
            for led_config in LED_CONFIG:
                if led_config['pin'] == pin:
                    # Update name and device_type if needed
                    if device.get('name') != led_config['name'] or device.get('device_type') != led_config['device_type']:
                        device_collection.update_one(
                            {"_id": device['_id']},
                            {"$set": {
                                "name": led_config['name'],
                                "device_type": led_config['device_type']
                            }}
                        )
                        updated_count += 1
                    break
        
        return jsonify({"success": True, "updated_count": updated_count})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Only attempt to initialize database if connection was successful
    if device_collection is not None:
        # Check if devices exist in the collection, create them if not
        if device_collection.count_documents({}) == 0:
            # Create the 4 LED devices
            for led in LED_CONFIG:
                device_collection.insert_one({
                    "name": led["name"],
                    "pin": led["pin"],
                    "device_type": led["device_type"],
                    "state": False
                })
            print("Created LED devices in database")
        else:
            # Verify all devices have correct names and update if necessary
            devices = list(device_collection.find())
            update_needed = False
            
            # Check if we have exactly 4 devices with correct names
            if len(devices) != 4:
                update_needed = True
            else:
                # Check device names and types
                device_pins = [device.get('pin') for device in devices]
                for led in LED_CONFIG:
                    if led['pin'] not in device_pins:
                        update_needed = True
                        break
                        
                    # Verify correct names
                    for device in devices:
                        if device.get('pin') == led['pin'] and (device.get('name') != led['name'] or device.get('device_type') != led['device_type']):
                            update_needed = True
                            break
            
            if update_needed:
                # Clear and recreate all devices
                device_collection.delete_many({})
                for led in LED_CONFIG:
                    device_collection.insert_one({
                        "name": led["name"],
                        "pin": led["pin"],
                        "device_type": led["device_type"],
                        "state": False
                    })
                print("Reset LED devices in database")
            else:
                print("LED devices already exist with correct configuration")
        
        # Update any devices with old names on startup
        devices = list(device_collection.find())
        updated = 0
        for device in devices:
            pin = device.get('pin')
            for led_config in LED_CONFIG:
                if led_config['pin'] == pin and (device.get('name') != led_config['name'] or device.get('device_type') != led_config['device_type']):
                    device_collection.update_one(
                        {"_id": device['_id']},
                        {"$set": {
                            "name": led_config['name'],
                            "device_type": led_config['device_type']
                        }}
                    )
                    updated += 1
                    break
        
        if updated > 0:
            print(f"Updated {updated} device names to LED format")
    else:
        print("WARNING: Starting app without database connection. App will run in limited mode.")
    
    app.run(host='0.0.0.0', port=5000, debug=True) 