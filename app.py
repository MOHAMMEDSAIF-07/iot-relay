from flask import Flask, render_template, request, jsonify
import pymongo
from bson.objectid import ObjectId
import os

app = Flask(__name__)

# Database configuration
MONGO_URI = os.environ.get('MONGO_URI', "mongodb+srv://mdsaif123:22494008@iotusingrelay.vfu72n2.mongodb.net/")
DB_NAME = os.environ.get('DB_NAME', "test")
COLLECTION_NAME = os.environ.get('COLLECTION_NAME', "devices")

# Initialize MongoDB connection
try:
    mongo_client = pymongo.MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    # Ping the server to verify the connection
    mongo_client.admin.command('ping')
    print("Successfully connected to MongoDB!")
    database = mongo_client[DB_NAME]
    device_collection = database[COLLECTION_NAME]
except Exception as e:
    print(f"MongoDB connection error: {e}")
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

@app.route('/')
def index():
    """Render the main control page"""
    try:
        if device_collection is None:
            return render_template('index.html', devices=[], error="Database connection failed")
        devices = list(device_collection.find())
        return render_template('index.html', devices=devices)
    except Exception as e:
        print(f"Error in index route: {e}")
        return render_template('index.html', devices=[], error=str(e))

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
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False) 