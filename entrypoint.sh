#!/bin/bash

set -e

git config --global user.email "deploy@autosoft-tech.com"
git config --global user.name "Autosoft"

cd ${GIT_FOLDER}
git pull https://${GIT_USER}:${GIT_PASS}@${GIT_REPO} ${GIT_BRANCH}
git pull
cp -rvf ${GIT_FOLDER}/* ${APP_FOLDER}/

# cd ${APP_FOLDER}/

python ${APP_FOLDER}/main.py

exit 1
