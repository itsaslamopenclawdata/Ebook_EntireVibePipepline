# User Inputs & Configuration Guide
**Vibe PDF Book Generation Platform**

**Date:** February 25, 2026
**Repository:** https://github.com/itsaslamopenclawdata/Ebook_EntireVibePipepline
**Reference:** [Next_steps_25022026.md](https://github.com/itsaslamopenclawdata/Ebook_EntireVibePipepline/blob/main/Next_steps_25022026.md)

---

## Overview

This document outlines all the **API keys, authorizations, credentials, and configuration** you need to provide to complete the implementation of the Vibe PDF Book Generation Platform.

Please follow each section carefully, acquire the required inputs, and **fill in this document with your actual values**. Once complete, share this file with me and I'll configure the system accordingly.

---

## 📋 Required Inputs Summary

| Category | Item | Priority | Cost | Difficulty |
|----------|------|----------|------|------------|
| 🔐 Application Security | JWT Secret Key | 🔴 CRITICAL | Free | Easy |
| 🗄️ Database | PostgreSQL Credentials | 🔴 CRITICAL | Free/$ | Medium |
| ⚡ Cache/Queue | Redis Credentials | 🔴 CRITICAL | Free/$ | Easy |
| 🔑 LLM Providers | Anthropic API Key | 🟠 HIGH | $ | Easy |
| 🔑 LLM Providers | OpenAI API Key | 🟠 HIGH | $ | Easy |
| 🔑 LLM Providers | Google AI API Key | 🟠 HIGH | Free/$ | Easy |
| 🔐 Google OAuth | OAuth Client ID | 🟠 HIGH | Free | Medium |
| 🔐 Google OAuth | OAuth Client Secret | 🟠 HIGH | Free | Medium |
| ☁️ Google Services | Service Account JSON | 🟠 HIGH | Free | Medium |
| ☁️ Google Drive | Drive Folder ID | 🟠 HIGH | Free | Easy |
| 🐳 Deployment | Docker Registry | 🟡 MEDIUM | Free/$ | Medium |
| 🌐 Domain | Production Domain | 🟡 MEDIUM | $ | Easy |
| 📊 Monitoring | Sentry DSN | 🟢 OPTIONAL | Free/$ | Easy |
| 📊 Monitoring | Cloud Provider | 🟢 OPTIONAL | $ | Medium |

---

## 📝 Configuration Template

**Copy this section, fill in your values, and save it:**

```yaml
# ========================================
# VIBE PDF PLATFORM - CONFIGURATION
# ========================================
# Fill in ALL required values marked with [REQUIRED]

# --- APPLICATION SECURITY [REQUIRED] ---
APP_ENV: production
DEBUG: "false"
SECRET_KEY: "[REQUIRED - Generate a secure random string]"
FRONTEND_URL: "https://your-domain.com"

# --- DATABASE [REQUIRED] ---
DATABASE_URL: "[REQUIRED - PostgreSQL connection string]"
DB_HOST: "[REQUIRED - e.g., localhost or prod-db-host]"
DB_PORT: "5432"
DB_NAME: "vibepdf"
DB_USER: "vibepdf"
DB_PASSWORD: "[REQUIRED - Database password]"

# --- REDIS [REQUIRED] ---
REDIS_URL: "[REQUIRED - Redis connection string]"
REDIS_HOST: "[REQUIRED - e.g., localhost or prod-redis-host]"
REDIS_PORT: "6379"
REDIS_PASSWORD: "[OPTIONAL - Redis password if set]"

# --- LLM PROVIDERS [AT LEAST ONE REQUIRED] ---
ANTHROPIC_API_KEY: "[REQUIRED - from https://console.anthropic.com]"
OPENAI_API_KEY: "[OPTIONAL - from https://platform.openai.com/api-keys]"
GOOGLE_AI_API_KEY: "[OPTIONAL - from https://aistudio.google.com/app/apikey]"
LLM_PROVIDER_PRIORITY: "anthropic,openai,google"

# --- GOOGLE OAUTH [REQUIRED] ---
GOOGLE_OAUTH_CLIENT_ID: "[REQUIRED - from Google Cloud Console]"
GOOGLE_OAUTH_CLIENT_SECRET: "[REQUIRED - from Google Cloud Console]"
GOOGLE_OAUTH_REDIRECT_URI: "[REQUIRED - https://your-api-domain.com/api/v1/auth/google/callback]"

# --- GOOGLE SERVICES [REQUIRED] ---
GOOGLE_CREDENTIALS_PATH: "/app/credentials/google-service-account.json"
GOOGLE_SERVICE_ACCOUNT_JSON: "[REQUIRED - Service account JSON content - see below]"
GOOGLE_DRIVE_FOLDER_ID: "[REQUIRED - Google Drive folder ID for PDFs]"

# --- CORS CONFIGURATION [REQUIRED] ---
CORS_ORIGINS: "[REQUIRED - Comma-separated frontend domains]"
# Example: https://vibepdf.com,https://www.vibepdf.com,http://localhost:3000

# --- RATE LIMITING [REQUIRED] ---
RATE_LIMIT_ENABLED: "true"
RATE_LIMIT_REQUESTS: "100"
RATE_LIMIT_PERIOD: "60"

# --- MONITORING [OPTIONAL] ---
SENTRY_DSN: "[OPTIONAL - Sentry DSN for error tracking]"
PROMETHEUS_ENABLED: "true"
LOG_LEVEL: "info"

# --- DEPLOYMENT [REQUIRED FOR PRODUCTION] ---
DOCKER_REGISTRY: "[REQUIRED - e.g., Docker Hub, AWS ECR, GCR]"
DOCKER_REGISTRY_USERNAME: "[REQUIRED - Registry username]"
DOCKER_REGISTRY_PASSWORD: "[REQUIRED - Registry password/token]"
PRODUCTION_DOMAIN: "[REQUIRED - Production domain]"
API_DOMAIN: "[REQUIRED - API domain or subdomain]"
```

---

## 🔐 SECTION 1: Application Security

### 1.1 JWT Secret Key [REQUIRED]

**Purpose:** Used to sign and verify JWT tokens for user authentication.

**How to Generate:**

#### Option A: Using Python
```bash
# Generate a secure random string
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

#### Option B: Using OpenSSL
```bash
# Generate 64-character random string
openssl rand -base64 64
```

#### Option C: Using Online Generator
Visit: https://www.uuidgenerator.net/guid or use any secure password generator to create a 64+ character random string.

**Your JWT Secret Key:**
```
[ADD YOUR SECRET KEY HERE - 64+ characters, random string]
```

---

#### Option B: Using OpenSSL
```bash
# Generate 64-character random string
openssl rand -base64 64
```

**Your JWT Secret Key:**
```
[ADD YOUR SECRET KEY HERE]
```

---

### 1.2 Frontend URL

**Purpose:** Used for CORS configuration and OAuth redirect URIs.

**Your Frontend URL:**
```
[ADD YOUR FRONTEND URL HERE - e.g., https://vibepdf.com or http://localhost:3000 for dev]
```

---

## 🗄️ SECTION 2: Database Configuration

### 2.1 PostgreSQL Database [REQUIRED]

**Purpose:** Primary database for users, books, chapters, and generation tasks.

---

#### Option A: Local Development (Docker)

**Cost:** FREE
**Setup Time:** 5 minutes

**Steps:**

1. **Using Docker Compose (Recommended)**
   Add this to your `docker-compose.yml`:
   ```yaml
   postgres:
     image: postgres:15-alpine
     environment:
       POSTGRES_DB: vibepdf
       POSTGRES_USER: vibepdf
       POSTGRES_PASSWORD: your-secure-password-here
     volumes:
       - postgres_data:/var/lib/postgresql/data
     ports:
       - "5432:5432"
   ```

2. **Start PostgreSQL:**
   ```bash
   docker-compose up -d postgres
   ```

3. **Your Database URL:**
   ```
   postgresql+asyncpg://vibepdf:your-secure-password-here@localhost:5432/vibepdf
   ```

**Your Local Database Configuration:**
```yaml
DB_HOST: localhost
DB_PORT: "5432"
DB_NAME: vibepdf
DB_USER: vibepdf
DB_PASSWORD: [SET YOUR PASSWORD]
DATABASE_URL: postgresql+asyncpg://vibepdf:[YOUR-PASSWORD]@localhost:5432/vibepdf
```

---

#### Option B: Cloud PostgreSQL (Production)

**Recommended Providers:**

1. **Supabase (Free Tier Available)**
   - Website: https://supabase.com
   - Cost: Free tier (500MB), then $25/month
   - Setup Time: 10 minutes

   **Steps:**
   1. Go to https://supabase.com and sign up/login
   2. Click "New Project"
   3. Set project name: `vibe-pdf-platform`
   4. Set database password: **[Generate secure password]**
   5. Wait for project to be provisioned
   6. Go to Settings → Database
   7. Copy the connection string

   **Your Supabase Configuration:**
   ```yaml
   DB_HOST: [From Supabase project URL - e.g., db.xxxxxxxx.supabase.co]
   DB_PORT: "5432"
   DB_NAME: postgres
   DB_USER: postgres
   DB_PASSWORD: [Your database password]
   DATABASE_URL: postgresql+asyncpg://postgres:[YOUR-PASSWORD]@[YOUR-HOST]:5432/postgres
   ```

2. **Neon (Serverless PostgreSQL)**
   - Website: https://neon.tech
   - Cost: Free tier (0.5GB), then from $19/month
   - Setup Time: 5 minutes

   **Steps:**
   1. Go to https://neon.tech and sign up
   2. Click "Create Project"
   3. Set project name: `vibe-pdf-platform`
   4. Copy the connection string from dashboard

3. **AWS RDS (Enterprise)**
   - Website: https://aws.amazon.com/rds/
   - Cost: From $15/month
   - Setup Time: 30 minutes

4. **Google Cloud SQL (Enterprise)**
   - Website: https://cloud.google.com/sql
   - Cost: From $15/month
   - Setup Time: 30 minutes

**Your Production Database Configuration:**
```yaml
DB_HOST: [YOUR-DB-HOST]
DB_PORT: "5432"
DB_NAME: [YOUR-DB-NAME]
DB_USER: [YOUR-DB-USER]
DB_PASSWORD: [YOUR-DB-PASSWORD]
DATABASE_URL: postgresql+asyncpg://[USER]:[PASSWORD]@[HOST]:5432/[NAME]
```

---

### 2.2 Database Backup Password (Optional but Recommended)

**Purpose:** Encrypt database backups.

**Generate using:**
```bash
openssl rand -base64 32
```

**Your Backup Encryption Key:**
```
[ADD YOUR BACKUP KEY HERE]
```

---

## ⚡ SECTION 3: Redis Configuration

### 3.1 Redis [REQUIRED]

**Purpose:** Cache and message broker for Celery background tasks.

---

#### Option A: Local Development (Docker)

**Cost:** FREE
**Setup Time:** 2 minutes

**Steps:**

Add to `docker-compose.yml`:
```yaml
redis:
  image: redis:7-alpine
  volumes:
    - redis_data:/data
  ports:
    - "6379:6379"
```

**Start Redis:**
```bash
docker-compose up -d redis
```

**Your Local Redis Configuration:**
```yaml
REDIS_HOST: localhost
REDIS_PORT: "6379"
REDIS_PASSWORD: ""
REDIS_URL: redis://localhost:6379/0
```

---

#### Option B: Cloud Redis (Production)

**Recommended Providers:**

1. **Redis Cloud (Free Tier)**
   - Website: https://redis.com/try-free/
   - Cost: Free (30MB), then from $7/month
   - Setup Time: 5 minutes

   **Steps:**
   1. Go to https://redis.com/try-free/ and sign up
   2. Create a free database
   3. Copy the connection string

2. **Upstash (Serverless Redis)**
   - Website: https://upstash.com
   - Cost: Free tier (10,000 commands/day)
   - Setup Time: 2 minutes

   **Steps:**
   1. Go to https://upstash.com and sign up
   2. Create a new Redis database
   3. Copy the connection string

3. **ElastiCache (AWS)**
   - Website: https://aws.amazon.com/elasticache/
   - Cost: From $17/month
   - Setup Time: 30 minutes

**Your Production Redis Configuration:**
```yaml
REDIS_HOST: [YOUR-REDIS-HOST]
REDIS_PORT: "[YOUR-REDIS-PORT]"
REDIS_PASSWORD: [YOUR-REDIS-PASSWORD]
REDIS_URL: redis://default:[PASSWORD]@[HOST]:[PORT]/0
```

---

## 🔑 SECTION 4: LLM Provider API Keys

**IMPORTANT:** You need at least **ONE** LLM provider configured. Having multiple provides fallback options.

---

### 4.1 Anthropic Claude API [RECOMMENDED]

**Purpose:** Primary LLM for content generation (best for long-form content).

**Cost:**
- Claude Haiku: $0.25/1M input tokens, $1.25/1M output tokens
- Claude Sonnet: $3/1M input tokens, $15/1M output tokens
- Claude Opus: $15/1M input tokens, $75/1M output tokens

**Setup Steps:**

1. **Go to Anthropic Console:**
   https://console.anthropic.com/

2. **Create Account:**
   - Click "Get API Key"
   - Sign up with email or Google
   - Verify email address

3. **Generate API Key:**
   - Go to "API Keys" section
   - Click "Create Key"
   - Give it a name: "Vibe PDF Platform"
   - Copy the API key immediately (shown only once!)

4. **Add Billing:**
   - Go to "Billing" section
   - Add credit card
   - Set spending limit (recommended: $50-$100/month initially)

5. **Set Usage Limits:**
   - Go to "Usage" section
   - Set daily/monthly limits to prevent overage

**Your Anthropic API Key:**
```
sk-ant-[YOUR-ANTHROPIC-API-KEY-HERE]
```

**Example:** `sk-ant-api03-1234567890abcdef1234567890abcdef`

---

### 4.2 OpenAI GPT API [OPTIONAL]

**Purpose:** Alternative LLM provider (fallback option).

**Cost:**
- GPT-4o: $5/1M input tokens, $15/1M output tokens
- GPT-4o-mini: $0.15/1M input tokens, $0.60/1M output tokens
- GPT-3.5 Turbo: $0.50/1M input tokens, $1.50/1M output tokens

**Setup Steps:**

1. **Go to OpenAI Platform:**
   https://platform.openai.com/

2. **Create Account:**
   - Sign up with email or Google
   - Verify email address
   - Add phone number for verification

3. **Generate API Key:**
   - Go to "API Keys" section
   - Click "Create new secret key"
   - Give it a name: "Vibe PDF Platform"
   - Copy the API key

4. **Add Billing:**
   - Go to "Billing" section
   - Add credit card
   - Set up payment method

**Your OpenAI API Key:**
```
sk-[YOUR-OPENAI-API-KEY-HERE]
```

**Example:** `sk-proj-1234567890abcdefghijklmnopqrstuvwxyz`

---

### 4.3 Google Gemini API [OPTIONAL]

**Purpose:** Alternative LLM provider with Google's language models.

**Cost:**
- Gemini Pro: FREE tier (15 requests/minute), then paid pricing available
- Gemini Ultra: Pricing varies

**Setup Steps:**

1. **Go to Google AI Studio:**
   https://aistudio.google.com/app/apikey

2. **Create Project:**
   - Click "Create API key"
   - Sign in with Google account
   - Create a new project or select existing

3. **Generate API Key:**
   - Click "Create API key in new project"
   - Or select existing project and create key
   - Copy the API key

4. **Enable APIs:**
   - Go to Google Cloud Console
   - Enable "Generative Language API"
   - Enable API if not already enabled

**Your Google AI API Key:**
```
AIza[YOUR-GOOGLE-API-KEY-HERE]
```

**Example:** `AIzaSyAbCdEfGhIjKlMnOpQrStUvWxYz1234567890`

---

### 4.4 LLM Provider Priority Configuration

**Which provider should be used first?** (List in order of preference)

**Example:** `anthropic,openai,google` will try Anthropic first, fallback to OpenAI, then Google.

**Your LLM Provider Priority:**
```
anthropic,openai,google
```

---

## 🔐 SECTION 5: Google OAuth 2.0 [REQUIRED]

**Purpose:** Allow users to sign in with their Google account.

---

### 5.1 Create Google Cloud Project

**Setup Time:** 20 minutes
**Cost:** FREE

**Steps:**

1. **Go to Google Cloud Console:**
   https://console.cloud.google.com/

2. **Create New Project:**
   - Click project selector (top-left)
   - Click "NEW PROJECT"
   - Project name: `Vibe PDF Platform`
   - Click "CREATE"
   - Wait for project to be created (1-2 minutes)

3. **Select the Project:**
   - Click project selector again
   - Select "Vibe PDF Platform"

---

### 5.2 Enable Required APIs

**Required APIs:**
- Google+ API (or People API)
- Google Drive API

**Steps:**

1. **Go to APIs & Services → Library:**
   https://console.cloud.google.com/apis/library

2. **Search and Enable APIs:**
   - Search for "Google+ API" (deprecated, but still needed)
   - Click on it and click "ENABLE"
   - Search for "People API"
   - Click on it and click "ENABLE"
   - Search for "Google Drive API"
   - Click on it and click "ENABLE"

---

### 5.3 Configure OAuth Consent Screen

**Purpose:** Configure what information the app will request from users.

**Steps:**

1. **Go to APIs & Services → OAuth consent screen:**
   https://console.cloud.google.com/apis/credentials/consent

2. **Choose User Type:**
   - Select "External" (for public app)
   - Click "CREATE"

3. **Fill in App Information:**
   - App name: `Vibe PDF Platform`
   - User support email: [Your email]
   - App logo: [Optional - upload later]
   - Authorized domains: [Your frontend domain, e.g., vibepdf.com]
   - Developer contact information: [Your email]
   - Click "SAVE AND CONTINUE"

4. **Scopes (OAuth Scopes):**
   - Click "ADD OR REMOVE SCOPES"
   - Add these scopes:
     - `https://www.googleapis.com/auth/userinfo.email`
     - `https://www.googleapis.com/auth/userinfo.profile`
     - `https://www.googleapis.com/auth/drive.file`
   - Click "UPDATE"
   - Click "SAVE AND CONTINUE"

5. **Test Users:**
   - Add your email as a test user (required before public launch)
   - Click "ADD USERS"
   - Enter your email address
   - Click "ADD"
   - Click "SAVE AND CONTINUE"

6. **Summary:**
   - Review all settings
   - Click "BACK TO DASHBOARD"

---

### 5.4 Create OAuth 2.0 Credentials

**Steps:**

1. **Go to APIs & Services → Credentials:**
   https://console.cloud.google.com/apis/credentials

2. **Create OAuth Client ID:**
   - Click "CREATE CREDENTIALS" → "OAuth client ID"
   - Application type: "Web application"
   - Name: `Vibe PDF Platform Web Client`

3. **Configure Authorized Redirect URIs:**
   - Click "ADD URI" under "Authorized redirect URIs"
   - Add your callback URL:
     ```
     https://your-api-domain.com/api/v1/auth/google/callback
     ```
     For local development:
     ```
     http://localhost:8000/api/v1/auth/google/callback
     ```
   - Click "CREATE"

4. **Copy Credentials:**
   - **Copy the Client ID** (shown in modal)
   - **Copy the Client Secret** (shown in modal - copy immediately, shown only once!)

5. **Save Credentials Safely:**
   - Save Client ID and Secret in a secure password manager
   - Never commit these to version control!

**Your Google OAuth Configuration:**
```yaml
GOOGLE_OAUTH_CLIENT_ID: [YOUR-OAUTH-CLIENT-ID]
GOOGLE_OAUTH_CLIENT_SECRET: [YOUR-OAUTH-CLIENT-SECRET]
GOOGLE_OAUTH_REDIRECT_URI: https://your-api-domain.com/api/v1/auth/google/callback
```

**Example Client ID:**
```
1234567890-abcdefghijklmnopqrstuvwxyz.apps.googleusercontent.com
```

---

## ☁️ SECTION 6: Google Cloud Services

### 6.1 Google Drive Service Account [REQUIRED]

**Purpose:** Server-side authentication for uploading PDFs to Google Drive.

---

#### 6.1.1 Create Service Account

**Setup Time:** 15 minutes
**Cost:** FREE

**Steps:**

1. **Go to IAM & Admin → Service Accounts:**
   https://console.cloud.google.com/iam-admin/serviceaccounts

2. **Create Service Account:**
   - Click "CREATE SERVICE ACCOUNT"
   - Service account name: `vibe-pdf-platform`
   - Service account description: `Service account for Vibe PDF Platform`
   - Click "CREATE AND CONTINUE"

3. **Grant Access (Optional):**
   - Skip for now (we'll grant Drive access separately)
   - Click "DONE"

---

#### 6.1.2 Grant Drive Access to Service Account

**Steps:**

1. **Create Google Drive Folder:**
   - Go to https://drive.google.com
   - Click "New" → "Folder"
   - Folder name: `Vibe PDF Books`
   - Click "CREATE"

2. **Share Folder with Service Account:**
   - Right-click on "Vibe PDF Books" folder
   - Click "Share"
   - In "Add people and groups", paste the service account email:
     ```
     vibe-pdf-platform@your-project-id.iam.gserviceaccount.com
     ```
   - Select role: "Editor"
   - Click "Send"

3. **Get Folder ID:**
   - Open the "Vibe PDF Books" folder
   - Copy the folder ID from the URL:
     ```
     https://drive.google.com/drive/folders/[FOLDER-ID-HERE]
     ```
   - The folder ID is the part after `/folders/`

**Your Google Drive Configuration:**
```yaml
GOOGLE_DRIVE_FOLDER_ID: [YOUR-FOLDER-ID]
```

**Example Folder ID:** `1A2b3C4d5E6f7G8h9I0jK`

---

#### 6.1.3 Create Service Account Key

**Steps:**

1. **Go to Service Accounts:**
   https://console.cloud.google.com/iam-admin/serviceaccounts

2. **Select Service Account:**
   - Click on "vibe-pdf-platform" service account

3. **Create Key:**
   - Go to "Keys" tab
   - Click "ADD KEY" → "Create new key"
   - Key type: "JSON"
   - Click "CREATE"

4. **Download JSON File:**
   - The JSON file will be downloaded automatically
   - Rename it to: `google-service-account.json`
   - **Store this file securely!** Never commit to Git!

5. **Copy JSON Content:**
   - Open the downloaded JSON file
   - Copy the entire content (including all brackets and quotes)

**Your Google Service Account JSON (Copy entire content):**
```json
{
  "type": "service_account",
  "project_id": "[YOUR-PROJECT-ID]",
  "private_key_id": "[YOUR-KEY-ID]",
  "private_key": "-----BEGIN PRIVATE KEY-----\n[YOUR-PRIVATE-KEY]\n-----END PRIVATE KEY-----\n",
  "client_email": "[YOUR-SERVICE-ACCOUNT-EMAIL]",
  "client_id": "[YOUR-CLIENT-ID]",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/[YOUR-SERVICE-ACCOUNT-EMAIL]"
}
```

**⚠️ SECURITY WARNING:** This JSON file contains sensitive credentials. Store it securely and never share it publicly!

---

### 6.2 Google Cloud Storage (Optional Alternative to Drive)

**Purpose:** Alternative storage solution for PDFs.

**Setup Steps:**

1. **Go to Cloud Storage:**
   https://console.cloud.google.com/storage

2. **Create Bucket:**
   - Click "CREATE BUCKET"
   - Bucket name: `vibe-pdf-books` (must be globally unique)
   - Location: Choose region closest to your users
   - Storage class: Standard
   - Access control: Uniform
   - Click "CREATE"

3. **Grant Access:**
   - Go to bucket permissions
   - Add your service account as "Storage Admin"
   - Optionally, make bucket public for PDF access

---

## 🌐 SECTION 7: Domain Configuration

### 7.1 Production Domain [REQUIRED FOR PRODUCTION]

**Purpose:** Frontend URL for users to access the application.

**Recommended Domains:**

1. **Register Domain:**
   - Namecheap: https://www.namecheap.com
   - GoDaddy: https://www.godaddy.com
   - Cloudflare Registrar: https://www.cloudflare.com/products/registrar/

2. **Choose Domain Name:**
   - Examples: `vibepdf.com`, `ebookgenerator.io`, `bookmaker.app`

**Your Production Domain:**
```
[ADD YOUR DOMAIN HERE - e.g., vibepdf.com]
```

---

### 7.2 API Subdomain (Optional but Recommended)

**Purpose:** Separate subdomain for API to simplify CORS configuration.

**Example:**
- Frontend: `https://vibepdf.com`
- API: `https://api.vibepdf.com`

**Your API Domain:**
```
[ADD YOUR API DOMAIN HERE - e.g., api.vibepdf.com or leave empty if using same domain]
```

---

### 7.3 DNS Configuration

**Required DNS Records:**

| Type | Name | Value | Purpose |
|------|------|-------|---------|
| A | @ | [Your server IP] | Frontend domain |
| A | api | [Your server IP] | API subdomain |
| CNAME | www | vibepdf.com | www redirect |

---

## 🐳 SECTION 8: Docker Registry

### 8.1 Docker Registry Account [REQUIRED FOR PRODUCTION]

**Purpose:** Store and deploy Docker images.

**Recommended Registries:**

1. **Docker Hub (Free)**
   - Website: https://hub.docker.com
   - Cost: Free for public repos, $7/month for private
   - Setup Time: 5 minutes

   **Steps:**
   1. Go to https://hub.docker.com
   2. Sign up for account
   3. Go to Account Settings → Security
   4. Generate Access Token (for CI/CD)
   5. Copy the username and access token

2. **AWS ECR (Enterprise)**
   - Website: https://aws.amazon.com/ecr/
   - Cost: First 500GB/month free storage
   - Setup Time: 30 minutes

3. **Google Container Registry (GCR)**
   - Website: https://cloud.google.com/container-registry
   - Cost: First 500GB/month free storage
   - Setup Time: 30 minutes

**Your Docker Registry Configuration:**
```yaml
DOCKER_REGISTRY: [YOUR-REGISTRY - e.g., docker.io/yourusername]
DOCKER_REGISTRY_USERNAME: [YOUR-REGISTRY-USERNAME]
DOCKER_REGISTRY_PASSWORD: [YOUR-REGISTRY-PASSWORD-TOKEN]
```

---

## 📊 SECTION 9: Monitoring & Error Tracking

### 9.1 Sentry (Optional but Recommended)

**Purpose:** Track errors and performance issues in production.

**Cost:** Free for 5,000 errors/month, then $26/month

**Setup Steps:**

1. **Go to Sentry:**
   https://sentry.io/

2. **Create Account:**
   - Sign up with email or GitHub
   - Create new project: "Vibe PDF Platform"
   - Platform: Python

3. **Get DSN:**
   - Copy the DSN (Data Source Name) from project settings

**Your Sentry Configuration:**
```yaml
SENTRY_DSN: https://[YOUR-SENTRY-KEY]@o[ORG-ID].ingest.sentry.io/[PROJECT-ID]
```

---

## 🎯 SECTION 10: Environment-Specific Configuration

### 10.1 Development Environment

```yaml
APP_ENV: development
DEBUG: "true"
FRONTEND_URL: "http://localhost:3000"
DATABASE_URL: postgresql+asyncpg://vibepdf:devpassword@localhost:5432/vibepdf
REDIS_URL: redis://localhost:6379/0
CORS_ORIGINS: "http://localhost:3000"
```

### 10.2 Staging Environment

```yaml
APP_ENV: staging
DEBUG: "false"
FRONTEND_URL: "https://staging.vibepdf.com"
DATABASE_URL: [YOUR-STAGING-DB-URL]
REDIS_URL: [YOUR-STAGING-REDIS-URL]
CORS_ORIGINS: "https://staging.vibepdf.com"
```

### 10.3 Production Environment

```yaml
APP_ENV: production
DEBUG: "false"
FRONTEND_URL: "https://vibepdf.com"
DATABASE_URL: [YOUR-PRODUCTION-DB-URL]
REDIS_URL: [YOUR-PRODUCTION-REDIS-URL]
CORS_ORIGINS: "https://vibepdf.com,https://www.vibepdf.com"
```

---

## ✅ SECTION 11: Configuration Checklist

**Use this checklist to ensure all required inputs are provided:**

### Critical (Required for Any Deployment)
- [ ] JWT Secret Key generated
- [ ] Database credentials configured
- [ ] Redis credentials configured
- [ ] At least one LLM provider API key provided

### Required for Production
- [ ] Google OAuth Client ID
- [ ] Google OAuth Client Secret
- [ ] Google Service Account JSON
- [ ] Google Drive Folder ID
- [ ] Production domain configured
- [ ] CORS origins configured
- [ ] Docker registry credentials

### Recommended (Optional but Good to Have)
- [ ] Multiple LLM providers (for fallback)
- [ ] Sentry DSN for error tracking
- [ ] Backup encryption key
- [ ] Rate limiting configured

---

## 📤 SECTION 12: Submit Your Configuration

**Once you've filled in all the required values, provide this information:**

### Option A: Copy and Paste Values

```yaml
# --- ADD YOUR FILLED VALUES BELOW ---

SECRET_KEY: [YOUR-SECRET-KEY]
DATABASE_URL: [YOUR-DATABASE-URL]
REDIS_URL: [YOUR-REDIS-URL]
ANTHROPIC_API_KEY: [YOUR-ANTHROPIC-KEY]
OPENAI_API_KEY: [YOUR-OPENAI-KEY]
GOOGLE_AI_API_KEY: [YOUR-GOOGLE-AI-KEY]
GOOGLE_OAUTH_CLIENT_ID: [YOUR-OAUTH-CLIENT-ID]
GOOGLE_OAUTH_CLIENT_SECRET: [YOUR-OAUTH-CLIENT-SECRET]
GOOGLE_SERVICE_ACCOUNT_JSON: [YOUR-SERVICE-ACCOUNT-JSON]
GOOGLE_DRIVE_FOLDER_ID: [YOUR-DRIVE-FOLDER-ID]
CORS_ORIGINS: [YOUR-CORS-ORIGINS]
SENTRY_DSN: [YOUR-SENTRY-DSN]
```

### Option B: Upload Configuration File

1. Fill in this document with your values
2. Save it as `my-configuration.md`
3. Upload/attach the file and share with me

---

## 🔒 SECTION 13: Security Best Practices

**⚠️ IMPORTANT SECURITY REMINDERS:**

1. **Never commit secrets to Git**
   - Add sensitive files to `.gitignore`
   - Use environment variables for all secrets
   - Never hardcode API keys in code

2. **Use strong, unique passwords**
   - Generate random strings for JWT secrets
   - Use different passwords for database, Redis, etc.
   - Use a password manager (1Password, Bitwarden, etc.)

3. **Rotate credentials regularly**
   - Change JWT secrets monthly
   - Rotate API keys quarterly
   - Update service account keys if compromised

4. **Principle of least privilege**
   - Only grant necessary permissions to service accounts
   - Use separate environments (dev, staging, prod)
   - Limit API key usage

5. **Monitor usage**
   - Set up billing alerts for all services
   - Monitor API usage regularly
   - Review access logs

---

## 🆘 SECTION 14: Getting Help

**If you need help acquiring any of these credentials:**

### Anthropic API Key
- Documentation: https://docs.anthropic.com/
- Support: support@anthropic.com
- Console: https://console.anthropic.com/

### OpenAI API Key
- Documentation: https://platform.openai.com/docs/
- Support: help@openai.com
- Platform: https://platform.openai.com/

### Google Cloud Services
- Documentation: https://cloud.google.com/docs
- Support: https://cloud.google.com/support
- Console: https://console.cloud.google.com/

### Supabase
- Documentation: https://supabase.com/docs
- Support: https://supabase.com/support
- Console: https://supabase.com/dashboard

### Redis Cloud
- Documentation: https://docs.redis.com/
- Support: https://redis.com/enterprise/support
- Console: https://console.redis.com/

---

## 📋 Quick Reference: Required Credentials Summary

| # | Credential | Where to Get | Cost | Priority |
|---|------------|--------------|------|----------|
| 1 | JWT Secret Key | Generate locally | Free | 🔴 CRITICAL |
| 2 | PostgreSQL Credentials | Supabase/Neon/AWS | Free/$ | 🔴 CRITICAL |
| 3 | Redis Credentials | Docker/Redis Cloud/Upstash | Free/$ | 🔴 CRITICAL |
| 4 | Anthropic API Key | https://console.anthropic.com | $ | 🟠 HIGH |
| 5 | OpenAI API Key | https://platform.openai.com | $ | 🟠 HIGH |
| 6 | Google AI API Key | https://aistudio.google.com | Free/$ | 🟠 HIGH |
| 7 | Google OAuth Client ID | Google Cloud Console | Free | 🟠 HIGH |
| 8 | Google OAuth Client Secret | Google Cloud Console | Free | 🟠 HIGH |
| 9 | Google Service Account JSON | Google Cloud Console | Free | 🟠 HIGH |
| 10 | Google Drive Folder ID | Google Drive | Free | 🟠 HIGH |
| 11 | Production Domain | Domain Registrar | $ | 🟡 MEDIUM |
| 12 | Docker Registry | Docker Hub/AWS/GCR | Free/$ | 🟡 MEDIUM |
| 13 | Sentry DSN | https://sentry.io | Free/$ | 🟢 OPTIONAL |

---

## 🎯 Next Steps After Providing Configuration

**Once you provide all the required inputs:**

1. ✅ I'll create environment configuration files (`.env.development`, `.env.staging`, `.env.production`)
2. ✅ I'll set up Docker Compose with your database and Redis credentials
3. ✅ I'll configure the backend with your API keys
4. ✅ I'll set up Google OAuth with your credentials
5. ✅ I'll configure Google Drive integration with your service account
6. ✅ I'll test all integrations end-to-end
7. ✅ I'll generate the database migrations
8. ✅ I'll deploy and verify the application works

**Estimated Setup Time:** 1-2 hours after receiving all configuration

---

## 📝 Filled Configuration Template (Copy This Section)

```yaml
# ========================================
# VIBE PDF PLATFORM - YOUR CONFIGURATION
# ========================================

# --- APPLICATION SECURITY ---
APP_ENV: production
DEBUG: "false"
SECRET_KEY: "[YOUR-JWT-SECRET-KEY-HERE]"
FRONTEND_URL: "[YOUR-FRONTEND-URL]"

# --- DATABASE ---
DATABASE_URL: "[YOUR-DATABASE-URL]"
DB_HOST: "[YOUR-DB-HOST]"
DB_PORT: "5432"
DB_NAME: "vibepdf"
DB_USER: "[YOUR-DB-USER]"
DB_PASSWORD: "[YOUR-DB-PASSWORD]"

# --- REDIS ---
REDIS_URL: "[YOUR-REDIS-URL]"
REDIS_HOST: "[YOUR-REDIS-HOST]"
REDIS_PORT: "[YOUR-REDIS-PORT]"
REDIS_PASSWORD: "[YOUR-REDIS-PASSWORD]"

# --- LLM PROVIDERS ---
ANTHROPIC_API_KEY: "[YOUR-ANTHROPIC-API-KEY]"
OPENAI_API_KEY: "[YOUR-OPENAI-API-KEY]"
GOOGLE_AI_API_KEY: "[YOUR-GOOGLE-AI-API-KEY]"
LLM_PROVIDER_PRIORITY: "anthropic,openai,google"

# --- GOOGLE OAUTH ---
GOOGLE_OAUTH_CLIENT_ID: "[YOUR-OAUTH-CLIENT-ID]"
GOOGLE_OAUTH_CLIENT_SECRET: "[YOUR-OAUTH-CLIENT-SECRET]"
GOOGLE_OAUTH_REDIRECT_URI: "[YOUR-OAUTH-REDIRECT-URI]"

# --- GOOGLE SERVICES ---
GOOGLE_CREDENTIALS_PATH: "/app/credentials/google-service-account.json"
GOOGLE_SERVICE_ACCOUNT_JSON: "[YOUR-SERVICE-ACCOUNT-JSON]"
GOOGLE_DRIVE_FOLDER_ID: "[YOUR-DRIVE-FOLDER-ID]"

# --- CORS ---
CORS_ORIGINS: "[YOUR-CORS-ORIGINS]"

# --- RATE LIMITING ---
RATE_LIMIT_ENABLED: "true"
RATE_LIMIT_REQUESTS: "100"
RATE_LIMIT_PERIOD: "60"

# --- MONITORING ---
SENTRY_DSN: "[YOUR-SENTRY-DSN]"
PROMETHEUS_ENABLED: "true"
LOG_LEVEL: "info"

# --- DEPLOYMENT ---
DOCKER_REGISTRY: "[YOUR-DOCKER-REGISTRY]"
DOCKER_REGISTRY_USERNAME: "[YOUR-REGISTRY-USERNAME]"
DOCKER_REGISTRY_PASSWORD: "[YOUR-REGISTRY-PASSWORD]"
PRODUCTION_DOMAIN: "[YOUR-PRODUCTION-DOMAIN]"
API_DOMAIN: "[YOUR-API-DOMAIN]"

# ========================================
# END OF CONFIGURATION
# ========================================
```

---

## 📧 Contact

**Once you've filled in all the values:**

1. **Save this document** with your filled values
2. **Share it** with me (attach the file or copy-paste the YAML section above)
3. **I'll configure everything** and let you know when ready for testing!

**If you have questions about any section:**
- Refer to the detailed steps in each section
- Check the documentation links provided
- Ask me for clarification on any specific credential

---

**Document Version:** 1.0
**Last Updated:** February 25, 2026
**Next Steps:** Fill in all required values and share with AI assistant
