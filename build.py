import os
import subprocess
import sys

def create_spec():
    print("[1] AutoBitTrade.spec 생성 중...")
    spec_code = '''
# AutoBitTrade.spec
# -*- mode: python ; coding: utf-8 -*-
block_cipher = None

a = Analysis(
    ['gui/gui_app.py'],
    pathex=['.'],
    binaries=[],
    datas=[
        ('.env', '.'),
        ('config/tick_table.py', 'config'),
        ('api/api.py', 'api'),
        ('utils/telegram.py', 'utils'),
    ],
    hiddenimports=['customtkinter', 'requests', 'PyJWT'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='AutoBitTrade',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='AutoBitTrade'
)
'''
    with open("AutoBitTrade.spec", "w", encoding="utf-8") as f:
        f.write(spec_code.strip())

def build():
    print("[2] 빌드 실행 중 (캐시 사용)...")

    # ✅ pyinstaller 경로 직접 지정
    pyinstaller_path = os.path.join("venv", "Scripts", "pyinstaller.exe")
    if not os.path.exists(pyinstaller_path):
        print("❌ pyinstaller가 설치되지 않았거나 경로를 찾을 수 없습니다.")
        sys.exit(1)

    result = subprocess.run([pyinstaller_path, "AutoBitTrade.spec", "--noconfirm"])
    if result.returncode == 0:
        print("[3] ✅ 빌드 완료: dist\\AutoBitTrade\\AutoBitTrade.exe")
    else:
        print("[3] ❌ 빌드 실패!")

if __name__ == "__main__":
    create_spec()
    build()
