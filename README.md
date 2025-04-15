# EPL Prediction Engine

A machine learning powered Premier League prediction application that shows predicted standings and team statistics.

## Architecture

This application consists of two main components:

1. **Backend**: FastAPI server that provides EPL prediction data
2. **Frontend**: React app that displays predictions in an interactive UI

## Setup Instructions

### Backend Setup

1. Install required Python packages:

```bash
pip install -r requirements.txt
```

2. Place the `data_service.py` file in your backend directory alongside `main.py`:

```bash
cp data_service.py backend/
```

3. Update your `main.py` file with the improved version:

```bash
cp improved_main.py backend/main.py
```

4. Start the FastAPI server:

```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at http://127.0.0.1:8000/

### Frontend Setup

1. Install required frontend dependencies:

```bash
cd frontend
npm install prop-types
```

2. Create the TeamView component:

```bash
mkdir -p src/components
cp TeamView.jsx src/components/
```

3. Update your App.jsx:

```bash
cp App.jsx src/
```

4. Add the placeholder team logo:

```bash
cp placeholder-logo.png public/
```

5. Start the development server:

```bash
npm run dev
```

## API Documentation

Once the backend is running, view the API documentation at:
http://127.0.0.1:8000/docs

Available API endpoints:

- `GET /standings?season={season}` - Get league standings for a season
- `GET /team?season={season}&team={team}` - Get team details for a specific season
- `GET /seasons` - List all available seasons
- `GET /teams?season={season}` - List all teams in a season
- `GET /health` - API health check

## Model Information

The prediction engine uses a trained RandomForestRegressor model to predict team performance. The model was trained on multiple seasons of Premier League data, including:

- Team statistics (goals, points, wins, etc.)
- Manager ratings
- Team tier information
- Historical performance

## Troubleshooting

If you encounter issues:

1. Make sure both backend and frontend servers are running
2. Check that the data CSV file exists at the expected path
3. Verify the backend is accessible at http://127.0.0.1:8000/health
4. Check browser console for any CORS or connection errors
5. Ensure the simulated_season_history.csv file has the correct format

## License

This project is licensed under the MIT License - see the LICENSE file for details.