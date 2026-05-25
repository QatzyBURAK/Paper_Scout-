# Paper Scout — Akademik Makale Keşif ve Analiz Aracı

**Paper Scout**, araştırma süreçlerini hızlandırmak için geliştirilmiş, anlık olarak **arXiv** ve **Semantic Scholar** üzerinden makale çekebilen, bunları yerelde akıllıca birleştirip **Hibrit Arama (Hybrid Search)** yeteneği sunan uçtan uca çalışan bir akademik arama motorudur. 

Proje, jüri ve hocalarımızın yerel bilgisayarlarında herhangi bir karmaşık ayar gerektirmeden, en kararlı ve hızlı şekilde çalıştırılabilecek şekilde hazırlanmıştır.

---

## 🔍 Proje Neler Yapabiliyor?

* **Gelişmiş Hibrit Arama (Lexical + Semantic):**
  * **Kelime Bazlı Arama (Lexical):** SQLite'ın yerleşik **FTS5** modülünü kullanarak başlık ve özet metinlerinde hızlıca anahtar kelime eşleşmesi yapar.
  * **Anlamsal Benzerlik (Semantic):** Hugging Face üzerindeki **`all-MiniLM-L6-v2`** vektör modeli ve yerel **ChromaDB** entegrasyonu sayesinde, kelimeler birebir uyuşmasa bile sorgunun anlamına en yakın makaleleri bulup getirir.
  * **Akıllı Sıralama (RRF):** Kelime bazlı ve anlamsal sonuçları akademik olarak kabul görmüş **RRF (Reciprocal Rank Fusion)** algoritmasıyla ağırlıklandırarak birleştirir; en alakalı yayınları en üste taşır.
* **Tekilleştirme ve Veri Birleştirme (Deduping & Merging):** İki farklı kaynaktan çekilen mükerrer (kopya) makaleleri başlık benzerlik analiziyle tespit eder. Atıf sayılarını günceller, en zengin özet metnini ve orijinal bağlantı adreslerini koruyarak veritabanına tek bir kayıt olarak işler.
* **Sade ve Odaklanmış Arayüz (Aesthetic UX):**
  * Uzun süre makale tarayan araştırmacılar için özel olarak seçilmiş **Sıcak Parşömen (Ink & Paper)** ve **Slate Terminal (Koyu Tema)** renk paletleri.
  * Göz yormayan, pürüzsüz skeleton loader'lar ve Framer Motion ile tasarlanmış hafif, dikkat dağıtmayan arayüz geçişleri.
  * WCAG AA standartlarına uygun metin-arka plan kontrastı ve klavyeyle tam kontrol edilebilirlik (Erişilebilirlik).

---

## 🛠️ Teknik Altyapı

* **Backend:** Python 3.10, FastAPI, SQLAlchemy (SQLite), ChromaDB, Sentence Transformers.
* **Frontend:** React 19, TypeScript, Vite, Framer Motion, Vanilla CSS Modules.

---

## 🚀 Nasıl Çalıştırılır? (Birincil ve Önerilen Yol: Docker)

Hocalarımızın ve jüri üyelerinin bilgisayarlarında Python veya Node.js sürüm uyuşmazlıklarıyla ya da paket kurulum hatalarıyla vakit kaybetmemesi için **projenin Docker Compose yardımıyla tek bir komutla ayağa kaldırılması en çok önerilen ve en kararlı yöntemdir.**

Bilgisayarınızda **Docker Desktop** uygulaması açıksa, projenin ana klasöründe terminali açıp tek bir komutla tüm uygulamayı çalıştırabilirsiniz:

```bash
docker-compose up --build
```

### Bu Komut Arka Planda Neler Yapar?
* **Tam İzolasyon:** Backend (FastAPI) ve Frontend (React) servislerini izole konteynerler içinde ayağa kaldırır.
* **Yapay Zekâ Model Belleği:** İndirilen `all-MiniLM-L6-v2` vektör modeli, ilk açılışta indirildikten sonra `hf_cache` adındaki Docker volume'unda saklanır. Sonraki çalıştırmalarda tekrar indirme yapmaz, anında açılır.
* **Veritabanı Koruma:** Yerel SQLite veritabanı dosyasını (`backend/paper_scout.db`) ve vektör verilerini (`backend/chroma_data`) bilgisayarınızın yerel diskiyle eşitler, böylece verileriniz asla kaybolmaz.
* **Nginx Gücü:** React uygulamasını Nginx sunucusu arkasında derleyerek **`http://localhost:5173`** adresinden yayına açar.

Arayüze **`http://localhost:5173`** adresinden anında erişebilirsiniz!

---

## 💻 Alternatif Yol: Yerel (Local) Manuel Kurulum

Eğer bilgisayarınızda Docker kurulu değilse, backend ve frontend bileşenlerini yerel olarak manuel kurup çalıştırmak için sırasıyla aşağıdaki adımları uygulayabilirsiniz.

