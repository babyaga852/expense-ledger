# -*- mode: python ; coding: utf-8 -*-
block_cipher = None

a = Analysis(
    ['launcher.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('templates', 'templates'),
        ('static',    'static'),
        ('tracker.py', '.'),
        ('app.py',     '.'),
        ('project.py', '.'),
    ],
    hiddenimports=[
        # Flask & web
        'flask',
        'flask.templating',
        'jinja2',
        'jinja2.ext',
        'werkzeug',
        'werkzeug.serving',
        'werkzeug.routing',
        'werkzeug.exceptions',
        'click',
        # Exports
        'openpyxl',
        'openpyxl.styles',
        'reportlab',
        'reportlab.lib',
        'reportlab.platypus',
        'reportlab.lib.pagesizes',
        # Image
        'PIL',
        'PIL.Image',
        # DB & stdlib
        'sqlite3',
        'hashlib',
        'csv',
        'io',
        # Tkinter (desktop app)
        'tkinter',
        'tkinter.ttk',
        'tkinter.messagebox',
        'tkinter.filedialog',
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
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='ExpenseLedger',
)
