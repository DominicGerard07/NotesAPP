# 📝 SimpleNotes - Flask Note-Taking Web Application

A clean, responsive, and intuitive note-taking web application built with **Python 3**, **Flask**, and **SQLite**.

---

## ✨ Features

- **User Accounts & Multi-Tenant Privacy**:
  - **Individual Accounts**: Secure user registration and login with salted password hashing (`werkzeug.security`).
  - **Strict Data Isolation**: Each user has their own private notes, folders, and tags. Users cannot see, modify, or search across other users' data.
  - **Personal Home Folder**: Every user automatically receives their own default `Home` folder upon account creation.
  - **Quick Demo Account**: Pre-configured `demo` account (`demo` / `demo123`, email: `demo@example.com`) for immediate testing.
- **Password Reset via Email Verification Code**:
  - **Secure 6-Digit Codes**: Users can reset forgotten passwords by requesting a time-limited (15 min) verification code sent to their registered email address.
  - **Production SMTP Ready**: Works out of the box with standard SMTP servers (Gmail, SendGrid, Mailgun, Amazon SES, or custom mail transfer agents) via standard environment variables.
  - **Local Development / Offline Fallback**: When no SMTP credentials are configured, the reset code is securely logged to the console and displayed in the UI banner for zero-setup local development and evaluation.
- **Folder Structure & Hierarchical Subfolders**:
  - **Home Folder**: Pre-configured default space for general notes and quick thoughts (`parent_id = NULL`).
  - **Nested Subfolders**: Create folders inside folders to organize complex subjects, subcategories, or projects (e.g., *Work / Projects / Sprint 1*, *Computer Science / Python*).
  - **Visual Tree Guide Lines**: Directory tree sidebar displaying connecting branch lines (`├──`, `└──`) and vertical guide spines linking subfolders clearly with their parent folders.
  - **Hover Action**: Quick `+` button on any folder in the sidebar to instantly create a nested subfolder inside it.
  - **Safe Recursive Deletion**: Deleting any folder (root or nested) safely cascades all notes in that folder and its descendant subfolders to the **Home** folder—guaranteeing zero data loss.
  - **Folder Assignment & Breadcrumbs**: Assign notes to any subfolder from the note editor dropdown or filter by folder pill badge on cards with full path tooltips.
- **CRUD Operations**: Create, read, edit, and delete notes effortlessly.
- **Fluid FLIP Morphing Animations**: Seamless expanding and closing morph transitions calculated with precise bounding-box offsets (`top-left` origin FLIP math) and synchronized content fade, smoothly expanding from the card box into the full editor modal and collapsing back cleanly into the card box.
- **Markdown & Checklists**: Live markdown preview with support for bold, italic, code blocks, lists, interactive task checklists (`- [ ] task`), and real-time visual progress bars tracking task completion when checkboxes are ticked.
- **Modern Rounded Design**: Soft rounded edges across cards, modals, buttons, pill badges, and inputs.
- **Organization**:
  - **Pinning**: Pin key notes to keep them visible at the top.
  - **High-Contrast Pop Colors**: Categorize visually with punchy, high-contrast colors (Default, Blue, Green, Amber, Rose, Purple).
  - **Tags**: Multi-tagging with count badges and sidebar tag filtering.
- **Universal Search & Sort**:
  - **Universal Search across all folders & subfolders**: Instant debounced search querying across titles, content, tags, folder names, and nested subfolder paths (`Work / Projects / Sprint 1`).
  - **Subfolder Inclusivity**: Results from inside subfolders are surfaced universally, with note cards displaying full folder path pills.
  - **Quick Scope Toggle**: Easily switch between searching universally across all folders or restricting scope to the active folder and its subfolders.
  - Sort by Recently Updated, Oldest Updated, Recently Created, Oldest Created, or Title (A-Z / Z-A).
  - Switch between Card Grid and List layout views.
- **Dark / Light Mode**: Beautiful dark and light themes with preference saved in `localStorage`.
- **Keyboard Shortcuts**:
  - `Ctrl + N` / `Cmd + N`: Create a new note.
  - `/` or `Ctrl + K`: Jump to search bar.
  - `Ctrl + S`: Save note from within the editor.
  - `Escape`: Close open modal.
- **Data Portability**:
  - Export all notes as a JSON backup (`notes_backup.json`).
  - Import JSON backups to restore notes.
  - Single-note download as Plain Text (`.txt`).
- **Zero Heavy Frontend Dependencies**: Written in vanilla JavaScript and modern CSS for lightning-fast loading and zero bundle bloat.

---

## 📁 Project Structure

