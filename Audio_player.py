import threading
from tkinter import *
import os
from mutagen.mp3 import MP3
from PIL import ImageTk
import pygame
import time
from tkinter import messagebox, filedialog


#***************************** to run two function simultaneously *****************************#
def combine_funcs(*funcs):
    def combined_func(*args, **kwargs):
        for f in funcs:
            f(*args, **kwargs)
    return combined_func

#***************************** making list of songs *****************************#
def songs_list():
    files = [file for file in os.listdir('ringtone')]
    List = []
    for file in files:
        List.append(str(file))
        #print(file)
    #print(List)
    return List

#***************************** length of song*****************************#
def song_length():
    List_ = songs_list()
    song_len = dict()
    for song in List_:
        try:
            audio = MP3("./ringtone/" + song)
        except:
            audio = MP3(song)
        song_len[song] = audio.info.length
    return song_len

#***************************** Global Variables *****************************#

n=0 # to store song play/pause position
song = '' # to store current song name
new_pos = 0  # time seek
sp = 0  # next
sp1 = 0 # prev
#***************************** Play Control *****************************#
def start(song_name, folder_type='Default_Folder'):
    global new_pos
    new_pos = 0
    song_len = song_length()
    global song
    song = song_name
    global n
    n += 1
    song_name_label['text'] = "Now Playing: " + song_name
    pygame.mixer.init()
    if folder_type == 'Default_Folder':
        pygame.mixer.music.load("./ringtone/" + song_name)
    else:
        pygame.mixer.music.load(song_name)

    print("Playing:", song_name)
    play_pause_button['text'] = "Pause"
    pygame.mixer.music.unpause()
    pygame.mixer.music.play(0)
    n += 1

pause = False #to detect pause while running thread
def play_pause(song_name):
    global pause
    global n
    n += 1
    #print(song, "checking")
    if song == song_name:
        if n%2 == 0:
            play_pause_button['text'] = 'Pause'
            pygame.mixer.music.unpause()
            pause = False
            print("unpaused")
        elif n%2 !=0:
            play_pause_button['text'] = "Resume"
            pygame.mixer.music.pause()
            pause = True
            print("paused")
    else:
        n = 0
        play_pause_button['text'] = "Pause"

#***************************** next and Prev *****************************#
def next():
    global stop_event
    global new_pos
    new_pos = 0
    global sp
    if sp != 0 or pygame.mixer.music.get_busy():
        stop_event.set()
    else:
        stop_event.clear()
    #stop_event.set()
    global song
    selection_indices = listbox.curselection()
    # default next selection is the beginning
    #global next_selection
    global next_selection
    next_selection = 0
    # make sure at least one item is selected
    if len(selection_indices) > 0:
        # Get the last selection, remember they are strings for some reason
        # so convert to int
        last_selection = int(selection_indices[-1])
        # clear current selections
        listbox.selection_clear(selection_indices)
        # Make sure we're not at the last item
        if last_selection < listbox.size() - 1:
            next_selection = last_selection + 1

    listbox.activate(next_selection)
    listbox.selection_set(next_selection)
    song = listbox.get(next_selection)
    sp += 1
    get_time()

def previous():
    global stop_event
    global new_pos
    new_pos = 0
    global sp1
    if sp1 != 0 or pygame.mixer.music.get_busy():
        stop_event.set()
    else:
        stop_event.clear()
    #stop_event.set()
    global song
    List_song = songs_list()
    selection_indices = listbox.curselection()
    index = len(List_song)
    # default next selection is the beginning
    # global next_selection
    global prev_selection
    prev_selection = 0
    # make sure at least one item is selected
    if len(selection_indices) > 0:
        # Get the last selection, remember they are strings for some reason
        # so convert to int
        last_selection = int(selection_indices[-1])

        # clear current selections
        listbox.selection_clear(selection_indices)
        # Make sure we're not at the last item
        if last_selection == 0:
            prev_selection = index-1
        else:
            prev_selection = last_selection - 1

    listbox.activate(prev_selection)
    listbox.selection_set(prev_selection)
    song = listbox.get(prev_selection)
    sp1 += 1
    #time.sleep(0.8)
    get_time()

#***************************** song seeking *****************************#
def song_seek(pos):
    global song
    print('inside seek', song)
    song_len = song_length()
    global new_pos
    #song_slider['to'] = song_len[song]
    new_pos = int(pos)
    print('inside seek', new_pos)

#***************************** song playing time *****************************#
stop_event = threading.Event()
m = 0 #to restart current playing time in when get_time clicked again
def get_time():
    global stop_event
    global m
    if m != 0:
        stop_event.set()

    global song
    song_len = song_length() #dictionary
    total_length = song_len[song]  # import mutagen and use audio.info.length instead song_len[song]

    hours = total_length // 3600
    # store quotient and remainder in mins and secs respectively
    mins, secs = divmod(total_length, 60)
    mins = round(mins)
    secs = round(secs)
    hours = round(hours)
    time_format = '{}:{:02d}:{:02d}'.format(hours, mins, secs)
    print('total-time: ',time_format)
    total_time['text'] = time_format
    global t1
    t1 = threading.Thread(target=time_start, args=(total_length,))
    t1.daemon = True
    t1.start()
    m +=1


