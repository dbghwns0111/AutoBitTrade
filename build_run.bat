@chcp 65001 >nul
@echo off
cd /d %~dp0

echo [1] 가상환경 활성화
call venv\Scripts\activate.bat

echo [2] 의존성 설치
pip install -r requirements.txt

echo [3] 빌드 시작
python build.py

echo [4] ✅ 빌드 완료: dist\AutoBitTrade\AutoBitTrade.exe
echo [4] ▶ 실행파일 실행 중...
start dist\AutoBitTrade\AutoBitTrade.exe

pause
