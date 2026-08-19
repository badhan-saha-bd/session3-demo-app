# Session 3 CI Lab Application

This deliberately small application supports the Jenkins lab:

- `/` returns application information.
- `/health` returns a health response.
- Unit tests validate success and failure paths.
- The Dockerfile packages the application.
- The Jenkinsfile runs static validation, tests, image build, smoke testing, and evidence publication.

The application uses only Python's standard library at runtime so trainees can focus on the CI workflow.
