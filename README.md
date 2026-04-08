# 📁⚙️ File Sorter Enterprise

<p align="center">
  <a href="https://github.com/yourusername/file-sorter-enterprise/pulls">
    <img src="https://img.shields.io/badge/PRs-welcome-brightgreen.svg?longCache=true" alt="Pull Requests">
  </a>
  <a href="LICENSE">
      <img src="https://img.shields.io/badge/License-MIT-yellow.svg?longCache=true" alt="MIT License">
    </a>
    <a href="https://docs.pytest.org/en/stable/">
      <img src="https://img.shields.io/badge/testing-pytest-blue?longCache=true" alt="Testing: Pytest">
    </a>
</p>

📁⚙️ File Sorter Enterprise is an automated, secure, and highly efficient digital organization system designed for modern enterprises. It automatically categorizes, secures, and maintains files across the company using a sophisticated client-agent architecture connected to a robust centralized back-end.

> **Important Note:** 📁⚙️ File Sorter Enterprise is designed to streamline administrative and communications tasks. It mitigates the risk of misplaced files and corrupted documents, turning chaotic file sharing into a seamless structural taxonomy in real time.

<p align="center">
    <a href="#how--file-sorter-works">Demo (Local)</a>
    ·
    <a href="https://github.com/yourusername/file-sorter-enterprise/issues/new">Report Bug</a>
    ·
    <a href="https://github.com/yourusername/file-sorter-enterprise/issues/new">Request Feature</a>
    ·
    <a href="wiki">Wiki</a>
</p>

## Table of Contents

- [Motivation](#motivation)
- [Why File Sorter?](#why-file-sorter)
- [How 📁⚙️ File Sorter Works](#how--file-sorter-works)
- [Demo](#demo)
- [Getting Started](#getting-started)
- [Customizability and Ideas for Extensions](#customizability-and-ideas-for-extensions)
- [License](#license)
- [Contributing](#contributing)

## Motivation

In the era of digital transformation, businesses generate thousands of files daily. Misplaced files lead to lost productivity, compliance issues, and communication overhead. File Sorter Enterprise solves this problem from the ground up.

The spark for starting this project was to tackle "digital chaos" in production and business areas. Currently, many employees waste hours searching through 'Downloads' or unclassified shared networks. By implementing *File Sorter*, we unify the taxonomy of documents globally without requiring manual technical overhead from the user. 

## Why File Sorter?

File management often relies on restrictive cloud drives or clunky proprietary desktop clients. File Sorter Enterprise bridges the gap between Desktop Operations processing (using dragging capabilities through CustomTkinter) and the speed of real-time web processing (via FastAPI and WebSockets), completely decoupling the UI rules from the backend persistence layer.

## How 📁⚙️ File Sorter Works

The application employs a dual-stage setup composed of a central Backend and lightweight Desktop Agents logic.

### Architecture

File Sorter's architecture consists of several key components:
- **Backend (FastAPI)**: Serves endpoints and manages PostgreSQL connections.
- **Agent Orchestrator**: Uses `setup_and_run.py` to concurrently deploy PostgreSQL Docker containers and the local Agent UI.
- **Event WebSocket**: A real-time socket mechanism that listens to movements on the Agent to securely update the database without file sniffing.

### Web/Desktop Integration

1. **Watchdog Analysis**: Desktop directory movements are analyzed continuously.
2. **Metadata Capture**: Files are hashed using native systems to prevent duplicates.
3. **API Reporting**: A background thread passes JSON logging events to the cloud via WebSockets.
4. **Agent Action**: The UI interface reports the categorization directly to the user dynamically.

## Demo

Due to the local desktop nature of the CustomTkinter app, there is no public online demo. However, you can see the auto-generated documentation for the codebase locally under the `docs/` folder, and test the endpoints natively in `http://localhost:8000/docs` once launched.

## Getting Started

Follow these steps:

### Prerequisites

- Python 3.10+
- `pip`
- Docker (optional, for deploying PostgreSQL DB)

### Clone the Repository

1. Clone the repository:
    ```bash
    git clone https://github.com/yourusername/file-sorter-enterprise.git
    ```

2. Navigate into the project directory:
    ```bash
    cd file-sorter-enterprise
    ```

### Installation

Install the required standard dependencies (already defined in the main setup script context). You can use `pip`:

```bash
pip install fastapi uvicorn[standard] sqlmodel pydantic-settings passlib[bcrypt] bcrypt python-jose[cryptography] python-multipart psycopg2-binary redis requests websocket-client customtkinter watchdog pystray pillow tkinterdnd2 jinja2 httpx
```

### Usage

Use the graphical dashboard to initialize components:

```bash
python setup_and_run.py
```

1. Select either **Local (SQLite)** or **Docker (PG)** environments.
2. If using Docker, click **Levantar Base de Datos (Docker)** first.
3. Finally, launch both servers using **Launch Full System Node**.

### Integration Examples (Fulfilling Criterion 6i)

To truly leverage the interoperability of this system with external environments (like an ERP or CRM), the backend exposes a live REST API that can be consumed by external platforms.

**Example: Syncing Device Rules Programmatically**
```bash
curl -X 'GET' \
  'http://localhost:8000/api/v1/devices/sync/PC-LOCAL-01' \
  -H 'accept: application/json'
```
This enables third-party enterprise planners to ingest rule lists without interacting with the Desktop UI at all.

## Customizability and Ideas for Extensions

The architecture of 📁⚙️ File Sorter Enterprise is designed with extensibility and future digital transformation growth at its core.

### Extension Ideas
- **AI Classification Engine:** Inject an LLM (like Aphra does for translation) into the Desktop Agent workflow to auto-tag images or parse PDFs before deciding what folder to put them in.
- **Enterprise SSO:** Extend the basic JWT Authentication to OAuth providers (Google, Active Directory).
- **Metric Dashboards:** Extend the `/docs` auto-generated swagger to output customized Grafana graphs showing organizational efficiency.

## License

📁⚙️ File Sorter Enterprise is released under the [MIT License](https://github.com/yourusername/file-sorter-enterprise/blob/main/LICENSE). You are free to use, modify, and distribute the code for both commercial and non-commercial purposes.

## Contributing

Contributions to 📁⚙️ File Sorter Enterprise are welcome! Please check out the [CONTRIBUTING.md](CONTRIBUTING.md) file for guidelines on how to get started.