def time_start(t):
    global stop_event
    global pause
    global new_pos
    current = 0
    song_slider['to'] = t
    while t and pygame.mixer.music.get_busy():  
        if pause:
            continue
        else:
            if new_pos != current:
                current = int(new_pos)
                pygame.mixer.music.set_pos(new_pos)

            elif stop_event.is_set()==True:
                new_pos = 0
                song_slider.set(0)
                stop_event.clear() # to clear event set
                break

            current_hours = current // 3600
            current_mins, current_secs = divmod(current, 60)
            current_hours = round(current_hours)
            current_mins = round(current_mins)
            current_secs = round(current_secs)
            current_time_format = '{:0}:{:02d}:{:02d}'.format(current_hours, current_mins, current_secs)
            current_time['text'] = current_time_format
            song_slider.set(current)
            print(current_time_format)
            time.sleep(1)
            new_pos += 1
            current += 1
            t -= 1

    print('song ended')
    global m , n, sp, sp1
    print('m = ', m, "| n = ", n, "| sp = ", sp, "| sp1 = ", sp1 )

#***************************** Volume Controls *****************************#
new_volume =30
def set_vol(vol):
    global new_volume
    new_volume = int(vol)/100
    #print(new_volume)
    pygame.mixer.init()
    pygame.mixer.music.set_volume(new_volume)
    sound()

def mute():
    global new_volume
    global g
    if new_volume == 0:
        vol_scale.set(40)
    else:
        vol_scale.set(0)
        new_volume = 0

def sound():
    global new_volume
    #print('new volume: ', new_vol)
    if new_volume == 0:
        vol_icon['text'] = '🔇'
    else:
        vol_icon['text'] = '🔊'

# to close GUI
def exit_GUI():
    exit()
# dev info

def dev_info():
    messagebox.showinfo(title='DEV', message='''    This is Dhruv Singh, B.tech(CSE) student.
    A Simple_Audio PLayer,  completely devlop using Python 3.8
    Release Date - 15-08-2020
    
    Contact:
    Linkedin - https://www.linkedin.com/in/dhruv-singh-25ba02172/''')

def explorer():
    song_len = songs_list()
    filename = filedialog.askopenfilename(initialdir="/", title="Select a File",
        filetypes=(("Audio files","*.mp3*"),("all files","*.*")))

    listbox.insert(END, filename)
    song = filename.split('-', 1)[1]
    audio = MP3(filename)
    print(audio.info.length)
    song_len.append(filename)
    start(filename, 'Rand_Folder')

    print(song)

#***************************** GUI *****************************#
window = Tk()
window .title("MAx PLayer")
window.geometry("1280x800+100+50")

#***************************** background image *****************************#
image_show = ImageTk.PhotoImage(file='image/bg13.jpg')
bg_image = Label(window, image=image_show)
bg_image.place(relx=0, rely=0, relwidth=1, relheight=1)

#***************************** nav bar *****************************#
nav_frame = Frame(window, bg='black')
nav_frame.place(relx=0, rely=0, relwidth=1, relheight=0.035)

# Create a menu button
File_menubutton = Menubutton(nav_frame, text="File", bg='black', fg='white', bd=0)
File_menubutton.place(relx=0.0, rely=0, relheight=1, relwidth=0.03)

# Create pull down menu
File_menubutton.menu = Menu(File_menubutton, tearoff = 0)
File_menubutton["menu"] = File_menubutton.menu

# Add some commands
#File_menubutton.menu.add_command(label="Create new")
File_menubutton.menu.add_command(label="Open", command=explorer)
File_menubutton.menu.add_separator()
File_menubutton.menu.add_command(label="Exit", command=exit_GUI)

#about button
About_menubutton = Menubutton(nav_frame, text="About", bg='black', fg='white', bd=0)
About_menubutton.place(relx=0.03, rely=0, relheight=1, relwidth=0.03)

# Create pull down menu
About_menubutton.menu = Menu(About_menubutton, tearoff = 0)
About_menubutton["menu"] = About_menubutton.menu

# Add some commands
About_menubutton.menu.add_command(label="About DEV", command=dev_info)
About_menubutton.menu.add_command(label="Features")


#***************************** song name *****************************#
song_name_frame = Frame(window, bg='grey')
song_name_frame.place(relx=0.30, rely=0.06, relheight=0.05, relwidth=0.40)
song_name_label = Label(song_name_frame,font=("times now roman", 10), text="Always listen to your heart!")
song_name_label.place(relx=0.0, rely=0, relheight=1, relwidth=1)


#***************************** play control separator *****************************#
line = Frame(window)
line.place(relx=0, rely=0.84, relheight=0.001, relwidth=1)

cover = Frame(window, bg='black')
cover.place(relx=0.93, rely=0.92, relheight=0.08,relwidth=0.07)

