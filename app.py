from flask import Flask, render_template, request, jsonify
import pymongo
from bson.objectid import ObjectId
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Database configuration from environment variables
MONGO_URI = os.getenv('MONGO_URI')
DB_NAME = os.getenv('DB_NAME')
COLLECTION_NAME = os.getenv('COLLECTION_NAME')

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

@app.route('/')
def index():
    """Render the main control page"""
    if device_collection is None:
        return render_template('index.html', devices=[], error="Database connection failed")
    devices = list(device_collection.find())
    return render_template('index.html', devices=devices)

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