# Fashion Assistant

A modern web application that helps users discover and explore fashion recommendations based on their preferences and style. The application combines a React-based frontend with a Python backend to provide an interactive and personalized fashion experience.

## Features

- Interactive chat interface for fashion recommendations
- Personalized style suggestions based on user preferences
- Session management for continuous conversations
- Modern, responsive UI built with React and Tailwind CSS
- Real-time fashion advice and recommendations

## Tech Stack

### Frontend

- React with TypeScript
- Vite for build tooling
- Tailwind CSS for styling
- Modern UI components and responsive design

### Backend

- Python-based server
- Custom fashion recommendation engine
- Session management system
- Logging and monitoring capabilities

## Project Structure

```
fashion-assistant/
├── frontend/           # React frontend application
│   ├── src/           # Source code
│   ├── dist/          # Build output
│   └── package.json   # Frontend dependencies
│
└── backend/           # Python backend server
    ├── services/      # Backend services
    ├── models.py      # Data models
    └── requirements.txt # Python dependencies
```

## Getting Started

### Prerequisites

- Node.js (v14 or higher)
- Python 3.8 or higher
- npm or yarn package manager

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Start the development server:
   ```bash
   npm run dev
   ```

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Start the backend server:
   ```bash
   python main.py
   ```

## Development

- Frontend development server runs on `http://localhost:5173`
- Backend server runs on `http://localhost:8000`

## Environment Variables

### Frontend Environment Variables

Create a `.env` file in the frontend directory with the following variables:

```bash
VITE_BACKEND_URL=http://localhost:8000  # Backend API URL
```

### Backend Environment Variables

Create a `.env` file in the backend directory with the following variables:

```bash
FRONTEND_URL=http://localhost:5173  # Frontend URL
GOOGLE_GEMINI_API_KEY=your_api_key  # Google Gemini API key for AI features
```

Note: Replace placeholder values with your actual configuration. Never commit `.env` files to version control.

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Thanks to all contributors who have helped shape this project
- Special thanks to the open-source community for the amazing tools and libraries
