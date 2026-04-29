# File Sorter Enterprise

File Sorter Enterprise is an automated, AI-assisted file governance system that rescues unstructured drives from digital chaos. It actively monitors, categorizes, and organizes inbound files (documents, media, installations) into highly rigid directory structures while broadcasting real-time metrics to a cloud-based web dashboard.

## Live Demo
You can try out the modernized SaaS web dashboard without installing anything:
🌐 **[Live Demo on Vercel](https://filesorterv1.vercel.app/index.html)**

## Prerequisites
- Python 3.10+
- SQLite (built-in Python)
- Windows, macOS, or Linux (OS Independent)

## Step-by-Step Installation

```bash
# 1. Clone the repository
git clone https://github.com/NexMediaSolutions/file_sorter.git
cd file_sorter

# 2. Create and activate a Virtual Environment
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Setup the environment configuration
cp .env.example .env

# 5. Boot both the Cloud Backend and the Desktop Agent Node
python setup_and_run.py
```

## Quick Usage Example

1. Open the File Governance System Desktop UI.
2. Click on **Login** or **Register** to sync with your Cloud account.
3. In the Home menu, Drag & Drop any chaotic folder (e.g., `C:/Users/You/Downloads`) into the Dropzone.
4. Click **Start Organization**. The system will scan your files and group them into Folders like `Images`, `Documents`, and `Videos`.
5. Access the `<IP>:8000` web dashboard to see your company-wide file synchronization metrics in real-time.

## Project Structure

```text
file_sorter/
├── src/
│   ├── agent/             # CustomTkinter Desktop Client Source
│   │   ├── models/        # Application states, UI themes
│   │   ├── services/      # Cloud REST API Clients & HTTP handlers
│   │   └── views/         # Graphical Apple HIG UI components
│   └── backend/           # FastAPI Cloud Server Source
│       ├── api/           # Router Endpoints (v1)
│       └── core/          # JWT Security & Password Cryptography
├── tests/                 # Pytest Assertions for logic validation
├── landing/               # HTML/CSS Frontend code for the Web Dashboard
├── setup_and_run.py       # Orchestrator to boot FastAPI & Desktop UI simultaneously
└── verify_script.py       # Automated system integrity checks
```

## Environment Variables (.env)

| Variable | Description | Example | Required |
| --- | --- | --- | --- |
| `SECRET_KEY` | Hexadecimal signature key used to sign JWT Tokens | `0x9abcd1234...` | **Yes** |
| `ALGORITHM` | JWT Signature algorithm | `HS256` | Yes |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Lifecycle of user tokens | `30` | No |
| `DATABASE_URL` | SQLite / PostgreSQL URI connection | `sqlite:///./enterprise.db` | No |
| `SMTP_USER` | Email account for sending 2FA Codes and Audit Reports | `noreply@mycorp.com` | No (if offline) |
| `SMTP_PASSWORD` | App Password to authenticate the SMTP agent | `xxxx xxxx xxxx xxxx` | No (if offline) |

## Running Tests

We use `pytest` for all continuous integration hooks. To validate the latest build:

```bash
# Ensure you are on the virtual environment
pytest -v tests/
```
You can generate a test coverage report using:
```bash
coverage run -m pytest
coverage report -m
```

## Contributing
1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request
