# ACW (Auto Commit Wizard 🧙)

## Build

### Prerequisites

- Above `Python 3.12`
- [Poetry](https://python-poetry.org/)

### Script

```bash
git clone https://github.com/auto-commit-wizard/acw.git
cd acw
poetry install
```

## TO-DO

- [ ] `acw config`
  - [ ] OpenAI API Key 저장
  - [ ] 아래 값은 default 로 설정 후 custom 처리
    - [ ] Prompt message
    - [ ] commit message language (default: English, optional: Korean)
    - [ ] OpenAI Model
    - [ ] OpenAI Temperature
    - [ ] OpenAI Max Tokens
    - [ ] OpenAI Frequency Penalty
    - [ ] OpenAI Presence Penalty
- [x] 명령어 compile (like Makefile)
- [x] Install script
- [ ] Uninstall script
- [ ] `acw` (or `acw commit`)
  - [ ] Untracted files, Modified files 을 찾고
  - [ ] 커밋할 파일을 선택하게 한 뒤
  - [ ] 커밋 목적을 입력 받고
  - [ ] 커밋할 파일들의 변경된 내용을 가져와서 커밋 메시지 생성
    - [ ] 여러 개의 커밋 메시지를 생성해서 유저가 선택하게끔 처리
  - [ ] 커밋 메시지를 선택 or 직접 입력 (또는 수정) 하게 한 뒤
  - [ ] `push` 하고 종료
- [ ] `acw --help`
- [ ] `acw --version`
- [ ] extensions
  - [ ] IntelliJ plugin
  - [ ] VSCode extension
  - [ ] GitHub Actions
- [ ] Error Handling
  - [ ] `.git` folder 가 없을 때 처리
  - [ ] TBA
