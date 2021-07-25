#!/usr/bin/env bash

if [[ -n "${RCMT_GITHUB_USERNAME}" ]]; then
  git config --global credential.helper store
  echo "https://${RCMT_GITHUB_USERNAME}:${RCMT_GITHUB_ACCESS_TOKEN}@github.com" >> "${HOME}/.git-credentials"
fi

exec rcmt "$@"
