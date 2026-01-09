# AI Backend Frontend

React frontend application for the AI Backend platform with chat, document upload, and authentication features.

## Features

- 🔐 User authentication (Login/Register)
- 🔑 Google OAuth login and signup
- 💬 Real-time chat interface with AI agent
- 📄 Document upload and management
- 🎨 Modern, responsive UI with Tailwind CSS
- 🔒 Protected routes
- 📱 Mobile-friendly design

## Getting Started

### Prerequisites

- Node.js 18+ and npm/yarn
- Backend API running on http://localhost:8000

### Installation

1. Install dependencies:
```bash
npm install
```

2. Create a `.env` file:
```env
VITE_API_URL=http://localhost:8000
VITE_GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com
```

3. Start the development server:
```bash
npm run dev
```

The application will be available at http://localhost:3000

### Google OAuth Setup

To enable Google OAuth login/signup:

1. Create OAuth 2.0 credentials in [Google Cloud Console](https://console.cloud.google.com/)
2. Add your Client ID to the `.env` file as `VITE_GOOGLE_CLIENT_ID`
3. Configure authorized JavaScript origins and redirect URIs in Google Cloud Console
4. See [GOOGLE_OAUTH_SETUP.md](../docs/GOOGLE_OAUTH_SETUP.md) for detailed instructions

### Building for Production

```bash
npm run build
```

The built files will be in the `dist` directory.

## Project Structure

```
src/
├── components/       # Reusable components
├── context/         # React context (Auth)
├── pages/           # Page components
│   ├── Login.jsx
│   ├── Register.jsx
│   ├── Chat.jsx
│   └── Upload.jsx
├── services/        # API service layer
│   ├── api.js
│   ├── authService.js
│   ├── chatService.js
│   └── documentService.js
├── utils/           # Utility functions
│   └── googleAuth.js
├── App.jsx          # Main app component
└── main.jsx         # Entry point
```

## API Integration

The frontend communicates with the backend API at:
- `/api/auth/*` - Authentication endpoints (including `/api/auth/google` for OAuth)
- `/api/chat/*` - Chat endpoints
- `/api/rag/*` - Document/RAG endpoints

All API requests include authentication tokens in the Authorization header.

## Features in Detail

### Authentication
- Secure login and registration
- Google OAuth login/signup
- JWT token-based authentication
- Automatic token refresh
- Protected routes

### Chat Interface
- Real-time messaging with AI agent
- Document-specific conversations
- Streaming responses
- Chat history

### Document Management
- Upload PDF, TXT, DOCX, MD files
- View all uploaded documents
- Delete documents
- Document-specific chat filtering
