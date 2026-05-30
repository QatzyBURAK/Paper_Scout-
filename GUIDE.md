# 📘 Paper Scout — Installation & Troubleshooting Guide

This guide is designed to help you install, configure, and troubleshoot Paper Scout using Docker or local environments on **Linux (Ubuntu), Windows, and macOS**. It covers quick starts, platform-specific setups, and solutions to frequently encountered issues.

---

## Table of Contents

1. Prerequisites
2. Quick Start (3 Commands)
3. Platform-Specific Installation
4. Troubleshooting & FAQ
5. Fast Debugging Commands
6. Important Architecture Notes

---

## 1. Prerequisites

Before installing, make sure your system meets the following specifications:

- **Docker** (Engine or Desktop) + **Docker Compose v2** (`docker compose` - with space, not the legacy hyphenated `docker-compose`)
- **Git**
- **Hardware RAM:** At least **4 GB of free RAM** (required for running sentence-transformers embedding model + ChromaDB vector database), 8 GB recommended.
- **Disk Space:** At least **3 GB of free space** (to download docker images, python dependencies, node modules, and AI models).
- **Network:** Active internet connection (required on first launch to download libraries and the sentence-transformers model).

---

## 2. Quick Start (Ready in 3 Commands)

If your environment is fully prepared, run these commands to spin up the application:

```bash
# 1. Clone the repository
git clone https://github.com/QatzyBURAK/Paper_Scout-.git
cd Paper_Scout-

# 2. Prevent SQLite folder mount issue (highly recommended - see Issue #1)
touch backend/paper_scout.db
mkdir -p backend/chroma_data

# 3. Build and run containers
docker compose up --build
```

Once execution is complete:
- **Frontend SPA:** <http://localhost:5173>
- **Backend Swagger API Docs:** <http://localhost:8001/docs>

*Note: The first build can take **5 to 15 minutes** depending on your internet speed, as it downloads base OS images, npm/pip packages, and the Hugging Face AI embedding model. Subsequent launches take less than 5 seconds.*

---

## 3. Platform-Specific Installation

### 3.1. Linux (Ubuntu 22.04 / Debian)

Install the Docker Engine directly (Docker Desktop is not required for headless Linux servers):

```bash
sudo apt update
sudo apt install -y ca-certificates curl gnupg
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | \
  sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
  https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

Verify installation:
```bash
sudo docker run hello-world
```

**Running Docker without sudo (Highly Recommended):**
To avoid typing `sudo` on every command and to allow tools like VS Code extensions or Claude Code MCP to connect to the daemon:

```bash
sudo usermod -aG docker $USER
newgrp docker
docker run hello-world   # Should run successfully without sudo
```

*If you still get permission denied errors, restart your terminal session or log out and log back in.*

### 3.2. Windows

Install **Docker Desktop**: <https://www.docker.com/products/docker-desktop>

During installation:
- **WSL2 Backend:** Ensure the **WSL2 backend** option is checked (significantly faster than Hyper-V).
- **File Sharing:** Enable Drive Sharing (Settings → Resources → File sharing) to allow bind mounts for databases.
- Run system commands in **PowerShell or CMD**. Note environment variable differences:
  - CMD: `%USERPROFILE%`
  - PowerShell: `$env:USERPROFILE`
- **Line Endings:** Windows git handles line endings with CRLF which can crash inside Linux containers (see Issue #8).

### 3.3. macOS

Install **Docker Desktop**: <https://www.docker.com/products/docker-desktop>

**For Apple Silicon (M1/M2/M3) users:**
- Sentence-transformers and PyTorch have native arm64 wheels, but some sub-dependencies might try to fall back to amd64. If you see `no matching distribution` errors during build, ensure your Docker Desktop has **Rosetta 2 enabled** (Settings → General → Use Rosetta for x86/amd64 emulation).
- The first build might trigger "running under emulation" warnings and can take up to 20-30 minutes, but it will compile successfully and run with high stability thereafter.

---

## 4. Troubleshooting & FAQ

### Issue #1 — `sqlite3.OperationalError: unable to open database file` (Most Common)

**Symptoms:** The backend container fails to start, throwing an SQLite error in the logs.
**Cause:** This is a classic Docker bind-mount behavior. In `docker-compose.yml`, we mount `./backend/paper_scout.db:/app/paper_scout.db`. If `paper_scout.db` does not exist on your host machine when Docker spins up, **Docker automatically creates it as a directory**. SQLite cannot write to a directory, causing a crash.

**Solution:**
```bash
# 1. Stop containers
docker compose down

