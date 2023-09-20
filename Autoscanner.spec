# -*- mode: python ; coding: utf-8 -*-
import os 
os.environ['KIVY_GL_BACKEND'] = 'angle_sdl2'
from kivy_deps import sdl2,angle


block_cipher = None


a = Analysis(
    ['Main.py'],
    pathex=[],
    binaries=[],
    datas=[('src/kv/','./src/kv/'),('src/images/','src/images/'),('src/settings.json','src/')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='Autoscanner',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    icon='.\\src\\images\FireIcon.png',
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,Tree('.\\venv\\share\\sdl2\\bin\\'),
Tree('.\\venv\\share\\angle\\bin\\'),
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Autoscanner',
)
