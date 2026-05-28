# Paper Scout — Kurulum & Sorun Giderme Rehberi

Bu rehber Paper Scout'u Docker ile **Linux (Ubuntu), Windows ve macOS** üzerinde kurmak için. Hem yeni kuranlara hem de hata aldığında ne yapacağını bilmek isteyenlere yazıldı. Çoğu sorun aşağıdaki "Sık Karşılaşılan Sorunlar" bölümünde çözülmüş — önce oraya bak.

## İçindekiler

1. Önkoşullar
2. Hızlı başlangıç (3 komut)
3. İşletim sistemine göre kurulum
4. Sık karşılaşılan sorunlar
5. Hızlı debug komutları
6. Notlar

---

## 1. Önkoşullar

Tüm OS'ler için ortak:

- **Docker** (Engine veya Desktop) + **Docker Compose v2** (`docker compose`, tireli olan değil)
- **Git**
- En az **4 GB RAM** boş (sentence-transformers + ChromaDB için), 8 GB önerilen
- En az **3 GB disk** alanı (image'lar + model + node_modules)
- İnternet bağlantısı (ilk build sırasında pip/npm/model download için)

---

## 2. Hızlı başlangıç (her şey hazırsa)

```bash
git clone https://github.com/QatzyBURAK/paper-scout.git
cd paper-scout

# SQLite tuzağına düşmemek için ÖNCE boş dosyaları yarat (bkz. Sorun #1)
touch backend/paper_scout.db
mkdir -p backend/chroma_data

docker compose up --build
```

Bittiğinde:
- Frontend: <http://localhost:5173>
- Backend Swagger: <http://localhost:8001/docs>

İlk build **5-15 dakika** sürer (model download dahil). Sonraki açılışlar çok hızlı.

---

## 3. İşletim sistemine göre kurulum

### 3.1. Linux (Ubuntu 22.04 / Debian)

Docker Engine'i kur (Docker Desktop'a gerek yok):

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

Test:
```bash
sudo docker run hello-world
```

**Önemli — sudo'suz docker:** Her komutta `sudo` yazmak istemiyorsan (ve VS Code Docker eklentisi/Claude Code MCP gibi araçların çalışması için):

```bash
sudo usermod -aG docker $USER
newgrp docker
docker run hello-world   # sudo'suz çalışmalı
```

Hâlâ "permission denied" alıyorsan **terminali kapat aç** veya logout/login yap.

### 3.2. Windows

**Docker Desktop** kur: <https://www.docker.com/products/docker-desktop>

Kurulum sırasında:
- **WSL2 backend** seçeneğini işaretle (önerilen, daha hızlı).
- Drive sharing'i etkinleştir (bind mount için gerekli — Settings → Resources → File sharing).

Önemli notlar:
- Sistem komutlarını **CMD veya PowerShell**'de çalıştır. Ortam değişkeni syntax'ı farklı:
  - CMD: `%USERPROFILE%`
  - PowerShell: `$env:USERPROFILE`
- Git'i ilk kullanırken `core.autocrlf` ayarı önemli (bkz. Sorun #8).

### 3.3. macOS

**Docker Desktop** kur: <https://www.docker.com/products/docker-desktop>

**Apple Silicon (M1/M2/M3) kullanıcıları DİKKAT:**
- sentence-transformers + PyTorch arm64 wheel'leri var ama bazı eski sürümler hâlâ amd64-only. Build'de `no matching distribution` veya emülasyon yavaşlığı görürsen, Dockerfile'da Python image'ını `python:3.10-slim` yerine `--platform=linux/amd64` ile zorla, ya da arm64 uyumlu PyTorch sürümünü pin'le.
- Build sırasında "running under emulation" uyarısı görürsen ilk build çok yavaş olabilir (15-30 dakika).

---

## 4. Sık karşılaşılan sorunlar

### Sorun #1 — `sqlite3.OperationalError: unable to open database file` (EN YAYGIN)

Backend ayağa kalkmıyor, log'da SQLite hatası. Aslında Docker'ın klasik bir tuzağı: `docker-compose.yml` içinde

```yaml
- ./backend/paper_scout.db:/app/paper_scout.db
```

şeklinde bir bind mount var. **Host'ta `paper_scout.db` dosyası yoksa, Docker onu KLASÖR olarak yaratıyor.** SQLite de "klasöre yazamam" diye patlıyor.

**Çözüm:**

```bash
docker compose down
touch backend/paper_scout.db        # boş dosya yarat
mkdir -p backend/chroma_data        # Chroma için klasör, varsa dokunmaz
ls -la backend/paper_scout.db       # çıktı '-rw-...' ile başlamalı (dosya)
```

Eğer `ls -la` çıktısı `drwx...` ile başlıyorsa **klasör olarak yaratılmış**, sil ve yeniden:

```bash
rm -rf backend/paper_scout.db
touch backend/paper_scout.db
docker compose up
```

Bu sorun ilk kurulumda neredeyse herkesin başına gelir.