# 2. Check if paper_scout.db is a directory
# On Linux/macOS, a directory starts with 'd' in ls -la. On Windows, check the folder explorer.
# If it is a folder, delete it:
rm -rf backend/paper_scout.db

# 3. Create a blank file instead
touch backend/paper_scout.db
mkdir -p backend/chroma_data

# 4. Restart containers
docker compose up
```

---

### Issue #2 — GitHub Clone Fails (`Authentication failed / Password auth not supported`)

**Symptoms:** Git fails to clone the repository.
**Cause:** GitHub has deprecated password authentication in favor of Personal Access Tokens (PAT) or SSH.

**Solutions:**
- **Quickest Way (Download ZIP):** If it's a public repo, download the zip package directly:
  ```bash
  wget https://github.com/QatzyBURAK/Paper_Scout-/archive/refs/heads/main.zip -O paper-scout.zip
  unzip paper-scout.zip
  mv Paper_Scout--main paper-scout
  cd paper-scout
  ```
- **Using Personal Access Token (PAT):**
  1. Go to your GitHub account → Settings → Developer Settings → Personal Access Tokens → Tokens (classic).
  2. Generate a classic token, checking only the `repo` scope.
  3. Copy the token (`ghp_...`). When git clone prompts for credentials, enter your regular username and use the token as your password.

---

### Issue #3 — Port Conflict (`Bind for 0.0.0.0:8001 failed: port already allocated`)

**Symptoms:** Docker fails to bind to port 8001 (backend) or 5173 (frontend).
**Cause:** Another local process (e.g. an active local python/node instance, or a zombie socket) is occupying the port.

**Solution:**
Identify and terminate the process holding the port:
* **Linux/macOS:**
  ```bash
  sudo lsof -i :8001
  # Kill the process
  kill -9 <PID>
  ```
* **Windows (PowerShell):**
  ```powershell
  netstat -ano | findstr :8001
  # Kill the process using the PID found
  taskkill /PID <PID> /F
  ```
* *If the system says "Process not found" but netstat still shows it, the socket is in a lingering "zombie" state. A computer reboot will clear it, or you can temporarily modify the port mapping in `docker-compose.yml` (e.g., change `"8001:8001"` to `"8002:8001"`).*

---

### Issue #4 — `docker compose: command not found`

**Symptoms:** The terminal does not recognize the docker compose command.
**Cause:** You are running an older Docker version without the v2 compose plugin.

**Solution:**
On Linux, install the modern compose plugin:
```bash
sudo apt install -y docker-compose-plugin
```
*Note: Always use the modern **spaced** syntax: `docker compose up`. The hyphenated legacy syntax (`docker-compose`) has been deprecated.*

---

### Issue #5 — Sentence-Transformers Model Download Fails or is Extremely Slow

**Symptoms:** The backend hangs or crashes with `HTTPError / Connection refused` during initialization.
**Cause:** During the first startup, the backend contacts Hugging Face to download the `all-MiniLM-L6-v2` embedding model (~80 MB). If your proxy, firewall, or corporate network restricts Hugging Face, it will fail.

**Solutions:**
- Ensure you have an active network connection on the host machine.
- If Hugging Face is blocked in your country or network, you can pre-download the model, or use a corporate VPN during the first container build to cache the model in the `hf_cache` Docker volume.

---

### Issue #6 — Frontend Shows Blank Screen or "Unable to Connect"

**Symptoms:** The frontend loads but displays a "Could not connect to server" error.
**Cause:** The frontend is pointing to the wrong API address, or a CORS preflight block is triggered.

**Solutions:**
* **CORS Preflight Issue:** The backend CORS middleware only permits allowed origins. Our backend has been fortified with a dynamic regex handler:
  `allow_origin_regex=r"https?://(localhost|127\.0\.0\.1)(:\d+)?"`
  This allows any local port on your host (e.g. `5173`, `5174`, etc.). If you are running the frontend on a custom remote server, verify that the server's domain is added to `PAPER_SCOUT_CORS_ORIGINS` in your environment variables.
* **Port / URL Mismatch:** Verify your frontend API environment variable is aligned. In `.env.local` or `.env.example`, make sure it points to:
  `VITE_API_BASE_URL=http://127.0.0.1:8001`
  *Always rebuild containers after env changes:* `docker compose down && docker compose up --build`.

