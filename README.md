# IoT Light Control System

A web application to control LED lights connected to a Raspberry Pi.

## Features

- Real-time LED status monitoring
- Remote control of LED state
- MongoDB database integration
- Responsive web interface
- RESTful API for Raspberry Pi integration

## Local Development

1. Clone the repository:
```bash
git clone https://github.com/yourusername/iot-light-control.git
cd iot-light-control
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python app.py
```

The application will be available at `http://localhost:5000`

## Deployment

### GitHub Setup

1. Create a new repository on GitHub
2. Initialize git in your project directory:
```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/yourusername/iot-light-control.git
git push -u origin main
```

### Render Deployment

1. Sign up for a Render account (https://render.com)
2. Create a new Web Service
3. Connect your GitHub repository
4. Configure the service:
   - Name: iot-light-control
   - Environment: Python
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app`
5. Add environment variables:
   - `MONGO_URI`: Your MongoDB connection string
   - `PORT`: 5000
6. Deploy the service

## API Endpoints

- `GET /`: Web interface
- `POST /update_led`: Update LED status
- `GET /api/led_status`: Get current LED status

## Raspberry Pi Integration

Update the `SERVER_URL` in your Raspberry Pi script to point to your deployed Render URL.

## License

MIT License

## Components

1. **Web Application**: A Flask-based web app with a user interface to control the LED
2. **MongoDB Database**: Stores the LED status
3. **Raspberry Pi Script**: Reads the status from the database and controls the physical LED

## Setup Instructions

### 1. Web Application Setup

#### Local Development
1. Clone this repository
2. Navigate to the project directory
3. Create a virtual environment:
   ```
   python -m venv venv
   venv\Scripts\activate  # Windows
   source venv/bin/activate  # Linux/Mac
   ```
4. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
5. Copy `.env.example` to `.env` and update with your MongoDB connection string
6. Run the application:
   ```
   python app.py
   ```

#### Deployment to Heroku
1. Create a Heroku account if you don't have one
2. Install the Heroku CLI
3. Login to Heroku:
   ```
   heroku login
   ```
4. Create a new Heroku app:
   ```
   heroku create iot-light-control
   ```
5. Set up MongoDB Atlas and add your connection string as a config var:
   ```
   heroku config:set MONGO_URI="your_mongodb_connection_string"
   ```
6. Deploy the application:
   ```
   git push heroku main
   ```

### 2. Raspberry Pi Setup

1. Copy `raspberry_pi_script.py` to your Raspberry Pi
2. Install the required dependencies:
   ```
   pip install RPi.GPIO requests python-dotenv
   ```
3. Connect an LED to GPIO pin 18 (or change the pin in the script)
   - Connect the anode (longer leg) of the LED to GPIO 18
   - Connect the cathode (shorter leg) to a resistor (220-330 ohm)
   - Connect the other end of the resistor to GND
4. Create a `.env` file with your deployed web app URL:
   ```
   SERVER_URL=https://your-deployed-app.herokuapp.com
   ```
5. Run the script:
   ```
   python raspberry_pi_script.py
   ```

## Usage

1. Open the web application in your browser
2. Click the "Turn ON" button to turn on the LED connected to the Raspberry Pi
3. Click the "Turn OFF" button to turn off the LED

## How It Works

1. When you click a button on the web interface, it sends a request to the server
2. The server updates the LED status in the MongoDB database
3. The Raspberry Pi script periodically checks the status from the API
4. When a status change is detected, the script controls the physical LED accordingly "# led" 
"# pi-led" 
"# pi-ledcontrol" 
