#! python3

from cx_Freeze import setup, Executable

include_files = [
    './pack-o-tron.ico',
    './README.md',
    './example/',
    ]

build_exe_options = {
    'include_files' : include_files,
    }

executables = [
    Executable('musica_resource_packotron.py', icon='pack-o-tron.ico'),
    Executable('resource_pack_gui.py', icon='pack-o-tron.ico'),
    ]

setup(
    name = 'musica_resource_packotron',
    version = '1.0',
    description = 'Helper tool to make resource packs for the Minecraft mod Musica.',
    options = {'build_exe' : build_exe_options},
    executables = executables,
    )
