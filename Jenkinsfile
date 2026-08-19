pipeline {
    agent any

    options {
        timestamps()
        disableConcurrentBuilds()
        timeout(time: 15, unit: 'MINUTES')
    }

    triggers {
        pollSCM('H/2 * * * *')
    }

    environment {
        IMAGE_NAME = 'session3-training-app'
        SMOKE_CONTAINER = "session3-smoke-${BUILD_NUMBER}"
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
                sh 'git rev-parse --short HEAD'
            }
        }

        stage('Static Check') {
            steps {
                sh '''
                    docker run --rm \
                      -v "$WORKSPACE:/workspace" \
                      -w /workspace \
                      python:3.12-slim \
                      python -m py_compile app.py
                '''
            }
        }

        stage('Unit Tests') {
            steps {
                sh '''
                    mkdir -p reports
                    docker run --rm \
                      --user "$(id -u):$(id -g)" \
                      -e HOME=/tmp \
                      -v "$WORKSPACE:/workspace" \
                      -w /workspace \
                      python:3.12-slim \
                      sh -c 'python -m pip install --quiet --target /tmp/pytest -r requirements-dev.txt && PYTHONPATH=/tmp/pytest python -m pytest --junitxml=reports/junit.xml'
                '''
            }
        }

        stage('Build Image') {
            steps {
                sh 'docker build --tag ${IMAGE_NAME}:${BUILD_NUMBER} .'
            }
        }

        stage('Smoke Test') {
            steps {
                sh '''
                    docker rm -f "$SMOKE_CONTAINER" >/dev/null 2>&1 || true
                    docker run --detach --name "$SMOKE_CONTAINER" "$IMAGE_NAME:$BUILD_NUMBER"

                    ready=0
                    for attempt in $(seq 1 20); do
                      if docker exec "$SMOKE_CONTAINER" python -c "import urllib.request; response=urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=2); assert response.status == 200"; then
                        ready=1
                        break
                      fi
                      sleep 1
                    done

                    if [ "$ready" -ne 1 ]; then
                      docker logs "$SMOKE_CONTAINER"
                      exit 1
                    fi
                '''
            }
        }

        stage('Publish Evidence') {
            steps {
                sh '''
                    printf 'image=%s:%s\ncommit=%s\nbuild=%s\n' \
                      "$IMAGE_NAME" \
                      "$BUILD_NUMBER" \
                      "$(git rev-parse HEAD)" \
                      "$BUILD_TAG" \
                      > reports/build-metadata.txt
                '''
                archiveArtifacts artifacts: 'reports/**', fingerprint: true
            }
        }
    }

    post {
        always {
            junit allowEmptyResults: true, testResults: 'reports/junit.xml'
            sh 'docker rm -f "$SMOKE_CONTAINER" >/dev/null 2>&1 || true'
        }
        success {
            echo "Trusted image created: ${IMAGE_NAME}:${BUILD_NUMBER}"
        }
        failure {
            echo 'Pipeline failed. Read the first failing stage and its command output.'
        }
    }
}