### 1. Ön Hazırlık
Bilgisayarınızda **Python 3.10** ve **Node.js (v18+)** kurulu olduğundan emin olun.

---

### 2. Backend (Sunucu) Kurulumu

Çakışmaları önlemek adına backend kütüphaneleri sanal ortam (`.venv`) içine izole edilmiştir.

1. **Terminali açıp projenin ana klasörüne gidin.**
2. **Sanal ortamı oluşturun ve aktifleştirin:**
   * **Windows (PowerShell):**
     ```powershell
     python -m venv .venv
     .venv\Scripts\Activate.ps1
     ```
   * **Windows (CMD):**
     ```cmd
     python -m venv .venv
     .venv\Scripts\activate.bat
     ```
   * **macOS / Linux:**
     ```bash
     python3 -m venv .venv
     source .venv/bin/activate
     ```
3. **Backend projesini ve bağımlılıkları yükleyin:**
   ```bash
   pip install -e ./backend
   ```
4. **Sunucuyu Başlatın (Port 8001):**
   Windows ve tarayıcı ortamındaki IPv6 çözümlenme sorunlarını aşmak adına sunucuyu **tam olarak** şu komutla başlatın:
   ```bash
   cd backend
   ..\\.venv\\Scripts\\python.exe -m uvicorn paper_scout.api.app:create_app --factory --port 8001 --reload
   ```
   *(macOS kullanıcıları `../.venv/bin/python` yolunu kullanabilir).*

   Sunucu çalıştıktan sonra tarayıcınızdan `http://127.0.0.1:8001/docs` adresine giderek Swagger API dokümantasyonunu inceleyebilirsiniz.

---

### 3. Frontend (Arayüz) Kurulumu

1. **Yeni bir terminal penceresi açın ve `frontend` klasörüne geçiş yapın:**
   ```bash
   cd frontend
   ```
2. **Paketleri yükleyin:**
   ```bash
   npm install
   ```
3. **API Bağlantı Ayarı (`.env.local`):**
   Arayüzün 8001 portundaki backend ile kararlı haberleşmesi için `frontend/.env.local` dosyası aşağıdaki gibi ayarlanmıştır:
   ```env
   VITE_API_BASE_URL=http://127.0.0.1:8001
   ```
4. **Frontend'i Başlatın:**
   ```bash
   npm run dev
   ```
   Terminalde görünen yerel adrese (Örn: **`http://localhost:5173`**) tarayıcınızdan giriş yapın.

---

## 🎯 Test Etme Adımları (Adım Adım Değerlendirme)

Arayüz açıldıktan sonra sistemi şu temel senaryolarla test edebilirsiniz:

1. **Yeni Makale Çekme (Ingest):**
   * Arama kutusunun altındaki **"↓ Yeni makale çek"** butonuna basarak paneli açın.
   * Kutuya istediğiniz bir akademik konuyu yazın (Örn: `vision language model` veya `deep learning`).
   * Kaynakları (arXiv, Semantic Scholar) seçip **"Çek"** butonuna basın. Makaleler otomatik tekilleştirilerek yerel veri tabanına işlenecektir.
2. **Hibrit Arama Aşamaları:**
   * Arama kutusuna bir sorgu yazın (Örn: `transformer attention`).
   * **Keyword:** Sadece kelime eşleşmesi arar.
   * **Semantic:** Doğrudan eşleşme olmasa bile anlama en yakın sonuçları getirir.
   * **Hybrid (Önerilen):** İki gücü birleştirip en isabetli makaleleri önünüze getirir.
3. **Detaylar ve Gözat:**
   * Üst menüden **"Gözat"** sekmesine geçerek veritabanında birikmiş makalelerin tamamını görebilir ve sayfalama sistemini deneyebilirsiniz.
   * Herhangi bir makaleye tıkladığınızda açılan modal üzerinden yazarları, özeti (abstract), atıf sayılarını görebilir ve orijinal makale sayfasına yönlenebilirsiniz.

---

## 🧪 Test Süiti ve Kod Standartları

Projenin backend bileşenleri yüksek test kapsama oranına sahiptir. Sanal ortamınız aktifken `backend` klasörüne girip şu komutlarla testleri koşturabilir ve kod kalitesini denetleyebilirsiniz:

```bash
# Backend klasörüne geçin:
cd backend

# Tüm birim testlerini (139 adet) koşturmak için:
pytest

# Kod standartları denetimi (Linter):
ruff check .

# Tip güvenlik (Strict Type Checking) kontrolü:
mypy paper_scout tests --strict
```

---
*Bu çalışma, modern bilgi erişim (information retrieval) tekniklerini hem arka planda hem de ön yüzde en sade, performanslı ve kararlı haliyle bir araya getiren uçtan uca çalışan bir akademik arama motoru projesidir.*
