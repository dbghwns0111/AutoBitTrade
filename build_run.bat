@chcp 65001 >nul
@echo off
cd /d %~dp0

echo [0] conda base 환경 비활성화 시도...
call conda deactivate >nul 2>&1

echo [1] 가상환경(venv) 활성화
call venv\Scripts\activate.bat

echo [2] 의존성 설치
pip install --upgrade pip
pip install -r requirements.txt
IF %ERRORLEVEL% NEQ 0 (
    echo ❌ 의존성 설치 실패! requirements.txt를 확인하세요.
    pause
    exit /b
)

echo [3] 빌드 시작
python build.py
IF %ERRORLEVEL% NEQ 0 (
    echo ❌ 빌드 실패! build.py를 확인하세요.
    pause
    exit /b
)

IF EXIST dist\AutoBitTrade\AutoBitTrade.exe (
    echo [4] ✅ 빌드 완료: dist\AutoBitTrade\AutoBitTrade.exe
    echo [4] ▶ 실행파일 실행 중...
    start dist\AutoBitTrade\AutoBitTrade.exe
) ELSE (
    echo ❌ 실행파일이 존재하지 않습니다. 빌드가 실패했을 수 있습니다.
)

pause