---

### Issue #7 — Windows Line Endings Break Container Scripts (`/bin/sh^M: not found`)

**Symptoms:** Shell scripts fail to execute in containers with weird syntax errors.
**Cause:** Windows automatically converts Linux line endings (`LF`) to Windows carriage returns (`CRLF`). Linux containers do not accept carriage returns.

**Solution:**
Configure Git to check out files keeping their native line endings, then **delete and re-clone** the repository:
```bash
git config --global core.autocrlf input
cd ..
rm -rf Paper_Scout-
git clone https://github.com/QatzyBURAK/Paper_Scout-.git
```

---

### Issue #8 — Ingestion Returns "Time Out / 504 Gateway Timeout" or "429 Too Many Requests"

**Symptoms:** Ingesting papers throws a 504 Gateway Timeout or 429 Too Many Requests.
**Cause:** 
- **429 (Rate Limits):** Academic APIs like Semantic Scholar or arXiv have strict rate limits. If too many queries are sent, they temporarily block your IP.
- **504 (Timeouts):** If the external APIs are busy, they take too long to respond.
- **Resilient Ingestion Engine:** We have engineered a highly robust **Resilient Ingestion Engine**.
  - **Single Source Failure:** If you check both arXiv and Semantic Scholar, and one fails (e.g. arXiv times out or Semantic Scholar is rate-limited), **the backend continues and successfully ingests papers from the working service!**
  - **Fail-Fast:** We reduced the maximum request timeout from **15.0 seconds to 7.0 seconds** to prevent browser gateway timeouts.
  - **All-Source Failure:** If all selected services fail (absolute zero papers fetched), the system raises a clear, localized Turkish error explaining the situation so you are never left with silent failures. Simply wait 1-2 minutes and try again.

---

## 5. Fast Debugging Commands

Use these handy terminal commands to debug the state of your Docker containers:

```bash
# Check if containers are active and healthy
docker compose ps

# View live consolidated logs (all services)
docker compose logs -f

# View live logs for backend only
docker compose logs -f backend

# Open an interactive shell inside the backend container
docker compose exec backend bash

# Test if the API endpoint responds directly
curl "http://localhost:8001/papers?limit=2&offset=0"

# Stop containers safely (preserving all data)
docker compose down

# Hard Reset (Wipes containers and all volume cache - useful for clean test)
docker compose down -v
docker system prune -af
```

---

## 6. Important Architecture Notes

- **Ports:** Backend listens on port **8001**. Frontend listens on port **5173**. If you map these to different ports on the host, ensure they are updated in `docker-compose.yml`, `frontend/.env.local`, and backend CORS configurations simultaneously.
- **Python Version:** Locked strictly to **Python 3.10** to guarantee package and strict linter compatibility.
- **Database Path:** Local database files are saved in the `./backend/` directory on your host. Backup this folder if you want to export your ingested database.
- **Verification Test:** To perform a complete clean slate verification, run:
  `docker compose down -v && docker compose up --build`
  Ingest a few papers, run `docker compose down` (without the `-v` flag), and boot again. Your data must be perfectly persistent.

*If you encounter any other edge cases, feel free to open a GitHub Issue or add your findings to this GUIDE.*
