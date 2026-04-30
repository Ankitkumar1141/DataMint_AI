# DataMint AI

DataMint AI is an end-to-end Streamlit application for generating realistic synthetic datasets for machine learning experiments. The project uses Mistral AI to generate a dataset schema and Python to generate the full dataset locally, making the application faster, more reliable, and suitable for larger row counts.

## Features

- User registration and login
- Secure password hashing using bcrypt
- MySQL database integration
- Mistral AI schema generation
- Local Python-based dataset generation
- Support for multiple ML task types
- Support for multiple industry domains
- CSV and Excel export
- Docker and Docker Compose support
- Modular project structure
- Basic testable architecture

## Project Architecture

```text
DataMint/
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env
├── .streamlit/
│   └── secrets.toml
├── src/
│   └── datamint/
│       ├── __init__.py
│       ├── app.py
│       ├── config.py
│       ├── db/
│       │   ├── __init__.py
│       │   ├── connection.py
│       │   └── schema.py
│       ├── services/
│       │   ├── __init__.py
│       │   ├── auth.py
│       │   └── dataset.py
│       ├── ui/
│       │   ├── __init__.py
│       │   ├── auth_page.py
│       │   └── generator_page.py
│       └── utils/
│           └── __init__.py
└── tests/
    ├── test_auth.py
    └── test_data_validation.py
```

## How It Works

The project follows a schema-first generation pipeline:

```text
User Input
   ↓
Mistral AI generates dataset schema
   ↓
Python generates rows locally
   ↓
Dataset is validated
   ↓
Dataset is displayed in Streamlit
   ↓
User downloads CSV or Excel file
```

Instead of asking Mistral AI to generate hundreds or thousands of rows directly, DataMint AI asks Mistral only for the schema: column names, data types, ranges, categories, and descriptions. Python then generates the requested number of rows locally. This reduces timeout errors, lowers API usage, and improves reliability.

## Technology Stack

| Layer | Technology |
|---|---|
| Frontend | Streamlit |
| Backend | Python |
| AI Provider | Mistral AI |
| Database | MySQL |
| Data Processing | pandas |
| Password Security | bcrypt |
| Export | CSV, Excel |
| Containerization | Docker, Docker Compose |
| Testing | pytest |

## Main Modules

### `app.py`

Main Streamlit entry point. It loads settings, initializes the database schema, and renders either the authentication page or the dataset generator page.

### `config.py`

Loads application settings from `.env` or `.streamlit/secrets.toml`, including:

- MySQL host
- MySQL port
- MySQL user
- MySQL password
- MySQL database
- Mistral API key
- Mistral model name

### `db/connection.py`

Creates a reusable MySQL database connection using project settings.

### `db/schema.py`

Creates required database tables:

- `users`
- `generated_datasets`

### `services/auth.py`

Handles authentication logic:

- User registration
- Password hashing
- Password verification
- User login

### `services/dataset.py`

Handles dataset generation logic:

- Sends schema request to Mistral AI
- Parses JSON schema
- Generates rows locally using Python
- Validates row and column counts
- Saves dataset metadata
- Converts DataFrame to Excel bytes

### `ui/auth_page.py`

Contains the login and registration UI.

### `ui/generator_page.py`

Contains the dataset generation UI, including:

- Feature slider
- Row slider
- ML task selector
- Domain selector
- Dataset description input
- Dataset preview
- CSV and Excel download buttons

## Supported ML Tasks

- Classification
- Regression
- Clustering
- Time Series
- NLP / Text Classification
- Anomaly Detection
- Recommendation

## Supported Domains

- Healthcare
- Finance
- Education
- Defense
- E-commerce
- Agriculture
- Transportation
- Manufacturing
- Energy
- Real Estate
- HR & Recruitment
- Cybersecurity
- Retail
- Sports Analytics
- Environment & Climate

## Environment Variables

Create a `.env` file in the project root.

```env
MYSQL_HOST=db
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=root123
MYSQL_DATABASE=Datamint_AI

MISTRAL_API_KEY=your_mistral_api_key_here
MISTRAL_MODEL=mistral-small-latest
```

For local Streamlit-only execution without Docker, use:

```env
MYSQL_HOST=127.0.0.1
MYSQL_PORT=3306
MYSQL_USER=user
MYSQL_PASSWORD=password
MYSQL_DATABASE=Datamint_AI

MISTRAL_API_KEY=your_mistral_api_key_here
MISTRAL_MODEL=mistral-model
```

## Streamlit Secrets

You can also store secrets in `.streamlit/secrets.toml`.

```toml
[mysql]
HOST = "127.0.0.1"
PORT = 3306
USER = "root"
PASSWORD = "root123"
DATABASE = "Datamint_AI"

[keys]
MISTRAL_API_KEY = "your_mistral_api_key_here"
MISTRAL_MODEL = "mistral-small-latest"
```

For Docker Compose, use:

```toml
[mysql]
HOST = "db"
PORT = 3306
USER = "root"
PASSWORD = "root123"
DATABASE = "Datamint_AI"
```

## Installation Without Docker

### 1. Create virtual environment

```bash
python -m venv datamint_venv
```

### 2. Activate virtual environment

Windows CMD:

```cmd
datamint_venv\Scripts\activate
```

Windows PowerShell:

```powershell
.\datamint_venv\Scripts\Activate.ps1
```

macOS/Linux:

