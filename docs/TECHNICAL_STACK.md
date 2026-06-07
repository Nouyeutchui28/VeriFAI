# 🛠 VeriFAI LLM: Technical Stack & Tool Inventory

This document provides a comprehensive list of the tools, libraries, and frameworks utilized across the VeriFAI LLM ecosystem for development, security analysis, and production deployment.

## 1. Core Frameworks & UI
| Tool | Purpose | Description |
| :--- | :--- | :--- |
| **Streamlit** | Frontend UI | Provides the interactive web interface for code scanning and report visualization. |
| **FastAPI** | Backend API | High-performance asynchronous API framework managing the analysis engine and data orchestration. |
| **Uvicorn** | ASGI Server | The lightning-fast server implementation used to run the FastAPI backend. |

## 2. AI & Security Analysis
| Tool | Purpose | Description |
| :--- | :--- | :--- |
| **LangChain** | LLM Orchestration | Framework for connecting LLMs with external data sources and managing prompt templates. |
| **Ollama** | Local LLM Hosting | Enables the execution of open-source LLMs (like Llama3) locally for privacy-compliant scanning. |
| **Semgrep** | Static Analysis | Lightweight, open-source static analysis tool used to find security bugs via pattern matching. |
| **Groq (Optional)** | Cloud LLM Acceleration | High-speed cloud interface for LPU-powered LLM analysis. |

## 3. Data & Persistence
| Tool | Purpose | Description |
| :--- | :--- | :--- |
| **SQLAlchemy** | ORM | SQL Toolkit and Object Relational Mapper for database interactions. |
| **PostgreSQL** | Database | Production-grade relational database for persistent storage of scan reports and user data. |
| **Alembic** | DB Migrations | Database migration tool to manage schema changes over time. |
| **Pydantic** | Data Validation | Enforces type hints and provides robust data validation for API inputs/outputs. |

## 4. Security & Utility
| Tool | Purpose | Description |
| :--- | :--- | :--- |
| **Python-Jose / Passlib** | Security | Utilities for JWT token handling, hashing, and user authentication. |
| **Dotenv** | Config Management | Manages environment variables and secrets (API keys, DB credentials). |
| **FPDF2** | Report Generation | Library for generating professional PDF security reports from analysis results. |
| **Httpx / Requests** | Communication | Asynchronous and synchronous HTTP clients for external API interactions. |

## 5. Testing & Quality Assurance
| Tool | Purpose | Description |
| :--- | :--- | :--- |
| **Pytest** | Testing Framework | The primary framework for writing unit, integration, and security tests. |
| **Pytest-Cov** | Code Coverage | Measures exactly how much of the source code is executed during testing. |
| **Black / Flake8** | Linting & Style | Enforces consistent code formatting and identifies stylistic errors. |
| **Bandit** | Security Linting | Specifically searches for common security issues in Python code. |
