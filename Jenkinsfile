pipeline {
    agent any

    options {
        timestamps()
        disableConcurrentBuilds()
        timeout(time: 15, unit: 'MINUTES')
    }

    triggers {
        pollSCM('* * * * *')
    }

    environment {
        IMAGE_REPOSITORY = 'badhansahabd/session3-demo-app'
        SMOKE_CONTAINER = "session3-smoke-${BUILD_NUMBER}"
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
                script {
                    env.IMAGE_TAG = sh(
                        script: 'git rev-parse --short=12 HEAD',
                        returnStdout: true
                    ).trim()
                }
                echo "Immutable image tag: ${IMAGE_TAG}"
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
                sh 'docker build --tag ${IMAGE_REPOSITORY}:${IMAGE_TAG} .'
            }
        }

        stage('Smoke Test') {
            steps {
                sh '''
                    docker rm -f "$SMOKE_CONTAINER" >/dev/null 2>&1 || true
                    docker run --detach --name "$SMOKE_CONTAINER" "$IMAGE_REPOSITORY:$IMAGE_TAG"

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

        stage('Push to Docker Hub') {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'dockerhub-credentials',
                    usernameVariable: 'DOCKERHUB_USERNAME',
                    passwordVariable: 'DOCKERHUB_TOKEN'
                )]) {
                    sh 'printf %s "$DOCKERHUB_TOKEN" | docker login --username "$DOCKERHUB_USERNAME" --password-stdin'
                    script {
                        try {
                            sh '''
                                docker push "$IMAGE_REPOSITORY:$IMAGE_TAG"
                                docker tag "$IMAGE_REPOSITORY:$IMAGE_TAG" "$IMAGE_REPOSITORY:latest"
                                docker push "$IMAGE_REPOSITORY:latest"
                            '''
                        } finally {
                            sh 'docker logout >/dev/null 2>&1 || true'
                        }
                    }
                }
            }
        }

        stage('Publish Evidence') {
            steps {
                sh '''
                    printf 'image=%s\nimmutable_tag=%s\nlatest_tag=%s\ncommit=%s\nbuild=%s\n' \
                      "$IMAGE_REPOSITORY" \
                      "$IMAGE_TAG" \
                      latest \
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
            echo "Published ${IMAGE_REPOSITORY}:${IMAGE_TAG} and ${IMAGE_REPOSITORY}:latest"
        }
        failure {
            echo 'Pipeline failed. Read the first failing stage and its command output.'
        }
    }
}
