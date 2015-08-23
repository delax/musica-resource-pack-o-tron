#! python3

"""A basic GUI using tkinter for musica tool"""

import musica_resource_packotron as mt
from pathlib import Path

from tkinter import *
from tkinter import filedialog
from tkinter import messagebox
from tkinter import ttk

class MusicaApp(ttk.Frame):
    '''Main app window'''

    helptexts = {
        'thumbnail path' : 'The 128x128 .png thumbnail for the resource pack.',
        'pack name' : 'The name of the resource pack.',
        'pack author' : 'The author of the resource pack.',
        'pack description' : 'The description of the resource pack.',
        'track description' : 'The description of the in-game Record item, which otherwise uses the ' \
            + 'filename without the (.ogg) suffix.',
        'music listbox' : 'The list of the tracks by description, clicking one will fill the track info entries ' \
            + 'with its own info.',
        'add track' : 'Choose one or more audio-files and add to the track list.',
        'remove track' : 'Delete current/last selected track and remove from list.',
        'audio path' : 'The .ogg file to be used for the sound of the track.',
        'texture path' : 'The .png file to be used as the Record item texture.',
        'is shiny' : 'Give the Record item of the track a shine, like an enchanted item.',
        'special name' : 'If not blank, this will change the default item name from "Music Disc" to ' \
            + 'the given special name.',
        'lore' : 'If not blank, this will add an extra line of text (lore) to the Record item.',
        'set track info' : 'Change current/last selected track\'s info to the entered track info.',
        'output dir' : 'Resource Pack will be written into this directory. (default: "./")',
        }

    def __init__(self, master=None, default_texture=None, **kwds):
        super().__init__(master, **kwds)

        self.default_record_texture = default_texture
        if default_texture is not None:
            self.helptexts['texture path'] += ' Defaults to "%s".' % default_texture

        framekwds = {'padding' : '3 3 12 12'}

