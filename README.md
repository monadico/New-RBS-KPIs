# Betting Analytics Dashboard

A real-time betting analytics dashboard for RareBet Sports, built with React and Flask.

## 🏗️ Architecture

```
Monad Testnet → betting_database.py → SQLite DB → Flask API → React Frontend
```

- **Backend**: Flask API that serves aggregated data from SQLite database
- **Database**: SQLite with betting transaction data
- **Frontend**: React app with charts and analytics
- **Data Source**: Monad testnet blockchain data

## 📁 Project Structure

```
project/
├── backend/
│   ├── betting_database.py      # Data fetcher from Monad
│   ├── app.py                   # Flask API server
│   ├── requirements.txt
│   └── betting_transactions.db  # SQLite database
├── frontend/
│   ├── src/
│   ├── package.json
│   └── public/
└── start_local.py              # Script to run both locally
```

## 🚀 Quick Start

### 1. Install Dependencies

**Backend:**
```bash
cd backend
pip install -r requirements.txt
```

**Frontend:**
```bash
cd frontend
npm install
```

### 2. Update Database (if needed)

```bash
python betting_database.py --incremental  # Get new data
# or
python betting_database.py --start-block 0  # Full refresh
```

### 3. Start Local Development

**Option A: Use the startup script**
```bash
python start_local.py
```

**Option B: Start manually**
```bash
# Terminal 1 - Backend
cd backend
python app.py

# Terminal 2 - Frontend
cd frontend
npm start
```

### 4. Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:5000

## 📊 API Endpoints

- `GET /api/stats` - Basic statistics
- `GET /api/weekly` - Weekly aggregated data
- `GET /api/health` - Health check

## 🔧 Development

### Backend Development

The backend is a simple Flask API that:
- Reads from SQLite database
- Provides aggregated statistics
- Serves weekly data for charts

### Frontend Development

The frontend is a React app that:
- Fetches data from the API
- Creates interactive charts
- Displays analytics dashboard

### Database Updates

To update the database with new data:

```bash
python betting_database.py --incremental
```

This will fetch new transactions from Monad testnet and add them to the database.

## 🚀 Deployment

### Backend Deployment

1. Deploy to Railway/Render/Heroku
2. Set environment variables:
   - `DATABASE_PATH`: Path to database file

### Frontend Deployment

1. Build the React app:
   ```bash
   cd frontend
   npm run build
   ```

2. Deploy to Vercel/Netlify/GitHub Pages

## 📈 Features

- **Real-time Analytics**: Live data from Monad testnet
- **Weekly Breakdowns**: Transaction and volume analysis by week
- **Token Distribution**: MON vs Jerry token usage
- **User Analytics**: Unique users and engagement metrics
- **Interactive Charts**: Visual data representation

## 🔄 Data Flow

1. **Data Collection**: `betting_database.py` fetches from Monad testnet
2. **Storage**: Data stored in SQLite database
3. **API**: Flask serves aggregated data
4. **Frontend**: React displays charts and analytics

## 🛠️ Customization

### Adding New Analytics

1. Add new endpoints in `backend/app.py`
2. Create new components in `frontend/src/components`
3. Update types in `frontend/src/types/index.ts`

### Modifying Charts

The frontend uses Chart.js for visualizations. Add new charts by:
1. Installing chart components
2. Creating chart data from API responses
3. Adding chart components to Dashboard

## 📝 License

MIT License