#***************************** play button *****************************#
play_button_frame = Frame(window, bg='black')
play_button_frame.place(relx=0.11, rely=0.92, relheight=0.05, relwidth=0.10)
play_pause_button = Button(play_button_frame, text="Pause", font=("times now roman", 10), bd=0, fg='#d1d1d1', bg='black',
                        command=lambda: play_pause(listbox.get(listbox.curselection())))
play_pause_button.place(relx=0, rely=0, relheight=1, relwidth=0.5)

#***************************** Start button *****************************#
Start_button = Button(play_button_frame, text="►", font=("times now roman", 15, 'bold'), bd=0, fg='#d1d1d1', bg='black',
                        command=combine_funcs(lambda: start(listbox.get(listbox.curselection())), get_time))
Start_button.place(relx=0.5, rely=0, relheight=1, relwidth=0.5)

#***************************** prev button *****************************#
prev_button_frame = Frame(window, bg='black')
prev_button_frame.place(relx=0.06, rely=0.92, relheight=0.05, relwidth=0.05)
prev_button = Button(prev_button_frame, text="◄◄",font=("times now roman", 15, 'bold'), bd=0, fg='#d1d1d1', bg='black',
                                command=combine_funcs(previous ,lambda: start(listbox.get(listbox.curselection()))))
prev_button.place(relx=0.0, rely=0, relheight=1, relwidth=1)

#***************************** next button *****************************#
next_button_frame = Frame(window, bg='black')
next_button_frame.place(relx=0.21, rely=0.92, relheight=0.05, relwidth=0.05)
next_button = Button(next_button_frame, text='►►',font=("times now roman", 15, 'bold'),bd=0, fg='#d1d1d1', bg='black',
                                command=combine_funcs(next,
                        lambda: start(listbox.get(listbox.curselection()))))
next_button.place(relx=0.0, rely=0, relheight=1, relwidth=1)

#***************************** volume control *****************************#
vol_frame = Frame(window, bg='black', bd=0)
vol_frame.place(relx=0.80, rely=0.92, relheight=0.05, relwidth=0.13)
vol_scale = Scale(vol_frame,font=("times now roman", 10),   from_=0,
                     orient='horizontal', bg='black', fg='white', bd=0, highlightthickness=0, command=set_vol)
vol_scale.place(relx=0.0, rely=0, relheight=1, relwidth=1)
vol_scale.set(40)

#***************************** vol icon button  *****************************#
vol_icon_frame = Frame(window, bg='black')
vol_icon_frame.place(relx=0.76, rely=0.93, relheight=0.04, relwidth=0.03)
vol_icon = Button(vol_icon_frame, font=("times now roman", 18),bd=0, text='🔇', bg='black', fg='white', command=mute)
vol_icon.place(relx=0, rely=0, relheight=1, relwidth=1)

#***************************** song slider *****************************#
song_slider_Frame = Frame(window, bg='black', bd=0)
song_slider_Frame.place(relx=0.06, rely=0.85, relheight=0.05, relwidth=0.88)
song_slider = Scale(song_slider_Frame, orient='horizontal', bd=0, fg='white',highlightthickness=0,
                    bg='black', from_=0, to=100,command=song_seek)
song_slider.place(relx=0, rely=0, relheight=1, relwidth=1)

#***************************** current_play_ime *****************************#
current_time_frame = Frame(window, bg='black')
current_time_frame.place(relx=0.01, rely=0.86, relheight=0.04, relwidth=0.04)
current_time = Label(current_time_frame, text='--:--', bd=0, bg='black', fg='white')
current_time.place(relx=0.0, rely=0, relheight=1, relwidth=1)

#***************************** total time *****************************#
total_time_frame = Frame(window, bg='black')
total_time_frame.place(relx=0.95, rely=0.86, relheight=0.04, relwidth=0.04)
total_time = Label(total_time_frame, text='--:--',bd=0,  bg='black', fg='white')
total_time.place(relx=0.0, rely=0, relheight=1, relwidth=1)

#***************************** Playlist Label *****************************#
P_label_Frame = Frame(window, bg='grey')
P_label_Frame.place(relx=0.8, rely=0, relwidth=0.2, relheight=0.1)

P_label = Label(P_label_Frame, bg='grey', fg='black',text='Playlist' , font=('Wide Latin', 25, 'italic' ))
P_label.place(relx=0,rely=0, relheight=1, relwidth=1)

#***************************** list box (playlist) *****************************#
image_lbg = ImageTk.PhotoImage(file='image/lbg.jpg')
listbox_frame = Frame(window, bg='#4d0000', bd=0)
listbox_frame.place(relx=0.8, rely=0.1, relheight=0.74, relwidth=0.2)
listbox = Listbox(listbox_frame, bd=0, bg='black', fg='white', selectmode='ACTIVE',highlightthickness=0, selectbackground="grey")
listbox.place(relx=0.0, rely=0.03, relheight=1, relwidth=1)
#listbox['image'] = image_lbg
#***************************** PLaylist *****************************#
playlist = songs_list()
for item in playlist:
    listbox.insert(END, item)
# auto selecting 1st element of list box
listbox.selection_set( first = 0 )
'''for name in sorted(tkinter.font.families()):
    print(name)'''
window.mainloop()



