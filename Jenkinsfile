pipeline {
    agent any

    options {
        timeout(time: 15, unit: 'MINUTES')   // si se cuelga, se cancela solo
        disableConcurrentBuilds()            // una ejecución a la vez
    }

    environment {
        IMAGE_NAME = 'jobtracker'
    }

    stages {
        stage('Instalar dependencias') {
            steps {
                sh '''
                    python3 -m venv .venv
                    .venv/bin/pip install --quiet -r requirements-dev.txt
                '''
            }
        }

        stage('Lint') {
            steps {
                sh '.venv/bin/ruff check .'
            }
        }

        stage('Tests') {
            steps {
                sh '.venv/bin/pytest --cov=app --cov-report=term --cov-report=xml:coverage.xml --junitxml=test-results.xml'
            }
            post {
                always {
                    junit 'test-results.xml'   // muestra los resultados en Jenkins
                }
            }
        }

        stage('Analisis SonarQube') {
            when {
                expression {
                    // Solo corre si el contenedor de SonarQube esta encendido
                    return sh(
                        returnStatus: true,
                        script: 'docker ps --filter name=^sonarqube$ --filter status=running -q | grep -q .'
                    ) == 0
                }
            }
            steps {
                withCredentials([string(credentialsId: 'sonar-token', variable: 'SONAR_TOKEN')]) {
                    sh '''
                        docker run --rm -u root \
                            --volumes-from jenkins \
                            --network jenkins_default \
                            -w "$WORKSPACE" \
                            -e SONAR_HOST_URL=http://sonarqube:9000 \
                            -e SONAR_TOKEN \
                            sonarsource/sonar-scanner-cli:latest \
                            -Dsonar.qualitygate.wait=true
                    '''
                }
            }
        }

        stage('Build imagen Docker') {
            steps {
                sh 'docker build -t ${IMAGE_NAME}:${BUILD_NUMBER} -t ${IMAGE_NAME}:latest .'
            }
        }

        stage('Escaneo de seguridad (Trivy)') {
            steps {
                sh '''
                    # 1) Reporte informativo: muestra vulnerabilidades HIGH y CRITICAL
                    docker run --rm \
                        -v /var/run/docker.sock:/var/run/docker.sock \
                        -v trivy-cache:/root/.cache/ \
                        aquasec/trivy:latest image --no-progress \
                        --severity HIGH,CRITICAL --ignore-unfixed --exit-code 0 \
                        ${IMAGE_NAME}:${BUILD_NUMBER}

                    # 2) Puerta de calidad: falla si hay CRITICAL con arreglo disponible
                    docker run --rm \
                        -v /var/run/docker.sock:/var/run/docker.sock \
                        -v trivy-cache:/root/.cache/ \
                        aquasec/trivy:latest image --no-progress \
                        --severity CRITICAL --ignore-unfixed --exit-code 1 \
                        ${IMAGE_NAME}:${BUILD_NUMBER}
                '''
            }
        }

        stage('Smoke test') {
            steps {
                sh '''
                    docker run -d --name jt-smoke-${BUILD_NUMBER} \
                        -e DATABASE_URL=sqlite:////tmp/smoke.db \
                        ${IMAGE_NAME}:${BUILD_NUMBER}

                    for i in $(seq 1 15); do
                        if docker exec jt-smoke-${BUILD_NUMBER} python -c \
                            "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"; then
                            echo "Smoke test OK"
                            exit 0
                        fi
                        sleep 2
                    done

                    echo "La app no respondio en /health"
                    docker logs jt-smoke-${BUILD_NUMBER}
                    exit 1
                '''
            }
            post {
                always {
                    sh 'docker rm -f jt-smoke-${BUILD_NUMBER} || true'
                }
            }
        }
    }

    post {
        success { echo 'Pipeline OK: la imagen esta lista.' }
        failure { echo 'Pipeline FALLO: revisa la etapa en rojo.' }
    }
}
