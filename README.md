# Hobbora

## Product Description
Hobbora is a hobby project designed to create a platform where university students can either provide or consume tutoring services. The platform focuses on offering students additional, subject-specific tutoring from their peers, as well as allowing them to offer tutoring services to their classmates.

### Account Features
- **Educational Institution:** The user’s current place of study.
- **Tutoring Subjects:** A list of classes the user can tutor.
- **Tutor Rating:** The user’s rating as a tutor.
- **Student Rating:** The user’s rating as a student.
- **Preferred Communication:** The user’s preferred means of communication (Video Call/In-Person).
- **In-Person Location Options:** Available options for in-person sessions (School Library/Study Hall).

## Project Description
Hobbora primarily runs on a Kubernetes Cluster.

### Project Components
- **Front-End:** A Python Flask app that renders HTML templates.
- **Back-End API:** Handles traffic between the Flask app and the database.
- **Database:** A PostgreSQL database running as a Kubernetes StatefulSet.

---

# Development info

## Python Virtual Environment Setup

To set up a Python virtual environment and perform local development, we need to create a `VENV` and add a `.env.bat` file that the environment will use.

**Create the VENV**
1. Open a `CMD` terminal and navigate to the path where you want your venv stored
2. Create the virtual environment by running `python -m venv {name-of-venv}`
3. Activate the VENV by running the path to the `activate` file

**Populate VENV with variables**
1. Create a `.env.bat` file in {name-of-venv}/bin folder to store your enviroment variables
2. Populate the `.env.bat` file with variables in the format `export {env_name}="{env_string}"` (variables can only be strings)
3. Run the command `source {relative_path/.env.bat}`. This will print out the variables and add them to your VENV
4. !IMPORTANT: Make sure to add the VENV folder to your `.gitignore` file to prevent pushing secrets to your repo

**Pip install packages from non-standard repository**
1. To install one package: `pip install {package_name} -i {repo_url}`
2. To install all libraries on the requirements file: `pip install -r {requirements_file_full_path} -i {repo_url}`

**Deactivate the VENV**
1. Deactivate the VENV by running the path of the 'deactivate' file

---

## Microservice Environment Variables

### Picture API (`microservices/picture-api`)

The Picture API requires the following environment variables in your `.env.bat` file:

```bash
export S3_HOST="your_s3_host"
export S3_USER="your_s3_user"
export S3_PASS="your_s3_password"
export APP_HOST="0.0.0.0"
export APP_PORT="5000"
export PICTURE_BUCKET="your_picture_bucket"
export DEFAULT_PROFILE_PIC_PATH="your_default_profile_pic_path"
export DEFAULT_HOBBY_PIC_PATH="your_default_hobby_pic_path"
```

**Running the Picture API locally:**
```bash
source _venv/venv_picture_api/bin/activate
source _venv/venv_picture_api/bin/.env.bat
python microservices/picture-api/src/server.py
```

### Postgres DB API (`microservices/postgres-db-api`)

The Postgres DB API requires the following environment variables in your `.env.bat` file:

```bash
export POSTGRES_DB="your_database_name"
export POSTGRES_USER="your_postgres_user"
export POSTGRES_PASSWORD="your_postgres_password"
export POSTGRES_HOST="localhost"
export POSTGRES_PORT="5432"
export APP_HOST="0.0.0.0"
export APP_PORT="5001"
```

**Running the Postgres DB API locally:**
```bash
source _venv/venv_posgres_db_api/bin/activate
source _venv/venv_posgres_db_api/bin/.env.bat
python microservices/postgres-db-api/src/server.py
```

### Web UI (`microservices/web-ui`)

The Web UI requires the following environment variables in your `.env.bat` file:

```bash
export APP_HOST="0.0.0.0"
export APP_PORT="8000"
export DB_API_URL="http://localhost:8001"
export PICTURE_API_URL="http://localhost:8002"
```

**Running the Web UI locally:**
```bash
source _venv/venv_web_ui/bin/activate
source _venv/venv_web_ui/bin/.env.bat
python microservices/web-ui/src/server.py
```
