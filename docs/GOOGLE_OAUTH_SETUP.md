# Google OAuth Setup Guide

This guide explains how to set up Google OAuth authentication for the AI Backend application.

## Prerequisites

1. A Google Cloud Platform (GCP) account
2. A GCP project with the Google OAuth 2.0 API enabled

## Step 1: Create OAuth 2.0 Credentials

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Select your project or create a new one
3. Navigate to **APIs & Services** > **Credentials**
4. Click **Create Credentials** > **OAuth client ID**
5. If prompted, configure the OAuth consent screen:
   - Choose **External** user type (unless you have a Google Workspace)
   - Fill in the required information (App name, User support email, Developer contact)
   - Add scopes: `email`, `profile`, `openid`
   - Add test users if your app is in testing mode
6. For the OAuth client:
   - Application type: **Web application**
   - Name: **AI Backend**
   - Authorized JavaScript origins:
     - `http://localhost:3000`
     - `http://localhost:8000`
     - (Add your production URLs when deploying)
   - Authorized redirect URIs:
     - `http://localhost:3000/api/auth/google` (backend callback endpoint)
     - `http://localhost:8000/api/auth/google` (if using different backend port)
     - (Add your production callback URLs, e.g., `https://yourdomain.com/api/auth/google`)
7. Click **Create**
8. Copy the **Client ID** and **Client Secret**

## Step 2: Configure Backend

Add the following environment variables to your `.env` file:

```env
GOOGLE_OAUTH_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_OAUTH_CLIENT_SECRET=your-client-secret
GOOGLE_OAUTH_REDIRECT_URI=http://localhost:3000/api/auth/google
```

Or update `app/config.py` directly (not recommended for production).

## Step 3: Configure Frontend

Add the following environment variable to your frontend `.env` file:

```env
VITE_GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
```

## Step 4: Install Dependencies

### Backend

```bash
pip install google-auth google-auth-oauthlib google-auth-httplib2
```

Or install all requirements:

```bash
pip install -r requirements.txt
```

### Frontend

The Google Identity Services library is loaded via CDN in `index.html`. No additional npm packages are required.

## Step 5: Database Migration

The User model has been updated to support OAuth. You need to create and run a migration:

```bash
# Create migration
alembic revision --autogenerate -m "Add OAuth support to User model"

# Review the migration file, then apply it
alembic upgrade head
```

Or manually update your database:

```sql
ALTER TABLE users 
  ALTER COLUMN hashed_password DROP NOT NULL,
  ADD COLUMN provider VARCHAR DEFAULT 'email',
  ADD COLUMN google_id VARCHAR UNIQUE;
  
CREATE INDEX IF NOT EXISTS ix_users_google_id ON users(google_id);
```

## Step 6: Test the Integration

1. Start the backend server:
   ```bash
   uvicorn app.main:app --reload
   ```

2. Start the frontend:
   ```bash
   cd frontend
   npm run dev
   ```

3. Navigate to `http://localhost:3000/login` or `http://localhost:3000/register`
4. Click the "Sign in with Google" button
5. Complete the Google sign-in flow
6. You should be redirected to the chat page upon successful authentication

## How It Works

1. **Frontend**: User clicks "Sign in with Google" button
2. **Google**: User authenticates with Google and receives an ID token
3. **Frontend**: Sends the ID token to `/api/auth/google`
4. **Backend**: Verifies the token with Google, creates/updates user, returns JWT
5. **Frontend**: Stores JWT and redirects to chat page

## Security Notes

- Never expose your Client Secret in frontend code
- Always use HTTPS in production
- Keep your Client Secret secure and never commit it to version control
- Regularly rotate your OAuth credentials
- Monitor OAuth usage in Google Cloud Console

## Troubleshooting

### "Google OAuth is not configured"
- Make sure `GOOGLE_OAUTH_CLIENT_ID` is set in your backend `.env` file

### "Invalid Google token"
- Check that the Client ID matches between frontend and backend
- Verify the token hasn't expired
- Ensure the OAuth consent screen is properly configured

### Button not showing
- Check that `VITE_GOOGLE_CLIENT_ID` is set in frontend `.env`
- Verify the Google Identity Services script is loaded (check browser console)
- Make sure the Client ID is correct

### CORS errors
- Add your frontend URL to `CORS_ORIGINS` in backend config
- Verify authorized JavaScript origins in Google Cloud Console

