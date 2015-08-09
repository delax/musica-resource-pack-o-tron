#! python3

"""Create Minecraft Resource Packs for Musica."""

from pathlib import Path
import json
import argparse
from zipfile import ZipFile, ZIP_DEFLATED
from shutil import copy, rmtree

def processFilename(filename):
    '''Make filenames flat and computer friendly'''
    # title case and remove spaces
    clean_name = ''.join(filename.title().split())
    # lowercase first character
    clean_name = clean_name[0].lower() + clean_name[1:]
    return clean_name

# generate textures?
# would need Pillow or pypng + mathy stuff to shift hue

def _fillInfo(audiofiles, texturefiles, fileinfo=list()):
    '''Consolidate info for music'''
    from itertools import zip_longest
    # process audio files' filenames (unsure if is this really needed... can't hurt though)
    music = dict()
    for filethings in zip_longest(audiofiles, texturefiles,fileinfo):
        path = Path(filethings[0])
        clean_name = processFilename(path.stem)
        # account for duplicate cleaned names
        while clean_name in music:
            if i is not int:
                i = 1
            else:
                i += 1
            if clean_name + str(i) not in music:
                clean_name + str(i)
        # Set default infos
        music[clean_name] = {
            'description' : path.stem,
            'audioPath' : path.resolve(),
            'texturePath' : Path(filethings[1]).resolve(),
            'hasLore' : False,
            'isShiny' : False,
            'useSpecialName' : False,
            }
        # overwrite defaults with given info
        if filethings[2] is not None:
            music[clean_name].update(filethings[2])
    return music

def _makeDirs(packinfo, outputdir=Path.cwd()):
    '''make the directories for the resource pack'''
    folder = Path(outputdir) / packinfo['packName']
    folder.mkdir()

    # create inner folders:
    # assets
    #   \musica
    #       \lang
    #       \sounds
    #           \records
    #       \textures
    #           \items
    (folder / r'assets/musica/lang').mkdir(parents=True)
    (folder / r'assets/musica/sounds/records').mkdir(parents=True)
    (folder / r'assets/musica/textures/items').mkdir(parents=True)
    return folder.resolve()

def _makeTextFiles(folder, music, pack_info=dict()):
    '''Write the json text files for the resource pack'''
    pack_mcmeta = {
            "language": {
                "en_US": {
                    "region": "US",
                    "name": "English",
                    "bidirectional": False,
                }
            },
            "pack": {
                "description": "Contains music for Musica",
                "pack_format": 1,
            }
        }
    
    # fill pack info
    if 'description' in pack_info:
        pack_mcmeta['pack']['description'] = pack_info['description']

    record_pack = {
            "packInfo": {
                "packAuthor": "An Author",
                "packName": "A Musica pack",
                "packVersion": "1.0.0",
            },
            "records": {
                }
            }

    # fill record pack info
    for key in record_pack['packInfo']:
        if key in pack_info:
            record_pack['packInfo'][key] = pack_info[key]
    for i, track in enumerate(music.items()):
        record_pack['records']['track%s' % i] = {
            'recordName' : track[0],
            'hasLore' : track[1]['hasLore'],
            'isShiny' : track[1]['isShiny'],
            'useSpecialName' : track[1]['useSpecialName'],
            }
    # create the text files:

    # pack.mcmeta
    with (folder / r'pack.mcmeta').open('w') as f:
        json.dump(pack_mcmeta, f, indent=4)

    # record-pack.json
    with (folder / r'record-pack.json').open('w') as f:
        json.dump(record_pack, f, indent=4)

    # assets\musica\sounds.json
    with (folder / r'assets/musica/sounds.json').open('w') as f:
        sounds = { 'records.%s' % name : {
            'category' : 'record',
            'sounds' : [{
                'name' : 'records/%s' % info['audioPath'].stem,
                'stream' : True,
                }],
            } for name, info in music.items()}
        json.dump(sounds, f, indent=4)
    
    # assets\musica\lang\en_US.lang
    with (folder / r'assets/musica/lang/en_US.lang').open('w') as f:
        f.write('#Record Descriptions')
        for name, info in music.items():
            f.write('\nitem.record.{}.desc={}'.format(name, info['description']))