### Sorun #2 — GitHub clone hatası (`Authentication failed`)

```
remote: Invalid username or token. Password authentication is not supported.
```

GitHub 2021'den beri parola ile auth kabul etmiyor. İki yol:

**Public repo ise → ZIP indir (en hızlı):**

```bash
wget https://github.com/QatzyBURAK/paper-scout/archive/refs/heads/main.zip -O paper-scout.zip
unzip paper-scout.zip
mv paper-scout-main paper-scout
cd paper-scout
```

`unzip` yoksa: `sudo apt install unzip -y`. Branch `master` ise URL'de `main` yerine `master` yaz.

**Private repo ise → Personal Access Token (PAT):**

1. <https://github.com/settings/tokens/new> aç
2. Scopes: yalnızca `repo` kutusunu işaretle
3. Generate token → `ghp_...` ile başlayan token'ı **kopyala** (bir daha gösterilmez)
4. `git clone` istediğinde Username = kullanıcı adın, Password = token (paste edince görünmez, normal)

### Sorun #3 — Port çakışması (`Bind for 0.0.0.0:8001 failed: port already allocated`)

8001 veya 5173 portu başka bir süreç tarafından tutulmuş. Linux/macOS:

```bash
sudo lsof -i :8001
# veya
sudo ss -tlnp | grep 8001
```

Windows (PowerShell):

```powershell
netstat -ano | findstr :8001
```

Çıkan PID'i öldür:
- Linux/macOS: `kill -9 <PID>`
- Windows: `taskkill /PID <PID> /F`

**Zombi soket durumu** (PID listening görünüyor ama `taskkill` "process not found" diyor): süreç ölmüş ama soket lingering state'te. Bilgisayarı yeniden başlatınca temizlenir, ya da **farklı bir port kullan** — `docker-compose.yml`'de `8001:8001` yerine `8002:8001` yap, frontend'in `VITE_API_BASE_URL`'ini de güncelle.

### Sorun #4 — `docker compose: command not found`

Çok eski Docker kurmuşsun, modern v2 plugin yok. Linux'ta:

```bash
sudo apt install -y docker-compose-plugin
```

Windows/macOS Docker Desktop'ta otomatik gelir. **Boşluklu** kullan (`docker compose`), tireli (`docker-compose`) eskidi.

### Sorun #5 — `permission denied while trying to connect to the Docker daemon socket` (Linux)

Kullanıcın docker grubunda değil. Çözüm:

```bash
sudo usermod -aG docker $USER
newgrp docker
```

Sonra **terminali kapat ve aç** (newgrp her zaman tetiklemez). Hâlâ alıyorsan logout/login yap. Son çare reboot.

### Sorun #6 — sentence-transformers ilk açılışta çok yavaş veya HATA veriyor

Backend ilk kez ayağa kalkarken `all-MiniLM-L6-v2` modelini indiriyor (~80 MB). Bu ilk build'de **bir kere** olur, sonra cache'lenir.

**Çok yavaş ise:**
- İnternetin yavaş, normal.
- Dockerfile'da `--mount=type=cache,target=/root/.cache/huggingface` kullanılıyorsa hızlanır.

**`HTTPError` veya `Connection refused` ise:**
- Build sırasında ağ yok / kısıtlı (firewall, kurumsal ağ).
- Çözüm: model'i **build sırasında pre-download** et (Dockerfile'da `RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"`).

### Sorun #7 — Frontend açılıyor ama "Beklenmeyen bir hata" / boş ekran (CORS veya wrong URL)

Frontend backend'e bağlanamıyor. Tarayıcı DevTools → Console + Network sekmesine bak:

- **CORS hatası**: Backend'in CORS allowed origins'inde frontend'in URL'i yok. `paper_scout/api/app.py` (veya app create dosyası) içinde CORS middleware'i kontrol et — `http://localhost:5173` izinli olmalı.
- **404 / Connection refused**: Frontend yanlış porta gidiyor. `frontend/.env.local` veya `frontend/.env` içinde:
  ```
  VITE_API_BASE_URL=http://localhost:8001
  ```
  yazıyor mu? **Env değişikliğinden sonra `docker compose down && docker compose up --build`** — Vite env'i sadece başlangıçta okur.
- **Docker compose internal network**: Frontend container'dan backend container'a gidiyorsa, `localhost` değil **service name** kullan (`http://backend:8001`). `docker-compose.yml`'deki servis ismine bak.

### Sorun #8 — Windows'ta line ending sorunları (`/bin/sh^M: not found` veya shell script bozuk)

Git Windows'ta dosyaları CRLF olarak çekiyor, Linux container'ı CRLF'i sevmiyor.

```bash
git config --global core.autocrlf input
```

Sonra repo'yu **yeniden klonla** (eski klon zaten CRLF'le çekildi, düzelmez):

```bash
cd ..
rm -rf paper-scout
git clone https://github.com/QatzyBURAK/paper-scout.git
```

Veya tek dosya bazında düzeltmek istersen `dos2unix script.sh`.

