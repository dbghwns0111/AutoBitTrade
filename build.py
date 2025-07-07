import os
import subprocess

def create_spec():
    print("[1] gui_app.spec 생성 중...")
    spec_code = '''
# gui_app.spec
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
        ('utils/price.py', 'utils'),
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
    name='gui_app',
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
    name='gui_app'
)
'''
    with open("gui_app.spec", "w", encoding="utf-8") as f:
        f.write(spec_code.strip())

def build():
    print("[2] 빌드 실행 중 (캐시 사용)...")
    result = subprocess.run(["pyinstaller", "gui_app.spec", "--noconfirm"])
    if result.returncode == 0:
        print("[3] ✅ 빌드 완료: dist\\gui_app\\gui_app.exe")
    else:
        print("[3] ❌ 빌드 실패!")

if __name__ == "__main__":
    create_spec()
    build()
