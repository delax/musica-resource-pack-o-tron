#! python3

from cx_Freeze import setup, Executable
from pathlib import Path
from sys import platform

include_files = [
    './resources/',
    './README.md',
    './example/',
    ]

build_exe_options = {
    'include_files' : include_files,
    }

# set icons only for windows
if platform.startswith('win32'):
    icon_path = Path('resources', 'pack-o-tron.ico').resolve()
    base = "Win32GUI"
else:
    base = None
    icon_path = None

executables = [
    Executable('musica_resource_packotron.py',
               base=base,
               icon=str(icon_path) if icon_path else icon_path,
               ),
    Executable('resource_pack_gui.py',
               base=base,
               icon=str(icon_path) if icon_path else icon_path,
               ),
    ]

setup(
    name = 'musica_resource_packotron',
    version = '1.3',
    description = 'Helper tool to make resource packs for the Minecraft mod Musica.',
    options = {'build_exe' : build_exe_options},
    executables = executables,
    )