def _copyFiles(audioPaths, names, texturePaths, packTexturePath=None):
    '''Grab the premade files and copy them to proper place'''
    # Copy files into folder:
    # pack cover picture - > pack.png
    if packTexturePath is not None and packTexturePath.exists():
        copy(
            str(packTexturePath),
            str(folder / 'pack.png')
            )

    # audio files -> assets\musica\sounds\records\*
    for audioPath in audioPaths:
        copy(
            str(audioPath),
            str(folder / r'assets/musica/sounds/records/')
            )

    # texture files -> assets\musica\textures\items\record_[audio filename].png
    for name, texturePath in zip(names, texturePaths):
        copy(
            str(texturePath),
            str(folder / (r'assets/musica/textures/items/record_%s.png' % name))
            )

def _zipUpFolder(inputdir,outputdir=None):
    '''Compress everything in a directory, name it after the dir,
    and put it in output dir (defaults to inputdir).'''
    if outputdir is None:
        outputdir = inputdir
    inputdir = Path(inputdir)
    outputdir = Path(outputdir)
    files = inputdir.glob('**/*.*')
    with ZipFile(str(outputdir / inputdir.with_suffix('.rpack.zip').name), 'w', ZIP_DEFLATED) as zf:
        for file in files:
            zf.write(str(file), str(file.relative_to(inputdir)))

def _createArgParser():
    parser = argparse.ArgumentParser(
        description="Create Resource Packs for use with the Minecraft mod Musica, using specified " \
        + "'.ogg' sound files and '.png' textures for user-defined Records."
        )
    # audiofile [audiofile ...]
    parser.add_argument('audiofiles', type=Path, nargs='+',
                        help='An .ogg file to add to pack.')
    # [-t texturefile [texturefile ...]]
    parser.add_argument('-t', '--texturefiles', required=True, type=Path, nargs='+',
                        help='A .png file to use as a record texture.')
    # [-o outputdir]
    parser.add_argument('-o', '--outputdir', default=r'./', type=Path,
                        help='Where to output the resource pack.')
    # [-l musicdesc]
    parser.add_argument('-l', '--musicdesc', nargs='+',
                        help='The description of the in-game Record item, otherwise uses the' \
                        + 'filename without suffix (.ogg).')

    # pack metadata
    pack_metadata_group = parser.add_argument_group('Pack metadata arguments',
                                          'Arguments to fill in Pack metadata.')
    # [-p packtexturefile]
    pack_metadata_group.add_argument('-p', '--packthumbnail', type=Path,
                                     help='The 128x128 .png thumbnail for the resource pack.')
    # [-n packtitle]
    pack_metadata_group.add_argument('-n', '--packname', required=True,
                                     help='The name of the resource pack.')
    # [-a packauthor]
    pack_metadata_group.add_argument('-a', '--packauthor', default='An Author',
                                     help='The author of the resource pack.')
    # [-d packdescription]
    pack_metadata_group.add_argument('-d', '--packdescription', default='Contains music for Musica',
                                     help='The description of the resource pack.')
    
##    # [-j jsonfile]
##    parser.add_argument('-j', '--jsonfile', type=Path,
##                        help='Specify a JSON file to use for all data, any commandline arguments have ' \
##                        + 'precedence.')
    
    return parser

if __name__ == '__main__':
    parser = _createArgParser()
    args = parser.parse_args()

    # get names, data etc
    audioPaths = args.audiofiles
    texturePaths = args.texturefiles
    pack_info = {
        'packName' : args.packname,
        'packAuthor' : args.packauthor,
        'description' : args.packdescription,
        'thumbnail' : args.packthumbnail,
        }
    outputdir = args.outputdir.resolve()
    if args.musicdesc is not None:
        fileinfo=list([{ 'description' : desc} for desc in args.musicdesc])
    else:
        fileinfo = list()

    # fill info
    music = _fillInfo(audioPaths, texturePaths, fileinfo)
    names = list()
    audioPaths.clear()
    texturePaths.clear()
    for name,info in music.items():
        names.append(name)
        audioPaths.append(info['audioPath'])
        texturePaths.append(info['texturePath'])
    # make directories (actual or temp?)
    folder = _makeDirs(pack_info, outputdir)
    # make text files
    _makeTextFiles(folder, music, pack_info)
    # copy non-text files
    _copyFiles(audioPaths, music.keys(), texturePaths, pack_info['thumbnail'])
    # compress directory
    _zipUpFolder(folder,outputdir)
    rmtree(str(folder))
