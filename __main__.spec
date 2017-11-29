# -*- mode: python -*-
# usage: pyinstaller -F __main__.spec

import os


block_cipher = None

a = Analysis([ '__main__.py' ],
             pathex=[ os.getcwd() ],
             binaries=[],
             datas=[ ('images/*.png', 'images') ],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)

pyz = PYZ(a.pure,
          a.zipped_data,
          cipher=block_cipher)

exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='ytdl',
          debug=False,
          strip=False,
          upx=True,
          runtime_tmpdir=None,
          console=False )

if os.name == "nt": # on Windows
    coll = COLLECT(exe,
                   a.binaries,
                   a.zipfiles,
                   a.datas,
                   name='ytdl',
                   strip=False,
                   upx=True,
                   icon=None)
elif os.name == "posix": # on macOS
    app = BUNDLE(exe,
                 name='ytdl.app',
                 icon=None,
                 bundle_identifier=None,
                 info_plist={ 'NSHighResolutionCapable': 'True' })
# on Linux, just type "python __main__.py" in terminal
