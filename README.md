# ESG Agent - Environmental, Social & Governance Evaluation System

A comprehensive ESG evaluation system for financial transactions using AI-powered analysis.

## Project Structure

```
ESGAgent/
├── backend/                 # Python Flask backend
│   ├── classes/            # Data classes and state management
│   ├── nodes/              # AI agents for ESG analysis
│   ├── application.py      # Flask web server
│   ├── main.py            # Main workflow orchestration
│   ├── requirements.txt   # Python dependencies
│   └── .env              # Environment variables
├── frontend/              # Frontend web application
│   ├── index.html        # Main HTML page
│   ├── styles.css        # CSS styles
│   ├── script.js         # JavaScript functionality
│   └── package.json      # Frontend dependencies (optional)
└── README.md             # This file
```

## Installation & Setup

### Backend Setup

1. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env file with your API keys
   ```

5. **Run the backend server:**
   ```bash
   python application.py
   ```
   The backend will be available at `http://localhost:5000`

### Frontend Setup

1. **Navigate to frontend directory:**
   ```bash
   cd frontend
   ```

2. **Option 1: Simple HTTP Server (Python)**
   ```bash
   python -m http.server 3000
   ```

3. **Option 2: Node.js HTTP Server (if you have Node.js)**
   ```bash
   npm install
   npm run serve
   ```

4. **Option 3: Open directly in browser**
   Simply open `index.html` in your web browser

The frontend will be available at `http://localhost:3000`

## Environment Variables

Create a `.env` file in the backend directory with the following variables:

```env
# Required API Keys
OPENROUTER_API_KEY=your_openrouter_api_key_here

# Optional - if using OpenAI directly
OPENAI_API_KEY=your_openai_api_key_here

# Server Configuration
FLASK_PORT=5000
FLASK_HOST=0.0.0.0
FLASK_ENV=development

# Frontend URL
FRONTEND_URL=http://localhost:3000
```

## Usage

1. **Start the backend server** (port 5000)
2. **Open the frontend** (port 3000)
3. **Fill in transaction details** or click "Load Mock Data"
4. **Click "Analyze ESG Score"** to get the evaluation
5. **View results** including scores, charts, and recommendations

## API Endpoints

### POST /api/esg
Analyze ESG score for a transaction.

**Request Body:**
```json
{
  "transaction_data": {
    "transaction_id": "TXN_001",
    "transaction_description": "ủng hộ quỹ từ thiện mua xe điện cho bệnh viện",
    "payment_method": "mobile banking",
    "amount": 1000000,
    "aml_flag": "clean"
  },
  "sender_info": {
    "sender_name": "Nguyen Van A",
    "kyc_status": "verified"
  },
  "receiver_info": {
    "receiver_name": "Bệnh viện Nhi Trung Ương",
    "business_type": "healthcare charity",
    "kyc_status": "verified",
    "environmental_certificates": ["ISO 14001"],
    "business_license": "123456789",
    "tax_code": "987654321",
    "company_size": "large"
  }
}
```

## Dependencies

### Backend (Python)
- Flask: Web framework
- Flask-CORS: Cross-origin resource sharing
- LangGraph: Workflow orchestration
- OpenAI: AI API client
- Requests: HTTP library
- Python-dotenv: Environment variables

### Frontend (Vanilla JS)
- Chart.js: Data visualization
- Font Awesome: Icons
- No framework dependencies - pure HTML/CSS/JavaScript

## Development

### Running Tests
```bash
cd backend
python -m pytest
```

### Code Formatting
```bash
cd backend
black .
flake8 .
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License.
