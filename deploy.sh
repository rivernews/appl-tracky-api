ABSPATH=$(cd "$(dirname "$0")"; pwd)

echo "INFO: this script is executed at ${ABSPATH}."

cd terraform && \
terraform plan || return
cd ..

if [[ $1 != "" ]];
then
    git add .
    git commit -m "${1}"
    git push
fi

cd django && \
source ./venv/bin/activate && \
cd .. && \
$(aws ecr get-login --no-include-email --region us-east-2) && \
NEW_IMAGE_TAG=$(git rev-parse --short HEAD) && \
echo "INFO: Git short hash is ${NEW_IMAGE_TAG}, we will use this as new image tag." && \
source .env.sh && source .env && echo "INFO: Run script to generate environment file, test: AWS_ECR_NGINX_REPO_URI=${AWS_ECR_NGINX_REPO_URI}" && \
(docker container stop $(docker container ls -aq) || echo "INFO: No docker container to stop") && \
docker-compose --verbose --log-level DEBUG up -d --build --remove-orphans && \
docker tag "${AWS_ECR_NGINX_REPO_URI}:latest" "${AWS_ECR_NGINX_REPO_URI}:${NEW_IMAGE_TAG}" && echo "INFO: finish tagging ${AWS_ECR_NGINX_REPO_URI}:${NEW_IMAGE_TAG}" && \
docker tag "${AWS_ECR_WEB_REPO_URI}:latest" "${AWS_ECR_WEB_REPO_URI}:${NEW_IMAGE_TAG}" && echo "INFO: finish tagging ${AWS_ECR_WEB_REPO_URI}:${NEW_IMAGE_TAG}" && \
docker push "${AWS_ECR_NGINX_REPO_URI}:latest" && \
docker push "${AWS_ECR_NGINX_REPO_URI}:${NEW_IMAGE_TAG}" && \
docker push "${AWS_ECR_WEB_REPO_URI}:latest" && \
docker push "${AWS_ECR_WEB_REPO_URI}:${NEW_IMAGE_TAG}" && \
echo "SUCCESS! ECR image ready." && \
echo "Now running orchestration tool to update service..." && \
cd terraform && \
terraform apply -var="ecr_new_image_tag=${NEW_IMAGE_TAG:-latest}" -auto-approve && \
cd .. && \
echo "SUCCESS! Allow several minutes for change to take effect on production server. Take some rest and have a cup of coffee! Then go to the url and check it out." && return

echo Info: error occurred, reverting to original path...
cd "${ABSPATH}"
echo "ERROR: see above message. Reminder: make sure to check if Docker app is turned on."