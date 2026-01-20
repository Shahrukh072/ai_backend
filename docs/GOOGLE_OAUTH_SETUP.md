# Google OAuth Setup Guide - Step by Step

This guide provides detailed step-by-step instructions to set up Google OAuth authentication for the AI Backend application.

## Prerequisites

1. A Google account (Gmail account works fine)
2. Access to [Google Cloud Console](https://console.cloud.google.com/)

---

## Step 1: Create a Google Cloud Project

1. **Go to Google Cloud Console**
   - Open your browser and navigate to: https://console.cloud.google.com/
   - Sign in with your Google account

2. **Create a New Project** (or select existing)
   - Click on the project dropdown at the top of the page (it may show "Select a project" or an existing project name)
   - Click **"NEW PROJECT"** button
   - Enter a project name (e.g., "AI Backend" or "My App")
   - Click **"CREATE"**
   - Wait for the project to be created (usually takes a few seconds)
   - Make sure the new project is selected in the dropdown

---

## Step 2: Configure OAuth Consent Screen

**This step is required before creating OAuth credentials.**

1. **Navigate to OAuth Consent Screen**
   - In the left sidebar, click **"APIs & Services"**
   - Click **"OAuth consent screen"** (under "APIs & Services" section)

2. **Choose User Type**
   - Select **"External"** (unless you have a Google Workspace account)
   - Click **"CREATE"**

3. **Fill in App Information** (Step 1 of 4)
   - **App name**: Enter your app name (e.g., "AI Backend" or "My Application")
   - **User support email**: Select your email from the dropdown
   - **App logo**: (Optional) You can skip this for now
   - **App domain**: (Optional) Leave blank for localhost development
   - **Developer contact information**: Enter your email address
   - Click **"SAVE AND CONTINUE"**

4. **Add Scopes** (Step 2 of 4)
   - Click **"ADD OR REMOVE SCOPES"**
   - In the filter box, search for and select:
     - `.../auth/userinfo.email`
     - `.../auth/userinfo.profile`
     - `openid`
   - Click **"UPDATE"**
   - Click **"SAVE AND CONTINUE"**

5. **Add Test Users** (Step 3 of 4) - **IMPORTANT for Development**
   - Click **"ADD USERS"**
   - Enter your Google email address (the one you'll use to test login)
   - Click **"ADD"**
   - Click **"SAVE AND CONTINUE"**

6. **Summary** (Step 4 of 4)
   - Review the information
   - Click **"BACK TO DASHBOARD"**

**Note**: Your app will be in "Testing" mode initially. This means only test users can sign in. To make it public, you'll need to submit it for verification later.

---

## Step 3: Create OAuth 2.0 Client ID

1. **Navigate to Credentials**
   - In the left sidebar, click **"APIs & Services"**
   - Click **"Credentials"**

2. **Create OAuth Client ID**
   - Click the **"+ CREATE CREDENTIALS"** button at the top
   - Select **"OAuth client ID"** from the dropdown

3. **Configure OAuth Client**
   - **Application type**: Select **"Web application"**
   - **Name**: Enter a name (e.g., "AI Backend Web Client" or "Development Client")

4. **Add Authorized JavaScript origins**
   - Click **"+ ADD URI"** under "Authorized JavaScript origins"
   - Add: `http://localhost:3000`
   - Click **"+ ADD URI"** again
   - Add: `http://localhost:8000` (if your backend runs on port 8000)
   - **Important**: Do NOT include trailing slashes

5. **Add Authorized redirect URIs** (Optional but recommended)
   - Click **"+ ADD URI"** under "Authorized redirect URIs"
   - Add: `http://localhost:3000`
   - Add: `http://localhost:8000` (if needed)
   - **Note**: For this application, redirect URIs are not strictly required since we use ID token flow, but Google recommends adding them

6. **Create the Client**
   - Click **"CREATE"**

7. **Copy Your Credentials** ⚠️ **IMPORTANT**
   - A popup will appear showing:
     - **Your Client ID** (looks like: `123456789-abc123def456.apps.googleusercontent.com`)
     - **Your Client Secret** (looks like: `GOCSPX-abc123def456xyz789`)
   - **Copy both values immediately** - you won't be able to see the Client Secret again!
   - If you lose the Client Secret, you'll need to create a new OAuth client
   - Click **"OK"** to close the popup

8. **View Your Credentials Later** (if needed)
   - You can always see your Client ID in the Credentials page
   - To view or reset the Client Secret, click the edit icon (pencil) next to your OAuth client

---

## Step 4: Enable Required APIs

1. **Navigate to Library**
   - In the left sidebar, click **"APIs & Services"**
   - Click **"Library"**

2. **Enable Google+ API** (if not already enabled)
   - Search for "Google+ API" or "People API"
   - Click on it and click **"ENABLE"**

**Note**: The OAuth 2.0 API is usually enabled automatically, but if you encounter issues, you can enable it from the Library as well.

---

## Step 5: Configure Backend Environment Variables

1. **Create or Edit `.env` file**
   - In your project root directory (`/Users/shahrukhkhan/Downloads/ai_backend/`), create a `.env` file if it doesn't exist
   - Open the `.env` file in a text editor

2. **Add Google OAuth Configuration**
   ```env
   # Google OAuth Configuration
   GOOGLE_OAUTH_CLIENT_ID=your-client-id-here.apps.googleusercontent.com
   GOOGLE_OAUTH_CLIENT_SECRET=your-client-secret-here
   APP_BASE_URL=http://localhost:3000
   ```

3. **Replace the values**:
   - Replace `your-client-id-here.apps.googleusercontent.com` with your actual Client ID from Step 3
   - Replace `your-client-secret-here` with your actual Client Secret from Step 3
   - Keep `APP_BASE_URL=http://localhost:3000` (or change if your frontend runs on a different port)

4. **Save the file**

**Example** (don't use these - they're fake):
```env
GOOGLE_OAUTH_CLIENT_ID=123456789-abc123def456.apps.googleusercontent.com
GOOGLE_OAUTH_CLIENT_SECRET=GOCSPX-abc123def456xyz789
APP_BASE_URL=http://localhost:3000
```

---

## Step 6: Configure Frontend Environment Variables

1. **Navigate to Frontend Directory**
   ```bash
   cd frontend
   ```

2. **Create or Edit `.env` file**
   - Create a `.env` file in the `frontend/` directory if it doesn't exist
   - Open the `.env` file in a text editor

3. **Add Google Client ID**
   ```env
   VITE_GOOGLE_CLIENT_ID=your-client-id-here.apps.googleusercontent.com
   ```

4. **Replace the value**:
   - Replace `your-client-id-here.apps.googleusercontent.com` with your actual Client ID (same one you used in backend)
   - **Important**: Only the Client ID goes here, NOT the Client Secret!

5. **Save the file**

**Example**:
```env
VITE_GOOGLE_CLIENT_ID=123456789-abc123def456.apps.googleusercontent.com
```

---

## Step 7: Restart Your Servers

After adding environment variables, you need to restart both servers:

1. **Restart Backend Server**
   - Stop the backend server (Ctrl+C if running)
   - Start it again:
     ```bash
     uvicorn app.main:app --reload
     ```

2. **Restart Frontend Server**
   - Stop the frontend server (Ctrl+C if running)
   - Navigate to frontend directory:
     ```bash
     cd frontend
     npm run dev
     ```

**Important**: Environment variables are loaded when the server starts, so changes require a restart.

---

## Step 8: Test Google Sign-In

1. **Open Your Application**
   - Navigate to: http://localhost:3000/login

2. **Test Google Sign-In**
   - You should see a "Sign in with Google" button
   - Click the button
   - A Google sign-in popup should appear
   - Sign in with your Google account (the one you added as a test user)
   - You should be redirected back to your app and logged in

3. **If You See Errors**:
   - See the Troubleshooting section below

---

## Quick Reference: What Goes Where

### Backend `.env` file:
```env
GOOGLE_OAUTH_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_OAUTH_CLIENT_SECRET=your-client-secret
APP_BASE_URL=http://localhost:3000
```

### Frontend `.env` file:
```env
VITE_GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
```

**Remember**: 
- Client ID goes in BOTH files
- Client Secret goes ONLY in backend `.env` (never in frontend!)

---

## How It Works (Technical Details)

1. **Frontend**: User clicks "Sign in with Google" button
   - Google Identity Services (GSI) library loads (from CDN in `index.html`)
   - User authenticates with Google in a popup
   - Google returns an ID token to the frontend

2. **Frontend**: Sends ID token to backend
   - Frontend sends the token to `/api/auth/google` (POST request)
   - Token is included in the request body

3. **Backend**: Verifies the token
   - Backend uses Google's token verification API
   - Extracts user information (email, name, Google ID)
   - Creates or finds user in database

4. **Backend**: Returns JWT token
   - Backend creates a JWT access token
   - Returns it to the frontend

5. **Frontend**: Stores token and redirects
   - Frontend stores JWT in localStorage
   - Redirects user to chat page

---

## Dependencies

### Backend Dependencies

The following packages are required (should already be in `requirements.txt`):

```bash
pip install google-auth google-auth-oauthlib google-auth-httplib2
```

Or install all requirements:

```bash
pip install -r requirements.txt
```

### Frontend Dependencies

The Google Identity Services library is loaded via CDN in `frontend/index.html`. No additional npm packages are required.

---

## Database Setup

The User model supports OAuth. If you haven't run migrations yet:

### Option 1: Using Alembic (Recommended)

```bash
# Create migration
alembic revision --autogenerate -m "Add OAuth support to User model"

# Review the migration file, then apply it
alembic upgrade head
```

### Option 2: Manual SQL

```sql
ALTER TABLE users 
  ALTER COLUMN hashed_password DROP NOT NULL,
  ADD COLUMN provider VARCHAR DEFAULT 'email',
  ADD COLUMN google_id VARCHAR UNIQUE;
  
CREATE INDEX IF NOT EXISTS ix_users_google_id ON users(google_id);
```

**Note**: If you're using `init_db.py`, the schema should already include these fields.

## How It Works

1. **Frontend**: User clicks "Sign in with Google" button
2. **Google**: User authenticates with Google and receives an ID token
3. **Frontend**: Sends the ID token to `/api/auth/google`
4. **Backend**: Verifies the token with Google, creates/updates user, returns JWT
5. **Frontend**: Stores JWT and redirects to chat page

---

## Troubleshooting Common Issues

### ❌ Error: "Access blocked: Authorization Error - The OAuth client was not found"

**This is the error you're seeing!** Here's how to fix it:

1. **Check Client ID is correct**
   - Verify your Client ID in backend `.env` matches exactly what's in Google Cloud Console
   - Make sure there are no extra spaces or quotes around the value
   - Client ID should look like: `123456789-abc123def456.apps.googleusercontent.com`

2. **Check Client ID is set in frontend**
   - Verify `VITE_GOOGLE_CLIENT_ID` is set in `frontend/.env`
   - Make sure it matches the backend Client ID exactly

3. **Verify Authorized JavaScript Origins**
   - Go to Google Cloud Console → APIs & Services → Credentials
   - Click on your OAuth 2.0 Client ID
   - Under "Authorized JavaScript origins", make sure you have:
     - `http://localhost:3000` (no trailing slash)
     - `http://localhost:8000` (if needed)
   - Click "SAVE"

4. **Restart both servers** after making changes

5. **Clear browser cache** and try again

---

### ❌ Error: "Google OAuth is not configured"

**Backend error** - The backend can't find the Client ID:

1. **Check backend `.env` file exists**
   ```bash
   ls -la .env
   ```

2. **Verify the variable is set**
   ```bash
   # In your backend directory
   cat .env | grep GOOGLE_OAUTH_CLIENT_ID
   ```
   Should show: `GOOGLE_OAUTH_CLIENT_ID=your-client-id.apps.googleusercontent.com`

3. **Make sure you restarted the backend server** after adding the variable

4. **Check for typos** - Variable name must be exactly: `GOOGLE_OAUTH_CLIENT_ID`

---

### ❌ Error: "Invalid Google token" or "Token verification failed"

1. **Client ID mismatch**
   - Frontend and backend must use the SAME Client ID
   - Check both `.env` files have the same value

2. **Token expired**
   - Google ID tokens expire after 1 hour
   - Try signing in again

3. **OAuth consent screen not configured**
   - Go back to Step 2 and complete the OAuth consent screen setup
   - Make sure you added yourself as a test user

4. **Wrong project selected**
   - Make sure you're using credentials from the correct Google Cloud project

---

### ❌ Google Sign-In Button Not Showing

1. **Check frontend environment variable**
   ```bash
   # In frontend directory
   cat .env | grep VITE_GOOGLE_CLIENT_ID
   ```

2. **Check browser console** (F12 → Console tab)
   - Look for errors related to Google Identity Services
   - Common error: "Failed to load script" means the CDN script isn't loading

3. **Verify Google script is loaded**
   - Open `frontend/index.html`
   - Make sure this line exists:
     ```html
     <script src="https://accounts.google.com/gsi/client" async defer></script>
     ```

4. **Check network tab**
   - Open browser DevTools → Network tab
   - Refresh the page
   - Look for failed requests to `accounts.google.com`

5. **Restart frontend server** after adding environment variable

---

### ❌ Error: "This app isn't verified" or "Unverified app"

**This is normal for development!**

1. **Your app is in "Testing" mode**
   - This is expected for development
   - Only test users (the ones you added in Step 2) can sign in

2. **To allow more users**:
   - Go to Google Cloud Console → APIs & Services → OAuth consent screen
   - Click "PUBLISH APP" (only if you want to make it public)
   - **Warning**: Making it public may require app verification for production use

3. **For development**: Just add yourself and other test users in the OAuth consent screen

---

### ❌ CORS Errors

1. **Check backend CORS configuration**
   - In `app/config.py`, verify `CORS_ORIGINS` includes your frontend URL:
     ```python
     CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]
     ```

2. **Check Google Cloud Console**
   - Verify "Authorized JavaScript origins" includes your frontend URL
   - Must match exactly (including http/https and port)

---

### ❌ Error: "insufficient_quota" (429 Error)

**This is a different issue** - Your OpenAI API quota is exceeded, not Google OAuth:

1. **This is not a Google OAuth problem**
   - The error is from OpenAI API
   - Check your OpenAI account billing and quota

2. **To fix OpenAI quota issue**:
   - Go to https://platform.openai.com/account/billing
   - Add payment method or upgrade your plan
   - Or use a different LLM provider

---

## Verification Checklist

Use this checklist to verify your setup:

- [ ] Google Cloud project created
- [ ] OAuth consent screen configured (all 4 steps completed)
- [ ] Test user added in OAuth consent screen
- [ ] OAuth 2.0 Client ID created
- [ ] Client ID copied (looks like: `xxx.apps.googleusercontent.com`)
- [ ] Client Secret copied (looks like: `GOCSPX-xxx`)
- [ ] Authorized JavaScript origins added: `http://localhost:3000`
- [ ] Backend `.env` file has `GOOGLE_OAUTH_CLIENT_ID`
- [ ] Backend `.env` file has `GOOGLE_OAUTH_CLIENT_SECRET`
- [ ] Backend `.env` file has `APP_BASE_URL=http://localhost:3000`
- [ ] Frontend `.env` file has `VITE_GOOGLE_CLIENT_ID`
- [ ] Both Client IDs match exactly
- [ ] Backend server restarted after adding env variables
- [ ] Frontend server restarted after adding env variables
- [ ] Database has OAuth fields (provider, google_id columns)

---

## Security Best Practices

⚠️ **IMPORTANT SECURITY NOTES**:

1. **Never commit `.env` files to Git**
   - Make sure `.env` is in your `.gitignore` file
   - Client Secret must NEVER be exposed

2. **Client Secret is Backend Only**
   - Client Secret goes ONLY in backend `.env`
   - NEVER put Client Secret in frontend code or `.env`

3. **Use HTTPS in Production**
   - Always use HTTPS (not HTTP) for production
   - Update authorized origins to use `https://` in production

4. **Rotate Credentials Regularly**
   - Periodically regenerate Client Secret
   - Update your `.env` files when rotating

5. **Monitor Usage**
   - Check Google Cloud Console → APIs & Services → Credentials
   - Monitor for unusual activity

6. **Environment Variables**
   - Use different Client IDs for development and production
   - Never use production credentials in development

---

## Production Deployment

When deploying to production:

1. **Create a new OAuth Client** (or use existing)
   - Add production URLs to "Authorized JavaScript origins"
   - Example: `https://yourdomain.com`

2. **Update Environment Variables**
   - Backend: Use production Client ID and Secret
   - Frontend: Use production Client ID
   - Update `APP_BASE_URL` to production URL

3. **OAuth Consent Screen**
   - Complete app verification if required
   - Add production domain
   - Update privacy policy and terms of service URLs

4. **Security**
   - Use HTTPS everywhere
   - Enable security headers
   - Monitor for suspicious activity

