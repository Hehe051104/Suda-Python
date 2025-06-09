# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['QuizGame.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('correct.wav', '.'),
        ('incorrect.wav', '.'),
        ('warning.wav', '.'),
        ('Quiz.xlsx', '.'),
        ('名单.xlsx', '.'),
        ('小测验游戏说明.txt', '.'),
        ('Record.txt', '.'),
        ('score_history.json', '.'),
    ],
    hiddenimports=['openpyxl', 'pygame', 'matplotlib'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='QuizGame',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)
