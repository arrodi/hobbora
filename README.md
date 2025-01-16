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

## Python Virtual Enviroment Setup

To setup a python virtual enviroment and perform local development we need to create a `VENV` and add a `.env.bat` file that the enviroment will use.

**Create the VENV**
1. Open a `CMD` terminal and navigate to the path where you want your venv stored
2. Create the virtual enviroment by running `python -m venv {name-of-venv}`
3. Activate the VENV by running the path of the 'activate' file

**Populate VENV with variables**
1. Create a `.env.bat` file in {name-of-venv}/Scripts folder to store your enviroment variables
2. Populate the `.env.bat` file with variables in format `set {env_name}={env_string}` Note: variables can only be strings
3. Run the command `call {relative_path/.env.bat}`. This will print out the variables and add them to your VENV
4. !IMPORTANT: Make sure to add the VENV folder to your `.gitignore` file to prevent pushing secrets to your repo

**Pip install packages from non-standard repository**
1. To install one package: `pip install {package_name} -i {repo_url}`
2. To install all libraries on the requirements file: `pip install -r {requirements_file_full_path} -i {repo_url}`

**Deactivate the VENV**
1. Deactivate the VENV by running the path of the 'deactivate' file
