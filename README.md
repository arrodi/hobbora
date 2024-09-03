# Lurnen

## Product Description
Lurnen is a hobby project designed to create a platform where university students can either provide or consume tutoring services. The platform focuses on offering students additional, subject-specific tutoring from their peers, as well as allowing them to offer tutoring services to their classmates.

### Account Features
- **Educational Institution:** The user’s current place of study.
- **Tutoring Subjects:** A list of classes the user can tutor.
- **Tutor Rating:** The user’s rating as a tutor.
- **Student Rating:** The user’s rating as a student.
- **Preferred Communication:** The user’s preferred means of communication (Video Call/In-Person).
- **In-Person Location Options:** Available options for in-person sessions (School Library/Study Hall).

## Project Description
Lurnen primarily runs on a Kubernetes Cluster.

### Project Components
- **Front-End:** A Python Flask app that renders HTML templates.
- **Back-End API:** Handles traffic between the Flask app and the database.
- **Database:** A PostgreSQL database running as a Kubernetes StatefulSet.
