# Setup Instructions for Angular Chat UI

## Step 1: Install Node.js (if not already installed)

The Angular CLI requires Node.js. Install it from: https://nodejs.org/

Verify installation:
```bash
node --version
npm --version
```

## Step 2: Install Angular CLI and Dependencies

```bash
cd ChatUI
npm install -g @angular/cli
npm install
```

## Step 3: Start the Flask API Server

Open a new terminal and run:
```bash
cd Code
python api_server.py
```

The API will start on http://localhost:5000

## Step 4: Start the Angular Development Server

In another terminal:
```bash
cd ChatUI
ng serve
```

Or use npm:
```bash
npm start
```

The app will be available at http://localhost:4200

## Quick Start (Windows)

1. Double-click `start_api.bat` to start the API server
2. In another terminal: `cd ChatUI && npm start`

## Troubleshooting

- **Port 5000 already in use**: Change the port in `api_server.py`
- **Port 4200 already in use**: Angular will ask to use a different port
- **CORS errors**: Make sure Flask-CORS is installed and the API server is running
- **API connection errors**: Verify the API is running at http://localhost:5000