### Sorun #9 — Volume persistence kaybı (her restart'ta DB sıfırlanıyor)

`docker compose down` yaptın, makaleler uçtu. Bunun iki sebebi var:

1. **`-v` flag'i ile down ettin** (`docker compose down -v`) — bu **named volume'leri siler.** Sadece `docker compose down` kullan, `-v` kasten temizleme istemediğin sürece.
2. **Volume tanımı yanlış** — `docker-compose.yml`'de SQLite ve ChromaDB için bind mount veya named volume tanımlı olmalı. Kontrol et:
   ```yaml
   volumes:
     - ./backend/paper_scout.db:/app/paper_scout.db
     - ./backend/chroma_data:/app/chroma_data
   ```
   Bu satırlar yoksa veri container ölünce gider.

Test: ingest et → `docker compose down` (`-v` OLMADAN) → `docker compose up` → makaleler hâlâ olmalı.

### Sorun #10 — Apple Silicon (M1/M2/M3): build sırasında `no matching distribution` veya çok yavaş emülasyon

Bazı Python paketleri (özellikle eski PyTorch sürümleri) arm64 wheel'ı yok. Üç seçenek:

**A) Image'ı amd64 olarak zorla** (emülasyonda çalışır, biraz yavaş ama uyumlu):
```dockerfile
FROM --platform=linux/amd64 python:3.10-slim
```

**B) arm64 uyumlu sürümleri pin'le** (en iyisi ama biraz uğraş): `requirements.txt`'te PyTorch 2.x sürümü kullan, ML paketlerini arm64 destekli sürümlere güncelle.

**C) Build'de uyarıları görmezden gel**: "running under emulation" warning'i sadece uyarı, build tamamlanırsa sorun yok — sadece ilk build daha uzun.

### Sorun #11 — Build context çok büyük (`Sending build context ... 2 GB`)

`.dockerignore` eksik veya yetersiz. Repo'da `.dockerignore` olmalı, içinde en azından:

```
node_modules
.venv
__pycache__
*.pyc
.git
.chroma
*.db
.env.local
.DS_Store
```

Bu olmadan `node_modules` ve `.venv` her build'de Docker'a kopyalanır → 1-2 GB context, build çok yavaş.

### Sorun #12 — `docker compose up` çalışıyor ama kod değişiklikleri yansımıyor

Bind mount eksik veya backend `--reload` ile başlamıyor. `docker-compose.yml`'de backend servisinde:

```yaml
volumes:
  - ./backend:/app
command: uvicorn paper_scout.api.app:create_app --factory --host 0.0.0.0 --port 8001 --reload
```

olmalı. **`--reload` olmadan** dosya değişikliğinde restart gerekir.

Aynı şekilde frontend için Vite zaten hot-reload yapıyor ama bind mount lazım:

```yaml
volumes:
  - ./frontend:/app
  - /app/node_modules
```

İkinci satır (`/app/node_modules`) host'taki `node_modules`'un container'dakini ezmesini önler.

### Sorun #13 — Tarayıcı eski sürümü gösteriyor (frontend rebuild olmuş ama görünmüyor)

Vite hot-reload sonrası nadiren cache takılır. Çözüm: **`Ctrl+Shift+R`** (hard refresh) veya DevTools açıkken Network → "Disable cache".

---

## 5. Hızlı debug komutları

```bash
# Container'lar ayakta mı, ne durumda?
docker compose ps

# Log'lar (tüm servisler)
docker compose logs -f

# Sadece backend log'u
docker compose logs -f backend

# Container'ın içine gir
docker compose exec backend bash
docker compose exec frontend sh

# Backend'in /papers endpoint'i doğru mu cevap veriyor?
curl "http://localhost:8001/papers?limit=2&offset=0"
# Beklenen: {"items":[...],"total":N,"limit":2,"offset":0}

# Container'ları durdur ve sil (veri kalsın)
docker compose down

# TEMİZ başlangıç (veri DAHİL siler)
docker compose down -v
docker system prune -af   # tüm kullanılmayan image/cache'i siler, dikkat
```

---

## 6. Notlar

- Backend portu **8001**, frontend portu **5173**. Bunları değiştirirsen `docker-compose.yml` + frontend'in `.env.local`'i + backend'in CORS allowed origins'i — üçünü birden güncelle, yoksa bağlanamaz.
- Python sürümü **3.10** sabit, 3.11+ değil. Image değiştirmek istersen Dockerfile'da `python:3.10-slim` satırını koru.
- ChromaDB ve SQLite verisi **`./backend/`** altında — repo dışına yedek almak istersen bu klasörü kopyala.
- "Bende çalışıyor" testi için: `docker compose down -v && docker compose up --build` ile sıfırdan kurup tüm akışları (arama, ingest, gözat, detay) gerçekten dene. Volume persistence için ingest et, sonra `docker compose down` (`-v` OLMADAN) + `up` → veri durmalı.

Daha fazla sorun çıkarsa GitHub issue aç veya bu rehbere yeni bir Sorun #X ekle.
