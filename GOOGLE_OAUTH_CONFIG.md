# Google OAuth Configuration Summary

## ✅ Configuration Status

### Backend `.env` File
```
GOOGLE_OAUTH_CLIENT_ID=32570507647-bcdiqregmfisvvaf8r2pmhe48g51tos7.apps.googleusercontent.com
GOOGLE_OAUTH_CLIENT_SECRET=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
APP_BASE_URL=http://localhost:3000
```

### Frontend `.env` File
```
VITE_GOOGLE_CLIENT_ID=32570507647-bcdiqregmfisvvaf8r2pmhe48g51tos7.apps.googleusercontent.com
```

---

## 🔧 Google Cloud Console Configuration Required

**Important**: Add these URLs to your Google Cloud Console OAuth client:

### Authorized JavaScript Origins
Add these in Google Cloud Console → APIs & Services → Credentials → Your OAuth Client:
- `http://localhost:3000`
- `http://localhost:8000` (if your backend runs on port 8000)

### Authorized Redirect URIs (Optional but Recommended)
Add these for proper configuration (even though current ID token flow doesn't use them):
- `http://localhost:3000/api/auth/google/callback`
- `http://localhost:8000/api/auth/google/callback`

**For Production** (when deploying):
- `https://yourdomain.com/api/auth/google/callback`

---

## 📝 How It Works

1. **Frontend**: User clicks "Sign in with Google" button
   - Google Identity Services (GSI) authenticates user
   - Returns ID token to frontend

2. **Frontend**: Sends ID token to backend
   - POST request to `/api/auth/google`
   - Token in request body: `{ "token": "google_id_token" }`

3. **Backend**: Verifies token and creates/updates user
   - Verifies ID token with Google
   - Creates or finds user in database
   - Returns JWT access token

4. **Frontend**: Stores JWT and redirects
   - Stores JWT in localStorage
   - Redirects to chat page

---

## 🚀 Testing

1. **Restart both servers** after adding environment variables:
   ```bash
   # Backend
   uvicorn app.main:app --reload

   # Frontend (in separate terminal)
   cd frontend
   npm run dev
   ```

2. **Test Google Sign-In**:
   - Navigate to: http://localhost:3000/login
   - Click "Sign in with Google" button
   - Sign in with your Google account (must be added as test user in Google Cloud Console)
   - You should be redirected to the chat page upon successful login

---

## 🔍 Current Implementation

### Backend Endpoint
- **URL**: `POST /api/auth/google`
- **Location**: `app/api/routes/auth.py` (line 73)
- **Service**: `app/services/oauth_service.py`

### Frontend Integration
- **Component**: `frontend/src/pages/Login.jsx`
- **Service**: `frontend/src/services/authService.js`
- **Method**: `loginWithGoogle(googleToken)`

### OAuth Service Logic
The OAuth service (`app/services/oauth_service.py`) handles:
1. Token verification with Google
2. User lookup/creation
3. JWT token generation
4. User data sanitization

---

## ⚠️ Important Notes

1. **Callback URLs**: The callback URLs you mentioned are for Google Cloud Console configuration, not for backend code. The current implementation uses ID token flow (not authorization code flow), so no callback endpoint is needed in the code.

2. **Test Users**: Make sure your Google account is added as a test user in Google Cloud Console → OAuth consent screen → Test users.

3. **Environment Variables**: Both backend and frontend servers must be restarted after adding/modifying `.env` files.

4. **Client Secret**: Never expose the Client Secret in frontend code. It should ONLY be in backend `.env` file.

---

## 🐛 Troubleshooting

### "OAuth client was not found" Error
- Verify Client ID is correct in both backend and frontend `.env` files
- Make sure you added `http://localhost:3000` to "Authorized JavaScript origins" in Google Cloud Console
- Restart both servers after configuration changes

### Button not showing
- Check that `VITE_GOOGLE_CLIENT_ID` is set in `frontend/.env`
- Restart frontend server
- Check browser console for errors

### "Invalid Google token" Error
- Verify Client ID matches between frontend and backend
- Make sure your Google account is added as a test user in OAuth consent screen
- Check that token hasn't expired (ID tokens expire after 1 hour)

---

## 📚 Full Documentation

For detailed step-by-step setup instructions, see: [docs/GOOGLE_OAUTH_SETUP.md](docs/GOOGLE_OAUTH_SETUP.md)
