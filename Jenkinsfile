
pipeline {
    agent any

    options {
        timestamps()
        disableConcurrentBuilds()
        skipDefaultCheckout(true)
    }

    environment {
        COMPOSE_PROJECT_NAME = 'employee-directory-search-system'
        FRONTEND_URL = 'http://host.docker.internal:3017'
        BACKEND_URL = 'http://host.docker.internal:8007'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
                sh '''
                    echo "Repository checked out."
                    git log -1 --oneline
                    test -f docker-compose.yml
                    test -f backend/Dockerfile
                    test -f frontend/Dockerfile
                '''
            }
        }

        stage('Prepare Environment') {
            steps {
                withCredentials([
                    string(
                        credentialsId: 'employee-db-password',
                        variable: 'DB_PASSWORD'
                    )
                ]) {
                    sh '''
                        set +x
                        umask 077
                        printf 'DB_NAME=employee_directory\\nDB_PASSWORD=%s\\n' \
                            "$DB_PASSWORD" > .env
                        test -s .env
                    '''
                }
            }
        }

        stage('Validate Compose') {
            steps {
                sh 'docker compose config -q'
            }
        }

        stage('Build Images') {
            steps {
                sh 'docker compose build'
            }
        }

        stage('Deploy') {
            steps {
                sh '''
                    docker compose up -d --remove-orphans
                    docker compose ps
                '''
            }
        }

        stage('Smoke Tests') {
            steps {
                sh '''
                    set -eu

                    echo "Checking backend..."
                    backend_ok=0

                    for i in $(seq 1 30); do
                        if curl --connect-timeout 3 --fail --silent \
                            "$BACKEND_URL/" \
                            -o /tmp/employee-directory-api.json; then
                            backend_ok=1
                            break
                        fi
                        sleep 2
                    done

                    if [ "$backend_ok" -ne 1 ]; then
                        echo "Backend smoke test failed."
                        exit 1
                    fi

                    cat /tmp/employee-directory-api.json

                    echo "Checking frontend..."
                    curl --connect-timeout 5 --fail --silent \
                        "$FRONTEND_URL/" \
                        -o /tmp/employee-directory-index.html

                    grep -qi '<html' /tmp/employee-directory-index.html

                    echo "Frontend and backend smoke tests passed."
                '''
            }
        }
    }

    post {
        success {
            echo 'Employee Directory deployment and smoke tests succeeded.'
        }

        failure {
            echo 'Pipeline failed. Collecting Docker diagnostics.'

            sh '''
                docker ps -a
                docker logs --tail=80 employee-directory-mysql || true
                docker logs --tail=80 employee-directory-backend || true
                docker logs --tail=80 employee-directory-frontend || true
            '''
        }

        always {
            sh 'rm -f .env'
            sh 'rm -f /tmp/employee-directory-api.json /tmp/employee-directory-index.html'
        }
    }
}
