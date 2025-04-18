# Raspberry Pi LED Control System

A web-based control system for managing LEDs connected to a Raspberry Pi. This application allows you to control multiple LEDs remotely through a web interface.

## Features

- Control multiple LEDs individually
- Turn all LEDs on/off with a single click
- Real-time status updates
- Responsive design for mobile and desktop
- MongoDB database integration for state management

## Prerequisites

- Python 3.8 or higher
- MongoDB database
- Raspberry Pi with GPIO pins
- LED components and resistors

## Installation

1. Clone the repository:
```bash
git clone <your-repository-url>
cd <repository-name>
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
Create a `.env` file with the following content:
```
MONGO_URI=your_mongodb_connection_string
```

## Usage

1. Start the application:
```bash
python app.py
```

2. Open your web browser and navigate to:
```
http://localhost:5000
```

## Deployment

This application can be deployed on Render:

1. Create a new Web Service on Render
2. Connect your GitHub repository
3. Set the following configuration:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python app.py`
   - Environment Variables: Add your MongoDB connection string as `MONGO_URI`

## License

This project is licensed under the MIT License - see the LICENSE file for details. 