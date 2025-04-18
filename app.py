from flask import Flask, request, jsonify
import pymongo
import os
from dotenv import load_dotenv
import datetime

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Configuration
MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://scortal143:QSVgtxWjUqhEOpcJ@ledstatus.tr1ke.mongodb.net/")
PORT = int(os.getenv("PORT", 5000))
SERVER_URL = os.getenv("SERVER_URL", "https://your-deployed-app.herokuapp.com")

# MongoDB connection
client = pymongo.MongoClient(MONGO_URI)
db = client.iot_db
led_collection = db.led_status

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>IoT Light Control System</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }}

        body {{
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            padding: 20px;
        }}

        .container {{
            width: 100%;
            max-width: 600px;
        }}

        header {{
            text-align: center;
            margin-bottom: 30px;
        }}

        h1 {{
            color: #2c3e50;
            font-size: 2.5rem;
            margin-bottom: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
        }}

        h1 i {{
            color: #f1c40f;
        }}

        .subtitle {{
            color: #7f8c8d;
            font-size: 1.1rem;
        }}

        .card {{
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);
            padding: 30px;
            margin-bottom: 20px;
        }}

        .status-container {{
            display: flex;
            align-items: center;
            gap: 20px;
            margin-bottom: 30px;
        }}

        .indicator {{
            width: 80px;
            height: 80px;
            border-radius: 50%;
            transition: all 0.3s ease;
            position: relative;
        }}

        .indicator.on {{
            background: linear-gradient(145deg, #4CAF50, #45a049);
            box-shadow: 0 0 20px rgba(76, 175, 80, 0.5);
        }}

        .indicator.off {{
            background: linear-gradient(145deg, #e0e0e0, #bdbdbd);
            box-shadow: inset 2px 2px 5px rgba(0, 0, 0, 0.1);
        }}

        .status-info {{
            flex: 1;
            text-align: left;
        }}

        .status-info p {{
            margin: 5px 0;
            font-size: 1.1rem;
            color: #2c3e50;
        }}

        .status-on {{
            color: #4CAF50;
            font-weight: 600;
        }}

        .status-off {{
            color: #e74c3c;
            font-weight: 600;
        }}

        .last-updated {{
            font-size: 0.9rem !important;
            color: #7f8c8d !important;
        }}

        .divider {{
            height: 1px;
            background: linear-gradient(to right, transparent, #e0e0e0, transparent);
            margin: 20px 0;
        }}

        .controls {{
            display: flex;
            gap: 15px;
            justify-content: center;
        }}

        .btn {{
            padding: 12px 25px;
            border: none;
            border-radius: 8px;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            display: flex;
            align-items: center;
            gap: 8px;
            min-width: 140px;
            justify-content: center;
        }}

        .btn i {{
            font-size: 1.1rem;
        }}

        .btn:disabled {{
            opacity: 0.5;
            cursor: not-allowed;
            transform: none;
        }}

        .btn.on {{
            background: linear-gradient(145deg, #4CAF50, #45a049);
            color: white;
        }}

        .btn.on:hover:not(:disabled) {{
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(76, 175, 80, 0.3);
        }}

        .btn.off {{
            background: linear-gradient(145deg, #e74c3c, #c0392b);
            color: white;
        }}

        .btn.off:hover:not(:disabled) {{
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(231, 76, 60, 0.3);
        }}

        .btn.loading {{
            position: relative;
            pointer-events: none;
        }}

        .btn.loading::after {{
            content: '';
            width: 20px;
            height: 20px;
            border: 2px solid rgba(255, 255, 255, 0.3);
            border-radius: 50%;
            border-top-color: white;
            animation: spin 0.8s linear infinite;
            position: absolute;
            right: 10px;
        }}

        @keyframes spin {{
            to {{ transform: rotate(360deg); }}
        }}

        footer {{
            text-align: center;
            color: #7f8c8d;
            font-size: 0.9rem;
        }}

        .help-link {{
            color: #3498db;
            text-decoration: none;
            transition: color 0.3s ease;
        }}

        .help-link:hover {{
            color: #2980b9;
        }}

        @media (max-width: 500px) {{
            .container {{
                padding: 10px;
            }}
            
            h1 {{
                font-size: 2rem;
            }}
            
            .card {{
                padding: 20px;
            }}
            
            .status-container {{
                flex-direction: column;
                text-align: center;
            }}
            
            .status-info {{
                text-align: center;
            }}
            
            .controls {{
                flex-direction: column;
            }}
            
            .btn {{
                width: 100%;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1><i class="fas fa-lightbulb"></i> Smart Light Control</h1>
            <p class="subtitle">IoT Raspberry Pi LED Management System</p>
        </header>
        
        <div class="card">
            <div class="status-container">
                <div class="indicator {led_status_class}"></div>
                <div class="status-info">
                    <p>Current Status: <span id="status-text" class="{status_text_class}">{status_text}</span></p>
                    <p class="last-updated">Last updated: <span id="timestamp">{timestamp}</span></p>
                </div>
            </div>
            
            <div class="divider"></div>
            
            <div class="controls">
                <button id="turn-on" class="btn on" {turn_on_disabled}>
                    <i class="fas fa-power-off"></i> Turn ON
                </button>
                <button id="turn-off" class="btn off" {turn_off_disabled}>
                    <i class="fas fa-power-off"></i> Turn OFF
                </button>
            </div>
        </div>
    </div>

    <script>
        $(document).ready(function() {{
            function updateTimestamp() {{
                const now = new Date();
                const options = {{ 
                    hour: '2-digit', 
                    minute: '2-digit',
                    second: '2-digit',
                    hour12: true
                }};
                return now.toLocaleTimeString([], options);
            }}
            
            // Set initial timestamp if available
            if ($('#timestamp').text() === 'N/A') {{
                $('#timestamp').text(updateTimestamp());
            }}
            
            // Turn ON button
            $('#turn-on').click(function() {{
                const $btn = $(this);
                $btn.addClass('loading');
                
                $.post('/update_led', {{status: 1}}, function(data) {{
                    $btn.removeClass('loading');
                    if (data.success) {{
                        $('.indicator').removeClass('off').addClass('on');
                        $('#status-text').removeClass('status-off').addClass('status-on').text('ON');
                        $('#timestamp').text(updateTimestamp());
                        $('#turn-on').prop('disabled', true);
                        $('#turn-off').prop('disabled', false);
                    }}
                }});
            }});

            // Turn OFF button
            $('#turn-off').click(function() {{
                const $btn = $(this);
                $btn.addClass('loading');
                
                $.post('/update_led', {{status: 0}}, function(data) {{
                    $btn.removeClass('loading');
                    if (data.success) {{
                        $('.indicator').removeClass('on').addClass('off');
                        $('#status-text').removeClass('status-on').addClass('status-off').text('OFF');
                        $('#timestamp').text(updateTimestamp());
                        $('#turn-off').prop('disabled', true);
                        $('#turn-on').prop('disabled', false);
                    }}
                }});
            }});
        }});
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    # Get the latest LED status from database
    latest_status = led_collection.find_one(
        {"device_id": "raspberry_pi_1"},
        sort=[("timestamp", pymongo.DESCENDING)]
    )
    
    led_status = 0  # Default is off
    timestamp = None
    if latest_status:
        led_status = latest_status.get("status", 0)
        timestamp = latest_status.get("timestamp", None)
    
    # Prepare template variables
    template_vars = {
        'led_status_class': 'on' if led_status == 1 else 'off',
        'status_text_class': 'status-on' if led_status == 1 else 'status-off',
        'status_text': 'ON' if led_status == 1 else 'OFF',
        'timestamp': timestamp.strftime('%I:%M:%S %p') if timestamp else 'N/A',
        'turn_on_disabled': 'disabled' if led_status == 1 else '',
        'turn_off_disabled': 'disabled' if led_status == 0 else ''
    }
    
    return HTML_TEMPLATE.format(**template_vars)

@app.route('/update_led', methods=['POST'])
def update_led():
    status = int(request.form.get('status', 0))
    
    # Delete all previous status records
    led_collection.delete_many({"device_id": "raspberry_pi_1"})
    
    # Insert the new status
    led_collection.insert_one({
        "device_id": "raspberry_pi_1",
        "status": status,
        "timestamp": datetime.datetime.utcnow()
    })
    
    return jsonify({"success": True, "status": status})

@app.route('/api/led_status', methods=['GET'])
def get_led_status():
    # API endpoint for Raspberry Pi to check status
    latest_status = led_collection.find_one(
        {"device_id": "raspberry_pi_1"},
        sort=[("timestamp", pymongo.DESCENDING)]
    )
    
    led_status = 0  # Default is off
    if latest_status and "status" in latest_status:
        led_status = latest_status["status"]
    
    return jsonify({"status": led_status})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PORT, debug=True) 