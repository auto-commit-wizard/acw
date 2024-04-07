#!/bin/bash

# ACW 설치 여부 확인
if command -v acw &>/dev/null; then
  echo "ACW가 이미 설치되어 있습니다. 재설치를 원하시는 경우 삭제 후 진행해주세요."
  exit 0
fi

# Python 3.11 또는 3.12 버전이 설치되어 있는지 확인
if ! command -v python3.11 &>/dev/null && ! command -v python3.12 &>/dev/null; then
  echo "Python 3.11 또는 3.12 버전이 설치되어 있지 않습니다."
  exit 1
fi

# Poetry 설치 여부 확인
if ! command -v poetry &>/dev/null; then
  echo "Poetry가 설치되어 있지 않습니다."
  echo "Poetry를 설치하려면 아래 링크를 참조하세요:"
  echo "https://python-poetry.org/docs/#installation"
  exit 1
fi

# 설치 경로 설정
OPT_PATH="/opt"
BIN_PATH="/usr/local/bin"

# /opt 디렉토리가 없는지 확인
if [ ! -d "$OPT_PATH" ]; then
  read -p "/opt 디렉토리가 존재하지 않습니다. 생성하시겠습니까? (Y/n): " -n 1 choice
  choice=${choice:-Y} # 사용자가 아무 입력도 하지 않으면 기본값 "Y"로 설정
  echo ""
  case "$choice" in
  y | Y)
    sudo mkdir -p "$OPT_PATH"
    ;;
  *)
    read -p "설치할 경로를 입력하세요: " custom_path
    if [ ! -d "$custom_path" ]; then
      echo "입력한 경로가 존재하지 않습니다. 스크립트를 종료합니다."
      exit 1
    fi
    OPT_PATH="$custom_path"
    ;;
  esac
fi

# Poetry를 사용하여 프로젝트 의존성 설치
poetry install

# PyInstaller 설치
poetry add pyinstaller

# Python 스크립트를 실행 파일로 변환
poetry run pyinstaller --onefile acw.py

# 실행 파일을 원하는 위치로 이동
echo -e "\nsudo 권한이 필요합니다."
sudo cp ./dist/acw $OPT_PATH/acw
sudo ln -sf $OPT_PATH/acw $BIN_PATH/acw

# build 폴더, dist 폴더, *.spec 파일 제거
rm -rf build dist *.spec

echo "'acw'가 성공적으로 설치되었습니다."