```
notes_app/
├── api/
│   └── index.py        # Vercel serverless entrypoint for @vercel/python
├── app.py              # Flask app factory, auth routes, page routes & RESTful JSON API
├── database.py         # SQLite schema initialization, users, reset codes & multi-tenant CRUD
├── email_service.py    # Multi-provider email dispatcher (Resend, Gmail, SMTP & dev fallback)
├── vercel.json         # Vercel deployment routing and build configuration
├── .vercelignore       # Vercel ignore list for lean serverless deployments
├── .env.example        # Environment variable template for email & session settings
├── sample_notes.py     # Script to seed starter notes & subject folders for demo user
├── requirements.txt    # Python dependencies (Flask >= 3.0.0, python-dotenv)
├── run.sh              # One-click startup script for Linux/macOS
├── run.bat             # One-click startup script for Windows
├── static/
│   ├── app.js          # Client-side auth, reactive search, folder tree logic, modals & markdown
│   └── style.css       # Clean responsive styling, auth modal, animations, themes, and CSS variables
├── templates/
│   └── index.html      # Main HTML5 application shell, auth modal and editor modals
└── tests/
    └── test_app.py     # Comprehensive automated test suite (27 tests: auth, DB & API)
```

---

## 🚀 Quick Start

### Option 1: Using the Startup Script (Recommended)

- **Linux / macOS / WSL / Git Bash**:
  ```bash
  ./run.sh
  ```
- **Windows (Command Prompt / PowerShell / Double-Click)**:
  ```cmd
  run.bat
  ```
This automatically sets up the `.venv`, installs requirements, seeds sample notes if needed, and launches the server at `http://127.0.0.1:5000`.

### Option 2: Manual Setup

#### On Linux / macOS:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 sample_notes.py
python3 app.py
```

#### On Windows (PowerShell):
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python sample_notes.py
python app.py
```

#### On Windows (Command Prompt / CMD):
```cmd
python -m venv .venv
.venv\Scripts\activate.bat
pip install -r requirements.txt
python sample_notes.py
python app.py
```

Open your browser at:
```
http://127.0.0.1:5000
```

---

## 📡 RESTful API Endpoints

### 🔐 Authentication & Password Reset
| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/auth/register` | Register a new user (`{"username", "email", "password"}`) and establish session |
| `POST` | `/api/auth/login` | Authenticate user via username or email (`{"username", "password"}`) |
| `POST` | `/api/auth/logout` | Terminate current session |
| `GET` | `/api/auth/me` | Fetch active authenticated user profile |
| `POST` | `/api/auth/forgot-password` | Dispatch 6-digit reset code to user's registered email (`{"email"}`) |
| `POST` | `/api/auth/reset-password` | Verify 6-digit code and set new password (`{"email", "code", "new_password"}`) |

### 📁 Notes & Folders (Protected by Session Authentication)
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/folders` | List all user folders in tree order with `depth`, `path`, and `note_count` |
| `POST` | `/api/folders` | Create a new folder or nested subfolder (`{"name": "Projects", "parent_id": 2}`) |
| `PUT` | `/api/folders/<id>` | Rename or re-parent a folder (`{"name": "Sprint 1", "parent_id": 3}`) |
| `DELETE` | `/api/folders/<id>` | Delete folder & subfolders (cascades all descendant notes to Home) |
| `GET` | `/api/notes` | List user notes (supports `?q=search`, `?universal=true`, `?folder_id=1`, `?subfolders=true`, `?tag=work`) |
| `POST` | `/api/notes` | Create a new note (`{title, content, tags, color, is_pinned, folder_id}`) |
| `GET` | `/api/notes/<id>` | Fetch a single note by ID (includes `folder_path` and `folder_name`) |
| `PUT` | `/api/notes/<id>` | Update an existing note (supports moving between folders) |
| `DELETE` | `/api/notes/<id>` | Delete a note |
| `POST` | `/api/notes/<id>/pin` | Toggle pinned state for a note |
| `GET` | `/api/tags` | List all unique tags with note counts |
| `GET` | `/api/export` | Download a complete JSON backup of user's notes |
| `POST` | `/api/import` | Restore / import notes from JSON payload into user account |

---

---

## ☁️ Deploy to Vercel

SimpleNotes is fully pre-configured for one-click serverless deployment on **Vercel** with `@vercel/python`, auto-resolving routes via `api/index.py` and `vercel.json`.

### Option A: Deploy via GitHub (Recommended)

1. **Push your code to GitHub**:
   ```bash
   git init
   git add .
   git commit -m "Initial commit of SimpleNotes"
   git branch -M main
   git remote add origin https://github.com/<your-username>/<your-repo-name>.git
   git push -u origin main
   ```

