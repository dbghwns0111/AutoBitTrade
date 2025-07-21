import os
import subprocess

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
    hiddenimports=[],
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
    name='AutoBitTrade',  # ✅ 실행파일 이름 변경
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False  # ⛔ 콘솔 숨김
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='AutoBitTrade'  # ✅ 폴더명도 AutoBitTrade로 설정
)
'''
    with open("AutoBitTrade.spec", "w", encoding="utf-8") as f:
        f.write(spec_code.strip())

def build():
    print("[2] 빌드 실행 중 (캐시 사용)...")
    result = subprocess.run(["pyinstaller", "AutoBitTrade.spec", "--noconfirm"])
    if result.returncode == 0:
        print("[3] ✅ 빌드 완료: dist\\AutoBitTrade\\AutoBitTrade.exe")
    else:
        print("[3] ❌ 빌드 실패!")

if __name__ == "__main__":
    create_spec()
    build()
