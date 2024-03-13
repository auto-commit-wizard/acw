#!/bin/bash

# Python 3.11 또는 3.12 버전이 설치되어 있는지 확인
if command -v python3.11 &>/dev/null || command -v python3.12 &>/dev/null; then
  echo "Python 3.11 또는 3.12 버전이 설치되어 있습니다."
else
  echo "Python 3.11 또는 3.12 버전이 설치되어 있지 않습니다."
  exit 1
fi

# Poetry 설치 여부 확인
if command -v poetry &>/dev/null; then
  echo "Poetry가 이미 설치되어 있습니다."
else
  echo "Poetry가 설치되어 있지 않습니다."
  echo "Poetry를 설치하려면 아래 링크를 참조하세요:"
  echo "https://python-poetry.org/docs/#installation"
  exit 1
fi

# Poetry를 사용하여 프로젝트 의존성 설치
poetry install

# PyInstaller 설치
poetry add pyinstaller

# Python 스크립트를 실행 파일로 변환
poetry run pyinstaller --onefile acw.py

# `No such file or directory` 대응
sudo mkdir -p -m 775 /usr/local/bin

# 실행 파일을 원하는 위치로 이동
sudo cp ./dist/acw /usr/local/bin/acw

# build 폴더, dist 폴더, *.spec 파일 제거
rm -rf build dist *.spec

echo "'acw'가 성공적으로 설치되었습니다."
