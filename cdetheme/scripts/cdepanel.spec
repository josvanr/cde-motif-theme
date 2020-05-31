# -*- mode: python -*-

block_cipher = None


a = Analysis(['cdepanel.py'],
             pathex=['/sda10/sync/x/cdetheme0.9/cdetheme/scripts'],
             binaries=[],
             datas=[('CdePanel', 'CdePanel')],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='cdepanel',
          debug=False,
          strip=False,
          upx=True,
          runtime_tmpdir=None,
          console=True )