2. **Import into Vercel**:
   - Go to [vercel.com](https://vercel.com) and log in.
   - Click **"Add New..."** -> **"Project"**.
   - Select your GitHub repository and click **"Import"**.
   - Leave the Framework Preset as **Other** (Vercel automatically detects `vercel.json` and `@vercel/python`).

3. **Configure Environment Variables in Vercel**:
   In your Vercel Project settings (**Settings** -> **Environment Variables**), add:
   - `SECRET_KEY`: A secure random secret string for session cookies.
   - Connect a **Turso** database from the Vercel Marketplace to this project. The integration supplies `TURSO_DATABASE_URL` and `TURSO_AUTH_TOKEN`, which the app uses for persistent users, notes, folders, and password reset codes. Deploy again after connecting it.
   - For real emails, choose either **Resend** or **Gmail** (see instructions below):
     - **Resend**: `RESEND_API_KEY` = `re_...`
     - **Gmail**: `GMAIL_USER` = `you@gmail.com` and `GMAIL_APP_PASSWORD` = `xxxx xxxx xxxx xxxx`

4. Click **"Deploy"**! Your application will be live with a free `*.vercel.app` HTTPS domain.

---

### Option B: Deploy via Vercel CLI

1. Install the Vercel CLI (if not already installed):
   ```bash
   npm install -g vercel
   ```

2. Run `vercel` from the project directory:
   ```bash
   vercel
   ```

3. Deploy to production:
   ```bash
   vercel --prod
   ```

> **Persistent storage on Vercel**: Vercel Functions only provide temporary `/tmp` storage, so a local SQLite file there cannot safely hold accounts or notes. Connect a Turso database through the Vercel Marketplace; the app then reads `TURSO_DATABASE_URL` and `TURSO_AUTH_TOKEN` and stores data in Turso. On Vercel, the app now refuses to start without both values instead of silently using temporary storage. Data that has already disappeared from `/tmp` cannot be recovered by this change; restore it from an export or other backup if one exists.

---

## ✉️ Setting Up Real Email Delivery (Verification Codes)

To have the 6-digit verification code sent directly to a user's real email address, configure **either** of the following options in your `.env` file (locally) or in **Vercel Project Settings -> Environment Variables**:

### ⚡ Option 1: Resend (Recommended for Vercel)
Resend sends emails over HTTPS (never blocked by cloud firewalls or SMTP port restrictions):
1. Sign up for free at [resend.com](https://resend.com) (3,000 free emails/month).
2. Create an API Key in the Resend dashboard.
3. Add the following environment variables:
   ```env
   RESEND_API_KEY=re_your_api_key_here
   RESEND_FROM=SimpleNotes <onboarding@resend.dev>
   ```
   *(Note: `onboarding@resend.dev` delivers to the email address registered with your Resend account. To send to any recipient, add and verify your custom domain in Resend).*

---

### 📧 Option 2: Gmail (Quick & Free)
Use your existing Gmail address with a secure Google App Password:
1. Go to your [Google Account Security Settings](https://myaccount.google.com/security).
2. Ensure **2-Step Verification** is turned ON.
3. Search for **App Passwords** ([direct link](https://myaccount.google.com/apppasswords)).
4. Create an app password named `SimpleNotes` to generate a 16-character code.
5. Add the following environment variables:
   ```env
   GMAIL_USER=your_email@gmail.com
   GMAIL_APP_PASSWORD=abcd efgh ijkl mnop
   ```

---

### 📮 Option 3: Standard SMTP (Outlook, Brevo, SendGrid, Mailgun)
```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@example.com
SMTP_PASS=your_password_or_token
SMTP_FROM=SimpleNotes <your_email@example.com>
SMTP_TLS=true
```

> **Offline / Local Dev Fallback**: If neither Resend nor SMTP credentials are provided, SimpleNotes logs the verification code to the console and displays it in a local dev banner in the UI modal—allowing zero-setup local evaluation.

---

## 🧪 Running Automated Tests

Run the test suite using Python's built-in `unittest`:

```bash
.venv/bin/python3 -m unittest discover -s tests -v
```

All 27 automated tests verify:
- Vercel serverless entrypoint (`api/index.py`) and environment loading
- Email dispatching via Resend API and Gmail SMTP
- User registration, authentication sessions, and logout
- Strict multi-tenant data isolation (User A cannot view, edit, search, or delete User B's notes or folders)
- Email-based password reset code generation, expiration, single-use validation, and password updating
- Universal search across all folders and subfolders
- Folder and nested subfolder creation, path construction, tree order, circular reference protection, and safe deletion cascade
- Checklists, progress calculations, and export/import workflows.