```bash
source datamint_venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Start MySQL

If using Docker only for MySQL:

```bash
docker compose up db
```

### 5. Run Streamlit

Windows CMD:

```cmd
set PYTHONPATH=src && streamlit run src/datamint/app.py
```

Windows PowerShell:

```powershell
$env:PYTHONPATH="src"
streamlit run src/datamint/app.py
```

macOS/Linux:

```bash
PYTHONPATH=src streamlit run src/datamint/app.py
```

Open the application at:

```text
http://localhost:8501
```

## Docker Setup

### Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

ENV PYTHONPATH=/app/src
ENV PYTHONUNBUFFERED=1

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "src/datamint/app.py", "--server.address=0.0.0.0", "--server.port=8501"]
```

### docker-compose.yml

```yaml
services:
  db:
    image: mysql:8.0
    container_name: datamint-db
    restart: always
    environment:
      MYSQL_ROOT_PASSWORD: root123
      MYSQL_DATABASE: Datamint_AI
    ports:
      - "3306:3306"
    volumes:
      - datamint_mysql_data:/var/lib/mysql
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost", "-uroot", "-proot123"]
      interval: 10s
      timeout: 5s
      retries: 10

  app:
    build: .
    container_name: datamint-app
    restart: always
    ports:
      - "8501:8501"
    env_file:
      - .env
    depends_on:
      db:
        condition: service_healthy

volumes:
  datamint_mysql_data:
```

## Run With Docker Compose

From the project root:

```bash
docker compose up --build
```

Open:

```text
http://localhost:8501
```

Run in detached mode:

```bash
docker compose up --build -d
```

View logs:

```bash
docker compose logs -f app
```

Stop containers:

```bash
docker compose down
```

Stop and remove database volume:

```bash
docker compose down -v
```

Use `down -v` only when you want to delete database data.

## Push Docker Image to Docker Hub

### 1. Login

```bash
docker login
```

### 2. Build image

```bash
docker build -t your-dockerhub-username/datamint-ai:latest .
```

Example:

```bash
docker build -t john123/datamint-ai:latest .
```

### 3. Push image

```bash
docker push your-dockerhub-username/datamint-ai:latest
```

Example:

```bash
docker push john123/datamint-ai:latest
```

### 4. Use pushed image in Docker Compose

Replace:

```yaml
app:
  build: .
```

with:

```yaml
app:
  image: your-dockerhub-username/datamint-ai:latest
```

Then run:

```bash
docker compose up
```

## Testing

Run all tests:

```bash
PYTHONPATH=src pytest -v
```

Windows CMD:

```cmd
set PYTHONPATH=src && pytest -v
```

Windows PowerShell:

```powershell
$env:PYTHONPATH="src"
pytest -v
```

Run a specific test file:

```bash
PYTHONPATH=src pytest tests/test_auth.py -v
```

```bash
PYTHONPATH=src pytest tests/test_data_validation.py -v
```

## Full Pipeline Test

Use this checklist to verify the full application:

```text
[ ] Docker Compose starts successfully
[ ] MySQL container is healthy
[ ] Streamlit app opens on localhost:8501
[ ] User registration works
[ ] User login works
[ ] Dataset description is required
[ ] Mistral generates schema successfully
[ ] Python generates the requested number of rows
[ ] Dataset appears in Streamlit preview
[ ] CSV download works
[ ] Excel download works
[ ] Dataset metadata is saved in MySQL
[ ] Logout works
```

## Common Errors and Fixes

### `MISTRAL_API_KEY is missing`

Add your key to `.env` or `.streamlit/secrets.toml`.

```env
MISTRAL_API_KEY=your_mistral_api_key_here
```

### `Unknown MySQL server host 'db'`

You are running Streamlit locally. Use:

```env
MYSQL_HOST=127.0.0.1
```

Use `MYSQL_HOST=db` only when running inside Docker Compose.

### `The read operation timed out`

This usually happens when asking the model to generate too much content. The current schema-first pipeline avoids this by asking Mistral only for schema and generating rows locally.

### `cannot import name get_settings`

Make sure `config.py` contains:

```python
@lru_cache
def get_settings() -> Settings:
    return Settings()
```

### `cannot import name Mistral from mistralai`

Upgrade the Mistral SDK:

```bash
pip uninstall mistralai -y
pip install --upgrade mistralai
```

## Performance Improvement

The main performance improvement in DataMint AI is schema-first generation.

Old approach:

```text
Mistral AI generates all rows directly
```

Problems:

- Slow generation
- Timeout errors
- Token limit issues
- Wrong row counts
- Invalid JSON for large datasets

New approach:

```text
Mistral AI generates schema only
Python generates all rows locally
```

Benefits:

- Faster dataset generation
- Exact row count
- Exact column count
- Fewer API tokens
- Larger dataset support
- Better reliability

## Recommended Mistral Model

For development and demos:

```text
mistral-small-latest
```

For better schema quality:

```text
mistral-large-latest
```

## Example Dataset Prompt

```text
Customer loan approval dataset with age, income, loan amount, credit score, employment status, loan purpose, and approval status.
```

## Future Enhancements

- Add user dashboard for previous datasets
- Add dataset history page
- Add advanced schema editor
- Add missing value generation options
- Add noise/outlier generation
- Add correlation between columns
- Add train/test split download
- Add support for local LLMs
- Add admin analytics dashboard
- Add deployment to cloud platforms

## License

This project is intended for educational and demonstration purposes.

## Author
Ankit kumar
DataMint AI project.
