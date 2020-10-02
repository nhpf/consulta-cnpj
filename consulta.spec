# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['consulta.py'],
             pathex=['D:\\cnpj-process'],
             binaries=[],
             datas=[("D:\\cnpj-process\\media", "media/")],
             hiddenimports=['tkinter'],
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
          name='Consulta CNPJ',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=False , icon='D:\\cnpj-process\\media\\consulta.ico')
