#!/bin/bash

# Poetry가 설치되어 있는지 확인
if ! command -v poetry &> /dev/null
then
    echo "Poetry가 설치되어 있지 않습니다. 설치를 시작합니다..."
    # 공식 설치 스크립트 사용
    curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python -
    
    # 설치 후 PATH에 poetry를 추가할 수 있도록 환경 변수 설정
    # 이 부분은 사용자의 쉘 설정에 따라 다를 수 있으며, bash를 예로 들었습니다.
    source $HOME/.poetry/env
else
    echo "Poetry가 이미 설치되어 있습니다."
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
