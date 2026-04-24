# -*- mode: python ; coding: utf-8 -*-
block_cipher = None

a = Analysis(
    ['launcher.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('templates', 'templates'),
        ('expense_ledger_logo.png', '.'),
        ('tracker.py', '.'),
        ('app.py', '.'),
        ('project.py', '.'),
    ],
    hiddenimports=[
        'flask',
        'flask.templating',
        'jinja2',
        'jinja2.ext',
        'werkzeug',
        'werkzeug.serving',
        'werkzeug.routing',
        'werkzeug.exceptions',
        'click',
        'openpyxl',
        'openpyxl.styles',
        'reportlab',
        'reportlab.lib',
        'reportlab.platypus',
        'reportlab.lib.pagesizes',
        'PIL',
        'PIL.Image',
        'sqlite3',
        'hashlib',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='ExpenseLedger',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='ExpenseLedger'
)
