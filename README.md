# Git · GitHub · VS Code 초기 설정 및 Push 실습 가이드

> **실습 목표:** 로컬 PC에 작업 폴더를 만들고, VS Code에서 프로젝트를 열어 GitHub 원격 저장소에 최초 커밋을 업로드한다.
>
> **실습 환경:** Windows 10/11, Git, Visual Studio Code(VS Code), GitHub 계정

## 사전 준비

- [Git](https://git-scm.com/downloads) 설치
- [Visual Studio Code](https://code.visualstudio.com/) 설치
- [GitHub](https://github.com/) 계정 준비
- 터미널에서 `git --version`으로 Git 설치 확인

> **예시 정보**
> - 로컬 작업 폴더: `C:\AI4\ai4_lecture`
> - GitHub 저장소: `https://github.com/skn29teacher/ai4_lecture.git`
> - 기본 브랜치: `main` (소문자)
>
> 저장소 주소와 Git 사용자 정보는 본인 환경에 맞게 변경한다. 예시 저장소로 Push하려면 해당 저장소에 쓰기 권한이 있어야 한다.

---

## 1. 로컬 PC 작업 폴더 설정

프로젝트 파일을 관리할 폴더를 만든다. VS Code의 터미널(PowerShell)에서 다음을 실행한다.

```powershell
mkdir C:\AI4\ai4_lecture
cd C:\AI4\ai4_lecture
```

이미 폴더가 있다면 `mkdir`는 생략하고 `cd`만 실행한다.

**확인:** 현재 경로가 `C:\AI4\ai4_lecture`인지 확인한다.

```powershell
pwd
```

## 2. GitHub 원격 Repository 설정

1. [GitHub](https://github.com/)에 로그인한다.
2. 오른쪽 위 **+ → New repository**를 클릭한다.
3. **Repository name**에 `ai4_lecture`를 입력한다.
4. 공개 범위를 **Public** 또는 **Private**로 선택한다.
5. **Create repository**를 클릭한다.
6. 생성된 저장소의 **HTTPS 주소**를 복사한다.

예시:

```text
https://github.com/skn29teacher/ai4_lecture.git
```

**중요:** 이 가이드는 처음부터 로컬 프로젝트를 Push하는 절차이므로, 새 원격 저장소를 생성할 때 **Add a README file**, **Add .gitignore**, **Choose a license**를 선택하지 않고 **빈 저장소**로 시작하는 것이 가장 간단하다.

원격 저장소에 이미 파일이나 커밋이 있다면, 새 폴더에서 `git clone <저장소주소>`로 시작하는 방식이 일반적으로 더 안전하다.

## 3. VS Code에서 작업 폴더 열기

VS Code에서 **File → Open Folder(파일 → 폴더 열기)**를 선택하고 다음 경로를 연다.

```text
C:\AI4\ai4_lecture
```

또는 작업 폴더로 이동한 터미널에서 실행한다.

```powershell
code .
```

`code` 명령을 사용할 수 없다면 VS Code 메뉴에서 폴더를 직접 열면 된다.

VS Code의 **Terminal → New Terminal**을 선택해 통합 터미널을 연다.

## 4. Git 사용자 이름 및 이메일 설정

Git 커밋 기록에 표시할 사용자 정보를 설정한다.

```bash
git config --global user.name "본인 Git 사용자 이름"
git config --global user.email "본인 이메일@example.com"
```

설정 결과 확인:

```bash
git config --global user.name
git config --global user.email
```

> **참고:** `--global`은 PC의 사용자 계정에 적용되는 설정이다. 특정 저장소만 다른 이름/이메일을 사용하려면 **5단계 `git init` 이후** 해당 저장소에서 `git config --local user.name "이름"` 및 `git config --local user.email "이메일"`을 실행한다.
>
> Git의 `user.name`과 `user.email`은 **커밋 작성자 정보**이며 GitHub **로그인이나 Push 권한을 부여하는 설정이 아니다**. Push할 때는 해당 저장소에 권한이 있는 GitHub 계정으로 인증해야 한다.

## 5. Git 초기화 (`git init`)

현재 작업 폴더를 Git 저장소로 초기화한다.

```bash
git init
```

정상 실행되면 `.git` 디렉터리가 생성되고 이 폴더의 변경 이력을 Git으로 관리할 수 있다.

초기화 및 상태 확인:

```bash
git status
```

## 6. 기본 브랜치를 `main`으로 변경

GitHub에서 일반적으로 사용하는 브랜치 이름으로 변경한다.

```bash
git branch -M main
```

> Git 브랜치 이름은 대소문자를 구분할 수 있다. `Main`과 `main`은 동일한 이름이 아니므로 이 실습에서는 **`main`(소문자)**으로 통일한다.

최초 커밋 전에는 환경에 따라 브랜치 목록에 표시되지 않을 수 있다. 커밋 후 `git branch`로 확인할 수 있다.

## 7. 로컬 저장소와 원격 Repository 연결

2단계에서 복사한 GitHub HTTPS 주소를 `origin`이라는 이름으로 등록한다.

```bash
git remote add origin https://github.com/skn29teacher/ai4_lecture.git
```

연결 확인:

```bash
git remote -v
```

정상적으로 연결되면 `origin`의 `fetch` 및 `push` 주소가 표시된다.

이미 `origin`이 등록되어 있다는 오류가 나오면 중복 등록하지 않고 다음 명령으로 주소를 수정한다.

```bash
git remote set-url origin https://github.com/skn29teacher/ai4_lecture.git
```

## 8. 코드 작성 및 커밋 (`git add` / `git commit`)

VS Code에서 `README.md` 등 프로젝트 파일을 작성·저장한다.

예: `README.md`

```markdown
# ai4_lecture

Git과 GitHub를 이용한 협업 실습 저장소입니다.
```

현재 변경사항 확인:

```bash
git status
```

파일을 스테이징하고 최초 커밋을 생성한다.

```bash
git add .
git commit -m "first commit"
```

확인:

```bash
git log --oneline -1
```

> `git add .`는 현재 폴더 아래의 변경 파일을 커밋 대상으로 등록한다. 암호, API 키, 가상환경, 대용량 데이터 파일 등이 포함되지 않았는지 커밋 전에 확인하고 필요한 항목은 `.gitignore`에 추가한다.

## 9. GitHub로 Push

최초 Push에서는 원격 브랜치의 추적 관계(upstream)를 설정한다.

```bash
git push -u origin main
```

이후 같은 브랜치에서 변경사항을 업로드할 때는 간단히 실행할 수 있다.

```bash
git push
```

**최종 확인:** GitHub 저장소 페이지를 새로고침하여 `README.md` 등 프로젝트 파일과 커밋 기록이 반영되었는지 확인한다.

> **GitHub 인증:** HTTPS로 Push할 때 브라우저 로그인 또는 Git Credential Manager를 통해 인증을 요청받을 수 있다. 기존에 다른 계정으로 인증되어 있거나 권한이 없는 저장소로 Push하면 `403 Permission denied`가 발생할 수 있다.

---

## 전체 명령어 요약

아래 예시는 **2단계에서 원격 저장소를 빈 저장소로 생성했고, 3단계에서 VS Code 작업 폴더를 열었으며, `README.md` 파일을 작성한 상태**를 전제로 한다.

```bash
# 4. Git 작성자 정보 설정
git config --global user.name "본인 Git 사용자 이름"
git config --global user.email "본인 이메일@example.com"

# 5. Git 초기화
git init

# 6. 기본 브랜치 이름 설정
git branch -M main

# 7. 원격 저장소 연결
git remote add origin https://github.com/skn29teacher/ai4_lecture.git

# 7-2. 원격 저장소 변경은 기존 저장소 연결정보를  삭제하고 다시 연결
git remote remove origin
git remote add origin https://github.com/skn29teacher/ai4_lecture.git

# 8. 변경사항 커밋
git add .
git commit -m "first commit"

# 9. 최초 Push
git push -u origin main
```

## 이후 반복 작업: Pull → 수정 → Commit → Push

최초 연결 이후에는 원격 저장소의 변경사항을 확인하고 가져온 다음 작업하는 습관을 권장한다.

```bash
# 원격 최신 코드 반영 (커밋하지 않은 로컬 변경사항이 없는 상태에서)
git pull --rebase origin main

# VS Code에서 파일 수정 및 저장

# 변경사항 확인
git status

# 수정 내용 커밋
git add .
git commit -m "Update project files"

# 원격 저장소에 업로드
git push origin main
```

로컬 변경사항이 있어 `git pull`이 중단된 경우에는 먼저 커밋하거나, 아래처럼 임시 보관 후 다시 적용할 수 있다.

```bash
git stash push -u -m "backup before pull"
git pull --rebase origin main
git stash pop
```

`git stash pop`에서 파일 충돌이 발생하면 **충돌을 해결하고 `git add` → `git commit` → `git push`** 순서로 진행한다. 충돌을 해결하기 전에는 무조건 Push하지 않는다.

## 자주 발생하는 오류

| 오류 메시지/상황 | 원인 | 해결 방법 |
|---|---|---|
| `remote origin already exists` | 이미 `origin`이 등록됨 | `git remote -v` 확인 후 `git remote set-url origin <주소>` |
| `403 Permission denied` | GitHub 로그인 계정에 Push 권한이 없음 | 사용 중인 GitHub 인증 계정 및 저장소 쓰기 권한 확인 |
| `Please tell me who you are` | Git 작성자 이름·이메일 미설정 | `git config --global user.name` 및 `user.email` 설정 |
| `nothing to commit, working tree clean` | 커밋할 새 변경사항이 없음 | 변경한 파일이 실제 저장되었는지 `git status` 확인 |
| `failed to push some refs` / `non-fast-forward` | 원격 브랜치에 로컬에 없는 커밋 존재 | 로컬 변경사항을 먼저 정리한 뒤 `git pull --rebase origin main` 후 Push |
| `Your local changes ... would be overwritten by merge` | Pull 시 로컬 수정사항이 덮어써질 위험 | 변경사항을 커밋하거나 `git stash`로 보관한 뒤 Pull |

---

**실습 완료 기준:** 로컬 작업 폴더에서 `git status`를 실행해 상태를 확인할 수 있고, GitHub 원격 저장소의 `main` 브랜치에 작성한 코드와 커밋이 정상적으로 나타난다.