##        # menu
##        menubar = Menu(master)
##        menu_file = Menu(menubar)
##        menubar.add_cascade(menu=menu_file, label='File')
##        master.config(menu=menubar)

        notebook = ttk.Notebook(self)

        # Tab to enter Pack info
        packinfoframe = self._make_pack_info_frame(notebook, framekwds)
        
        # Tab to enter the various music files info
        musicframe = self._make_music_frame(notebook, framekwds)
        
        # Add both tabs to Notebook
        notebook.add(packinfoframe, text='Pack Info')
        notebook.add(musicframe, text='Music')

        # Output dir
        self.outputdirvar = StringVar()
        self.outputdirvar.set('./')

        outputdirframe = ttk.LabelFrame(self, text='Output Dir:', **framekwds)
        self._bind_display_help(outputdirframe, 'output dir')

        ttk.Entry(outputdirframe, textvariable=self.outputdirvar, width=20).grid(column=0, row=0, sticky=(W,E))
        ttk.Button(outputdirframe, text='Browse',
                   command=lambda *args : self.outputdirvar.set(filedialog.askdirectory())
                   ).grid(column=1, row=0, sticky=(W,E))

        outputdirframe.columnconfigure(0, weight=1)
        outputdirframe.columnconfigure(1, weight=1)
        outputdirframe.rowconfigure(0, weight=1)

        # Button to do the thing
        doitbutton = ttk.Button(self, text='Do it', command=self.make_pack)

        # Status bar to display help
        self.helptextvar = StringVar()
        self.helptextvar.set('')

        statusframe = ttk.Frame(self, relief='sunken', **framekwds)

        ttk.Label(statusframe, textvariable=self.helptextvar).grid(column=0, row=0, sticky=E)

        statusframe.columnconfigure(0, weight=1)
        statusframe.rowconfigure(0, weight=1)

        # Grid 'em
        kwds = {
            'sticky' : NSEW,
            'padx':3,
            'pady':3,
            }
        
        notebook.grid(column=0, row=0, **kwds)
        outputdirframe.grid(column=0, row=1, **kwds)
        doitbutton.grid(column=0, row=2, sticky=N, pady=kwds['pady'])
        statusframe.grid(column=0, row=3, sticky=(S,W,E))
        
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=1)
        
    def _bind_display_help(self, widget, itemname):
        """Displays help text in status bar for item, if it is available"""
        helptext = self.helptexts.get(itemname, '')
        if helptext != '':
            def show_help(e):
                self.helptextvar.set(helptext)
            def clear_help(e):
                self.helptextvar.set('')
            widget.bind('<Enter>', show_help)
            widget.bind('<Leave>', clear_help)

    def make_pack(self):
        """Do the actual work here"""
        import json
        
        pack_info = {
            'packAuthor' : self.packinfovars['author'].get(),
            'packName' : self.packinfovars['name'].get(),
            'description' : self.packinfovars['description'].get(),
            }
        if self.packinfovars['thumbnail path'].get() == '' or not Path( self.packinfovars['thumbnail path'].get() ).is_file():
            pack_info['thumbnailPath'] = None
        else:
            pack_info['thumbnailPath'] = Path( self.packinfovars['thumbnail path'].get() ).resolve()
        
        music = dict()
        for track in self.musicdictlist:
            d = {
                'audioPath' : Path( track['audio path'] ).resolve(),
                'texturePath' : Path( track.get('texture path', '') ).resolve(),
                'useSpecialName' : track.get('special name', '') != '',
                'isShiny' : track.get('is shiny', '') != '',
                'hasLore' : track.get('lore', '') != '',
            }
            d['description'] = d['audioPath'].stem if track.get('description', '') == '' else track['description']
            if d['useSpecialName']:
                d['specialName'] = track['special name']
            if d['hasLore']:
                d['lore'] = track['lore']

            # Throw out bad tracks here?
            if Path(d['audioPath']).is_file() and d['texturePath'].is_file():
                clean_name = mt._processFilename(d['audioPath'].stem)
                music[clean_name] = d

        outputdir = Path( self.outputdirvar.get() ).resolve()

        # Some bad data handling
        print(self.packinfovars['thumbnail path'].get())
        # errors
        if not outputdir.is_dir():
            messagebox.showerror(title='Error: Bad Data', message='Output directory does not exist.')
        elif len(music) == 0:
            if len(self.musicdictlist) == 0:
                messagebox.showerror(title='Error: Bad Data', message='Track list is empty.')
            else:
                messagebox.showerror(title='Error: Bad Data', message='Track list does not contain any tracks with proper Audio and Texture files.')
        elif pack_info['packName'] == '':
            messagebox.showerror(title='Error: Bad Data', message='Pack has no name.')
        else:
            # warnings
            if len(self.musicdictlist) != len(music):
                messagebox.showwarning(title='Warning', message='Several tracks were skipped due to improper data.')
            if pack_info['thumbnailPath'] is None and self.packinfovars['thumbnail path'].get() != '':
                messagebox.showwarning(title='Warning', message='Given Thumbnail file does not exist, defaulting to None.')
            mt._makePack(music, pack_info, outputdir)
            self.helptextvar.set("Pack written in '%s'." % outputdir \
                + "\nMove to resource folder ('\\minecraft\\resourcepacks\\') and turn on in options to use.")

    def _make_music_frame(self, master, framekwds):
        '''Make the Music frame'''
        musicframe = ttk.Frame(master)

        default_texture = self.default_record_texture

        self.trackid = None

        # The Track list
        tracklistframe = ttk.LabelFrame(musicframe, text='Track List', **framekwds)
        
        # The Music listbox
        musiclistboxframe = ttk.Frame(tracklistframe, **framekwds)

        self.musicdictlist = []
        musicnamelistvar = StringVar()
        
        musiclistbox = Listbox(musiclistboxframe, listvariable=musicnamelistvar)
        musiclistbox.grid(column=0, row=0, sticky=(N,E,S,W))
        self._bind_display_help(musiclistbox, 'music listbox')

        w = ttk.Scrollbar(musiclistboxframe, orient=VERTICAL, command=musiclistbox.yview)
        musiclistbox.configure(yscrollcommand=w.set)
        w.grid(column=1, row=0, sticky=(N,S,W))
        self._bind_display_help(w, 'music listbox')
        
        musiclistboxframe.grid(column=0, row=0, columnspan=2, sticky=(N,W,S, E))
        
        musiclistboxframe.columnconfigure(0, weight=1)
        musiclistboxframe.columnconfigure(1, weight=1)
        musiclistboxframe.rowconfigure(0, weight=1)
        
        # The add track button
        def add_track(*args):
            '''create a new track and update the list box'''
            files = filedialog.askopenfilename(multiple=True, filetypes=[('OGG', '*.ogg')])
            for path in map(Path, files):
                self.musicdictlist.append( {
                    'description' : path.stem,
                    'audio path' : path,
                    'texture path' : '' if default_texture is None else Path(default_texture).resolve(),
                    } )
            musicnamelistvar.set(
                tuple( map(lambda x : x['description'], self.musicdictlist) )
                )
        
        w = ttk.Button(tracklistframe, text='Add Track(s)', command=add_track)
        w.grid(column=0, row=1, sticky=(N,W))
        self._bind_display_help(w, 'add track')

        # The remove track button
        def remove_track(*args):
            '''Delete selected track and update list box'''
            trackid=musiclistbox.curselection()
            if len(trackid)==1:
                del self.musicdictlist[trackid[0]]
                musicnamelistvar.set(
                    tuple( map(lambda x : x['description'], self.musicdictlist) )
                    )
        
        w = ttk.Button(tracklistframe, text='Remove Track', command=remove_track)
        w.grid(column=1, row=1, sticky=(N, W))
        self._bind_display_help(w, 'remove track')

        tracklistframe.columnconfigure(0, weight=1)
        tracklistframe.columnconfigure(1, weight=1)
        tracklistframe.rowconfigure(0, weight=1)
        tracklistframe.rowconfigure(1, weight=1)

        # Track info
        trackinfovars = {
            'description' : StringVar(),
            'audio path' : StringVar(),
            'texture path' : StringVar(),
            'special name' : StringVar(),
            'lore' : StringVar(),
            'is shiny' : StringVar(),
            }

        trackinfoframe = ttk.LabelFrame(musicframe, text='Track Info', **framekwds)
        
        w = ttk.Label(trackinfoframe, text='Track Description:')
        w.grid(column=0, row=0, sticky=E)
        self._bind_display_help(w, 'track description')

        w = ttk.Entry(trackinfoframe, textvariable=trackinfovars['description'], width=32)
        w.grid(column=1, row=0, sticky=W)
        self._bind_display_help(w, 'track description')

        def get_audio_path(*args):
            '''Get the audio file path, and set the description to the file name'''
            path = Path( filedialog.askopenfilename(filetypes=[('OGG', '*.ogg')]) )
            trackinfovars['audio path'].set(path)
            trackinfovars['description'].set(path.stem)
            
        audiopathframe = ttk.LabelFrame(trackinfoframe, text='*Audio File:', **framekwds)
        self._bind_display_help(audiopathframe, 'audio path')

        ttk.Entry(audiopathframe, textvariable=trackinfovars['audio path'], width=20).grid(column=0, row=0, sticky=(W,E))
        ttk.Button(audiopathframe, text='Browse', command=get_audio_path).grid(column=1, row=0, sticky=(W,E))

        audiopathframe.grid(column=0, row=1, columnspan=2, sticky=(N,S,E,W))

        audiopathframe.columnconfigure(0, weight=1)
        audiopathframe.columnconfigure(1, weight=1)
        audiopathframe.rowconfigure(0, weight=1)

        texturepathframe = ttk.LabelFrame(trackinfoframe, text='*Texture File:', **framekwds)
        self._bind_display_help(texturepathframe, 'texture path')

        ttk.Entry(texturepathframe, textvariable=trackinfovars['texture path'], width=20).grid(column=0, row=0, sticky=(W,E))
        ttk.Button(texturepathframe, text='Browse',
                   command=lambda *args : trackinfovars['texture path'].set(
                       Path( filedialog.askopenfilename(filetypes=[('PNG', '*.png')]) )
                       )
                   ).grid(column=1, row=0, sticky=(W,E))

        texturepathframe.grid(column=0, row=2, columnspan=2, sticky=(N,S,E,W))

        texturepathframe.columnconfigure(0, weight=1)
        texturepathframe.columnconfigure(1, weight=1)
        texturepathframe.rowconfigure(0, weight=1)

        trackoptionsframe = ttk.LabelFrame(trackinfoframe, text='Additional Options', **framekwds)

        w = ttk.Checkbutton(trackoptionsframe, text='Is Shiny', variable=trackinfovars['is shiny'])
        w.grid(column=0, row=0, columnspan=2)
        self._bind_display_help(w, 'is shiny')

        w = ttk.Label(trackoptionsframe, text='Special Name:')
        w.grid(column=0, row=1, sticky=E, pady=3)
        self._bind_display_help(w, 'special name')

        w = ttk.Entry(trackoptionsframe, textvariable=trackinfovars['special name'], width=32)
        w.grid(column=1, row=1, sticky=W, pady=3)
        self._bind_display_help(w, 'special name')

        w = ttk.Label(trackoptionsframe, text='Lore:')
        w.grid(column=0, row=2, sticky=E, pady=3)
        self._bind_display_help(w, 'lore')

        w = ttk.Entry(trackoptionsframe, textvariable=trackinfovars['lore'], width=32)
        w.grid(column=1, row=2, sticky=W, pady=3)
        self._bind_display_help(w, 'lore')
        
        trackoptionsframe.grid(column=0, row=3, columnspan=2, sticky=(N,S,E,W))

        trackoptionsframe.columnconfigure(0, weight=1)
        trackoptionsframe.columnconfigure(1, weight=1)
        trackoptionsframe.rowconfigure(0, weight=1)
        trackoptionsframe.rowconfigure(1, weight=1)
        trackoptionsframe.rowconfigure(2, weight=1)
        
        def set_info(*args):
            if self.trackid is not None and self.trackid < len(self.musicdictlist):
                for key, infovar in trackinfovars.items():
                    self.musicdictlist[self.trackid][key] = infovar.get()
                musicnamelistvar.set(
                    tuple( map(lambda x : x['description'], self.musicdictlist) )
                    )

        w = ttk.Button(trackinfoframe, text='Set Info', command=set_info)
        w.grid(column=0, row=4, columnspan=2, pady=3)
        self._bind_display_help(w, 'set track info')

        trackinfoframe.columnconfigure(0, weight=1)
        trackinfoframe.columnconfigure(1, weight=1)
        trackinfoframe.rowconfigure(0, weight=1)
        trackinfoframe.rowconfigure(1, weight=1)

        # Change info to display a track's current info
        def select_music(*args):
            '''Change display according to selected track'''
            trackid=musiclistbox.curselection()
            if len(trackid) == 1:
                self.trackid = trackid[0]
                for key,infovar in trackinfovars.items():
                    infovar.set( self.musicdictlist[trackid[0]].get(key, '') )
        
        musiclistbox.bind('<<ListboxSelect>>', select_music)

        tracklistframe.grid(column=0, row=0, sticky=(N,W,S, E))
        trackinfoframe.grid(column=1, row=0, sticky=(N,E,S,W))
        
        musicframe.columnconfigure(0, weight=1)
        musicframe.columnconfigure(1, weight=1)
        musicframe.rowconfigure(0, weight=1)

        return musicframe

    def _make_pack_info_frame(self, master, framekwds):
        '''Make the Pack info frame'''
        
        packinfoframe = ttk.Frame(master)
        # Pack info
        self.packinfovars = {
            'name' : StringVar(),
            'author' : StringVar(),
            'description' : StringVar(),
            'thumbnail path' : StringVar(),
            }

        for info in self.packinfovars.values():
            info.set('')
        
        self.packinfovars['description'].set('A Musica Pack')
        self.packinfovars['name'].set('Musica Resource Pack')

        w = ttk.Label(packinfoframe, text='*Pack Name:')
        w.grid(column=0, row=0, sticky=E)
        self._bind_display_help(w, 'pack name')

        w = ttk.Entry(packinfoframe, textvariable=self.packinfovars['name'], width=32)
        w.grid(column=1, row=0, sticky=W)
        self._bind_display_help(w, 'pack name')

        w = ttk.Label(packinfoframe, text='Pack Author:')
        w.grid(column=2, row=0, sticky=E)
        self._bind_display_help(w, 'pack author')

        w = ttk.Entry(packinfoframe, textvariable=self.packinfovars['author'], width=32)
        w.grid(column=3, row=0, sticky=W, padx=3)
        self._bind_display_help(w, 'pack author')

        w = ttk.Label(packinfoframe, text='Pack Description:')
        w.grid(column=0, row=1, sticky=E, padx=3)
        self._bind_display_help(w, 'pack description')

        w = ttk.Entry(packinfoframe, textvariable=self.packinfovars['description'], width=32)
        w.grid(column=1, row=1, sticky=W)
        self._bind_display_help(w, 'pack description')

        # thumbnail file selection
        self.thumbnailfilepathvar = StringVar()
        self.thumbnailfilepathvar.set('')

        thumbnailfileframe = ttk.LabelFrame(packinfoframe, text='Pack Thumbnail File:', **framekwds)
        self._bind_display_help(thumbnailfileframe, 'thumbnail path')
        ttk.Entry(thumbnailfileframe, textvariable=self.packinfovars['thumbnail path'], width=32).grid(column=0, row=0, sticky=(W,E))
        ttk.Button(thumbnailfileframe, text='Browse',
                   command=lambda *args : self.packinfovars['thumbnail path'].set(
                       Path( filedialog.askopenfilename(filetypes=[('PNG', '*.png')]) )
                       )
                   ).grid(column=1, row=0, sticky=(E,W))

        thumbnailfileframe.columnconfigure(0, weight=1)
        thumbnailfileframe.columnconfigure(1, weight=1)
        thumbnailfileframe.rowconfigure(0, weight=1)

        thumbnailfileframe.grid(column=2, row=1, columnspan=2, padx=3)

        packinfoframe.columnconfigure(0, weight=1)
        packinfoframe.columnconfigure(1, weight=1)
        packinfoframe.columnconfigure(2, weight=1)
        packinfoframe.columnconfigure(3, weight=1)
        packinfoframe.rowconfigure(0, weight=1)
        packinfoframe.rowconfigure(1, weight=1)

        return packinfoframe
        

if __name__ == '__main__':
    root = Tk()
    root.title('Musica Resource Pack-o-tron')
    root.option_add('*tearOff', FALSE)

    # Main Background Frame
    main_frame = MusicaApp(root)
    main_frame.grid(column=0, row=0, sticky=(N, W, E, S))
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)

    root.mainloop()
