#! python3

"""Create Minecraft Resource Packs for Musica."""

from pathlib import Path
import json
import argparse
from zipfile import ZipFile, ZIP_DEFLATED
from shutil import copy, rmtree
from os import chdir

def _processFilename(filename):
    '''Make filenames flat and computer friendly'''
    import re
    # title case and remove spaces
    clean_name = '_'.join(re.findall(r'[\w\-_]+', filename.title()))
    # lowercase first character
    clean_name = clean_name[0].lower() + clean_name[1:]
    return clean_name

# generate textures?
# would need Pillow or pypng + mathy stuff to shift hue

def _fillInfo(audiofiles, texturefiles, fileinfo=list()):
    '''Consolidate info for music'''
    from itertools import zip_longest, chain
    # process audio files' filenames (unsure if is this really needed... can't hurt though)
    music = dict()
    for filethings in zip_longest(audiofiles, texturefiles,fileinfo, fillvalue=[None]):
        filethings = tuple(chain.from_iterable(filethings))
        path = Path(filethings[0])
        clean_name = _processFilename(path.stem)
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

def _makeDirs(packinfo, outputdir=None):
    '''make the directories for the resource pack'''
    if outputdir is None:
        outputdir = Path.cwd()
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
        record_pack['records']['track%s' % (i+1)] = {
            'recordName' : track[0],
            'hasLore' : track[1].get('hasLore', False),
            'isShiny' : track[1].get('isShiny', False),
            'useSpecialName' : track[1].get('useSpecialName', False),
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
            if 'lore' in info:
                f.write('\nitem.record.{}.lore={}'.format(name, info['lore']))
            if 'specialName' in info:
                f.write('\nitem.musica.record.{}.name={}'.format(name, info['specialName']))

def _copyFiles(folder, audioPaths, names, texturePaths, packTexturePath=None):
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

def _makePack(music, pack_info, outputdir):
    '''Use args to make a resource pack.'''
    # fill info
    names = list()
    audioPaths = list()
    texturePaths = list()
    for name,info in music.items():
        names.append(name)
        audioPaths.append(info['audioPath'])
        texturePaths.append(info['texturePath'])
    # make directories (actual or temp?)
    folder = _makeDirs(pack_info, outputdir)
    # make text files
    _makeTextFiles(folder, music, pack_info)
    # copy non-text files
    _copyFiles(folder, audioPaths, music.keys(), texturePaths,
               Path(pack_info['thumbnailPath']) if ('thumbnailPath' in pack_info) else None)
    # compress directory
    _zipUpFolder(folder,outputdir)
    rmtree(str(folder))
    print("Pack written at '%s'." % (outputdir / folder.with_suffix('.rpack.zip').name))
    print(r"Move to resource folder ('\minecraft\resourcepacks\') and turn on in options to use.")

def _createArgParser():
    parser = argparse.ArgumentParser(
        description="Create Resource Packs for use with the Minecraft mod Musica, using specified " \
        + "'.ogg' sound files and '.png' textures for user-defined Records."
        )
    
    # [-o outputdir]
    parser.add_argument('-o', '--outputdir', default=r'./', type=Path,
                        help='Where to output the resource pack.')

    subparsers = parser.add_subparsers(dest='subparser_name',
        help='Choose how to load data to make Resource Pack.')

    # JSON file method
    ###########
    parser_json = subparsers.add_parser('json', help='Load all data from a JSON file.')
    # jsonfile JSONFILE
    parser_json.add_argument('jsonfile', type=Path,
                        help='Specify a JSON file to use for all data.')
    
    # Command Line method
    ##############
    parser_cl = subparsers.add_parser('cl', help='Specify data via command line arguments.')
    required_group = parser_cl.add_argument_group('Required Arguments',
                                                  'Arguments Required to make the pack.')
                                                  
    # -m audiofile [audiofile ...]
    required_group.add_argument('-m', '--audiofiles', type=Path, nargs='+', required=True,
                                action='append', help='The .ogg file(s) to add to pack.')
    # -t texturefile [texturefile ...]
    required_group.add_argument('-t', '--texturefiles', type=Path, nargs='+', required=True,
                                action='append', help='The .png file(s) to use as a record texture.')

    # [-l musicdesc]
    parser_cl.add_argument('-l', '--musicdesc', nargs='+', action='append',
                        help='The description of the in-game Record item(s), which otherwise uses the ' \
                        + 'filename without the (.ogg) suffix.')

    # pack metadata
    pack_metadata_group = parser_cl.add_argument_group('Pack metadata arguments',
                                          'Arguments to fill in Pack metadata.')
    # [-p packtexturefile]
    pack_metadata_group.add_argument('-p', '--packthumbnail', type=Path,
                                     help='The 128x128 .png thumbnail for the resource pack.')
    # [-n packtitle]
    pack_metadata_group.add_argument('-n', '--packname', default='Musica Pack',
                                     help='The name of the resource pack.')
    # [-a packauthor]
    pack_metadata_group.add_argument('-a', '--packauthor', default='An Author',
                                     help='The author of the resource pack.')
    # [-d packdescription]
    pack_metadata_group.add_argument('-d', '--packdescription', default='Contains music for Musica',
                                     help='The description of the resource pack.')
    
    return parser

if __name__ == '__main__':

    parser = _createArgParser()
    args = parser.parse_args()

    if args.subparser_name:
        if args.subparser_name == 'json':
            if args.jsonfile.is_file():
                jsonpath = args.jsonfile.resolve()
                chdir(str(jsonpath.parent))
                print('Load JSON file...')
                with jsonpath.open('r') as jf:
                    jsoninfo = json.load(jf)
                pack_info = jsoninfo.get('pack_info', {})
                outputdir = Path(jsoninfo.get('outputdir', r'./')).resolve()

                music = dict()
                for track in jsoninfo['music']:
                    clean_name = _processFilename(Path(track['audioPath']).stem)
                    music[clean_name] = {
                        'description' : Path(track['audioPath']).stem,
                        'hasLore' : False,
                        'isShiny' : False,
                        'useSpecialName' : False,
                        }
                    music[clean_name].update(track)
                    music[clean_name]['audioPath'] = Path(music[clean_name]['audioPath']).resolve()
                    music[clean_name]['texturePath'] = Path(music[clean_name]['texturePath']).resolve()
            
        elif args.subparser_name == 'cl':
            # get names, data etc
            audioPaths = args.audiofiles
            texturePaths = args.texturefiles
            pack_info = {
                'packName' : args.packname,
                'packAuthor' : args.packauthor,
                'description' : args.packdescription,
                'thumbnailPath' : args.packthumbnail,
                }
            outputdir = args.outputdir.resolve()
            if args.musicdesc is not None:
                fileinfo=list([{ 'description' : desc} for desc in args.musicdesc])
            else:
                fileinfo = list()

            music = _fillInfo(audioPaths, texturePaths, fileinfo)

        _makePack(music, pack_info, outputdir)
    else:
        parser.print_help()

