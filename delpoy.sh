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
docker-compose push && echo Success! ECR image ready. && return

echo ERROR: see above message.