# Contributing to File Sorter Enterprise

First off, thank you for considering contributing to File Sorter Enterprise! It's people like you that make the open source community such an incredible place to learn, inspire, and create.

## How to Contribute

### 1. Reporting Bugs
- Ensure the bug was not already reported by searching on GitHub under Issues.
- If you're unable to find an open issue addressing the problem, open a new one. Be sure to include a title and clear description, as much relevant information as possible, and a code sample or an executable test case demonstrating the expected behavior that is not occurring.

### 2. Suggesting Enhancements
- Open a new issue with a clear title and description.
- Explain why this enhancement would be useful to most users.
- Include a specific example of how this enhancement will be used in enterprise environments.

### 3. Pull Requests
1. Fork the repo and create your branch from `main`.
2. Ensure you have installed all dependencies listed in `setup_and_run.py`.
3. If you've added new features, ensure they are documented (using Google-style Python docstrings).
4. Run the automated standard tests (if applicable) and verify the `setup_and_run.py` UI still runs properly.
5. Create the PR describing the changes precisely.

## Coding Guidelines
- **Python**: We follow PEP8. Please use `black` for formatting and `flake8` for linting.
- **English Language**: All code documentation, Pull Request messages, and commit logs MUST be in English.
- **Docstrings**: We use the Sphinx/Google docstring standard for auto-generating docs.

## Strategic Contribution Goals

To align community efforts with our enterprise strategy, we actively request contributions in the following domains:

- **Future Needs & Scalability (Criterion 6e):** We are looking for AI developers to integrate local LLMs into the Python agent to classify files by *content* rather than just extension.
- **System Integrations (Criterion 6i):** We invite data engineers to develop Webhooks interacting with our OpenAPI (`/docs`) in order to connect *File Sorter* telemetry directly to SAP, Microsoft Dynamics, or Salesforce.
- **Human Resources & Training (Criterion 6k):** To collaborate, you will need a strong background in **Asynchronous Python (FastAPI)** and **Event-Driven UI (CustomTkinter)**. We have prepared an explicit html-based reference accessible in our `docs/` folder to serve as the initial onboarding training material for new developers.

Once again, thank you for making this project better!
