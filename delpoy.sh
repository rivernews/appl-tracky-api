ABSPATH=$(cd "$(dirname "$0")"; pwd)

echo "INFO: this script is executed at ${ABSPATH}."

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
docker-compose up -d --build --remove-orphans && \
docker-compose push && echo "SUCESS! ECR image ready." && \
echo "Now running orchestration tool to update service..." && \
cd terraform && \
terraform apply && \
cd .. && \
echo "SUCCESS! Allow several minutes for change to take effect on production server. Take some rest and have a cup of coffee! Then go to the url and check it out." && return

echo Info: error occurred, reverting to original path...
cd "${ABSPATH}"
echo ERROR: see above message.