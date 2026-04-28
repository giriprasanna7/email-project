pipeline {
    agent any

    tools {
        nodejs 'Node25'
    }

    environment {
        GIT_REPO   = 'https://github.com/Samratstackly/stackly-email-main.git'
        GIT_BRANCH = 'main'

        SSH_KEY     = 'aws-jenkens'
        DEPLOY_USER = 'ubuntu'
        DEPLOY_HOST = '40.192.66.67'
        APP_DIR     = '/home/ubuntu/stackly-email'
    }

    stages {

        stage('Checkout Code') {
            steps {
                git url: "${GIT_REPO}", branch: "${GIT_BRANCH}"
            }
        }

        stage('Check Tools') {
            steps {
                sh '''
                set -e
                node -v
                npm -v
                '''
            }
        }

        stage('Deploy Code') {
            steps {
                sshagent([env.SSH_KEY]) {
                    sh """
                    rsync -avz --delete \
                      -e "ssh -o StrictHostKeyChecking=no" \
                      frontend django_backend email_project fastapi_app manage.py requirements.txt \
                      ${DEPLOY_USER}@${DEPLOY_HOST}:${APP_DIR}
                    """
                }
            }
        }

        stage('Remote Setup') {
            steps {
                sshagent([env.SSH_KEY]) {
                    sh """
                    ssh -o StrictHostKeyChecking=no ${DEPLOY_USER}@${DEPLOY_HOST} '
                        cd ${APP_DIR}
                        source venv/bin/activate
                        pip install -r requirements.txt
                        python manage.py migrate
                        python manage.py collectstatic --noinput
                        sudo systemctl restart gunicorn
                        sudo systemctl restart nginx
                    '
                    """
                }
            }
        }

        stage('Health Check') {
            steps {
                sshagent([env.SSH_KEY]) {
                    sh """
                    ssh -o StrictHostKeyChecking=no ${DEPLOY_USER}@${DEPLOY_HOST} '
                        curl -f http://127.0.0.1
                    '
                    """
                }
            }
        }
    }
}
