# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for LagForge v1.101
Includes UAC admin manifest embedding, WinDivert driver binaries, and hotkey modules.
"""

import os
import sys
from PyInstaller.utils.hooks import collect_data_files, collect_dynamic_libs, collect_submodules

block_cipher = None

# Collect pydivert assets and submodules
pydivert_datas = collect_data_files('pydivert')
pydivert_binaries = collect_dynamic_libs('pydivert')
pydivert_hiddenimports = collect_submodules('pydivert')

# Explicitly ensure WinDivert binaries are bundled
import pydivert
pydivert_path = os.path.dirname(pydivert.__file__)
dll_dir = os.path.join(pydivert_path, 'windivert_dll')

extra_binaries = []
extra_datas = []

if os.path.exists(dll_dir):
    for f in os.listdir(dll_dir):
        full_path = os.path.join(dll_dir, f)
        if os.path.isfile(full_path):
            if f.endswith('.dll') or f.endswith('.sys'):
                extra_binaries.append((full_path, 'pydivert/windivert_dll'))
                extra_binaries.append((full_path, '.'))
            extra_datas.append((full_path, 'pydivert/windivert_dll'))

all_binaries = list(set(pydivert_binaries + extra_binaries))
all_datas = list(set(pydivert_datas + extra_datas))
all_hiddenimports = list(set(
    pydivert_hiddenimports + [
        'PySide6',
        'PySide6.QtCore',
        'PySide6.QtGui',
        'PySide6.QtWidgets',
        'pydivert',
        'pydivert.windivert',
        'pydivert.windivert_dll',
        'pydivert.windivert_dll.structs',
        'hotkey_manager',
        'config_manager',
        'ui.profile_dialog',
    ]
))

a = Analysis(
    ['main.py'],
    pathex=['.'],
    binaries=all_binaries,
    datas=all_datas,
    hiddenimports=all_hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tkinter', 'matplotlib', 'scipy', 'numpy', 'torch', 'IPython'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(
    a.pure,
    a.zipped_data,
    cipher=block_cipher
)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='LagForge',
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
    uac_admin=True,
)
