# -*- mode: python ; coding: utf-8 -*-
from os.path import join, dirname, abspath, split
from os import sep
import glob
import quarry

block_cipher = None

quarry_data = os.path.join(split(quarry.__file__)[0], 'data')

datas = [
]
datas.extend((file, dirname(file).split("site-packages")[1][1:]) for file in glob.iglob(join(quarry_data,"**{}*.csv".format(sep)), recursive=True))
datas.extend((file, dirname(file).split("site-packages")[1][1:]) for file in glob.iglob(join(quarry_data,"**{}*.nbt".format(sep)), recursive=True))

a = Analysis(['__main__.py'],
             pathex=['.', '../venv/Lib/site-packages'],
             #pathex=['.', '../venv-linux/Lib/python3.8/site-packages'],
             binaries=[],
             datas=datas,
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='server',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=True )
