# Session 3 CI Lab Application

This deliberately small application supports the Jenkins lab:

- `/` returns application information.
- `/health` returns a health response.
- Unit tests validate success and failure paths.
- The Dockerfile packages the application.
- Jenkins polls the GitHub `main` branch for changes.
- The Jenkinsfile runs static validation, tests, image build, and smoke testing.
- Successful builds publish `badhansahabd/session3-demo-app:<commit>` and `latest` to Docker Hub.

The application uses only Python's standard library at runtime so trainees can focus on the CI workflow.

## Session 5 kind lab

The AWS sandbox version uses `Jenkinsfile.kind` to test, build, load, and deploy
the application into a local kind cluster. Follow the
[beginner Session 5 lab guide](docs/session-5-kind-aws-sandbox-lab.md) for the
environment, `kubectl` exercises, self-healing demonstration, and automated
GitHub-to-Kubernetes delivery flow.
