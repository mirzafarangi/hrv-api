# HRV Metrics API

A REST API for processing and storing Heart Rate Variability (HRV) data.

## Project Overview

This API processes incoming HRV session data, calculates various HRV metrics, and stores the data in a PostgreSQL database. It provides endpoints for submitting new HRV sessions, retrieving past sessions, and more.

## Features

- Process raw RR intervals to calculate HRV metrics
- Validate and clean HRV data
- Calculate time and frequency domain HRV metrics
- Organize metrics into functional indexes
- Store data in PostgreSQL for persistence
- RESTful API for data submission and retrieval

## Tech Stack

- **FastAPI**: Modern, fast API framework
- **SQLAlchemy**: SQL toolkit and ORM
- **Alembic**: Database migration tool
- **PostgreSQL**: Relational database (hosted on Render)
- **Pydantic**: Data validation and serialization
- **SciPy/NumPy**: Scientific computing for HRV analysis
- **Render**: Cloud hosting platform

## Project Structure

```
hrv_metrics_api/
├── alembic/                # Database migrations
├── app/
│   ├── api/                # API endpoints
│   ├── core/               # Core functionality
│   ├── constants/          # Constant values
│   ├── models/             # Data models
│   └── config.py           # Application configuration
├── main.py                 # Application entry point
├── requirements.txt        # Dependencies
└── README.md               # Documentation
```

## Local Development

### Prerequisites

- Python 3.9+
- PostgreSQL

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/hrv-metrics-api.git
   cd hrv-metrics-api
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file based on `.env.example`:
   ```bash
   cp .env.example .env
   # Edit .env with your database credentials
   ```

5. Run database migrations:
   ```bash
   alembic upgrade head
   ```

6. Start the development server:
   ```bash
   uvicorn main:app --reload
   ```

7. Access the API documentation at https://hrv-api-86i0.onrender.com/docs

## Deployment on Render

### Database Setup

1. In your Render dashboard, go to "New" > "PostgreSQL".
2. Configure the database:
   - Name: `HRV_records`
   - Database: `hrv_records_db`
   - User: `ashkan` (or your preferred username)
   - Region: `Frankfurt (EU Central)`
   - Plan: Choose according to your needs (e.g., Free, Basic, Pro)

3. Wait for the database to be created. Note the connection details.

### API Service Setup

1. In your Render dashboard, go to "New" > "Web Service".
2. Connect your GitHub repository.
3. Configure the service:
   - Name: `HRV Metrics API`
   - Root Directory: `/` (or your subfolder if in a monorepo)
   - Environment: `Python`
   - Build Command: `./build.sh`
   - Start Command: `gunicorn -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:$PORT`
   - Plan: Choose according to your needs

4. Add the following environment variables:
   - `DATABASE_URL`: Copy the Internal Database URL from your PostgreSQL instance
   - `DEBUG`: Set to `False` for production

5. Click "Create Web Service" and wait for the deployment to complete.

6. Your API will be available at the URL provided by Render with documentation at `/docs`.

## API Endpoints

### Main Endpoints

- `POST /api/hrv/session`: Process and store a new HRV session
- `GET /api/hrv/sessions/user/{user_id}`: Get all sessions for a specific user
- `GET /api/hrv/sessions/tag/{tag_name}`: Get all sessions with a specific tag
- `GET /api/hrv/session/{session_id}`: Get detailed information for a specific session

### Example Request (Process Session)

```json
{
  "user_id": "user_test",
  "device_info": {
    "firmwareVersion": "2.1.9",
    "model": "Polar H10"
  },
  "recordingSessionId": "sample_session_001",
  "timestamp": "2025-03-25T23:10:00Z",
  "rrIntervals": [812, 805, 798, 790, 803, 815, 825, 833, 826, 819, 
                 810, 805, 795, 788, 782, 775, 780, 785, 790, 798, 
                 805, 810, 820, 830, 832, 835, 830, 825, 815, 808, 
                 800, 795, 790, 785, 780, 775, 780, 790, 805, 815, 
                 825, 830, 835, 830, 825, 815, 805, 795, 790, 785],
  "heartRate": 74,
  "motionArtifacts": false,
  "tags": ["Sleep"]
}
```

## Database Schema

The application uses several tables:

- `users`: Stores user information
- `devices`: Records device information
- `tags`: Contains session tags
- `hrv_sessions`: Main session details
- `hrv_metrics`: Calculated HRV metrics
- `rr_intervals`: Raw RR interval data


## License

MIT License

## Contributors

- Meta-Mar - beheshti@posteo.de
