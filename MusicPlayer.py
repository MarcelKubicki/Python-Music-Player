import tkinter
import pygame
import customtkinter
from tkinter import filedialog
import time
from mutagen.mp3 import MP3
from mutagen.id3 import ID3
from PIL import Image
from io import BytesIO


class MusicPlayer:

    def __init__(self, root):
        self.root = root

        self.root.title("Music Player")
        self.root.geometry("480x600")
        self.root.resizable(False, False)

        self.loaded_music = []
        self.active_song = ""
        self.stopped = False
        pygame.mixer.init()

        self.play_button = customtkinter.CTkButton(master=self.root, text="▶", command=self.play_music, width=80)
        self.play_button.place(relx=0.5, rely=0.5, anchor=tkinter.CENTER)

        skip_forward_button = customtkinter.CTkButton(master=self.root, text="⏭", command=self.skip_forward, width=2)
        skip_forward_button.place(relx=0.62, rely=0.5, anchor=tkinter.CENTER)

        skip_backward_button = customtkinter.CTkButton(master=self.root, text="⏮", command=self.skip_backward, width=2)
        skip_backward_button.place(relx=0.38, rely=0.5, anchor=tkinter.CENTER)

        slider = customtkinter.CTkSlider(master=self.root, from_=0, to=1, command=self.adjust_volume,
                                         orientation="vertical")
        slider.place(relx=0.9, rely=0.25, anchor=tkinter.CENTER)

        self.progressbar = customtkinter.CTkSlider(master=self.root, from_=0, to=100, width=250)
        self.progressbar.set(0)
        self.progressbar.place(relx=0.5, rely=0.55, anchor=tkinter.CENTER)

        self.current_time = customtkinter.CTkLabel(master=self.root, text="00:00")
        self.current_time.place(relx=0.17, rely=0.548, anchor=tkinter.CENTER)

        self.total_time = customtkinter.CTkLabel(master=self.root, text="00:00")
        self.total_time.place(relx=0.83, rely=0.548, anchor=tkinter.CENTER)

        import_button = customtkinter.CTkButton(master=self.root, text="+ Import Music", command=self.import_music)
        import_button.place(relx=0.2, rely=0.6, anchor=tkinter.CENTER)

        delete_song = customtkinter.CTkButton(master=self.root, text="- Delete song", command=self.delete_song)
        delete_song.place(relx=0.5, rely=0.6, anchor=tkinter.CENTER)

        delete_all = customtkinter.CTkButton(master=self.root, text="x Delete all", command=self.delete_all)
        delete_all.place(relx=0.8, rely=0.6, anchor=tkinter.CENTER)

        self.playlist = customtkinter.CTkFrame(master=self.root, width=400, height=200)
        self.playlist.place(relx=0.5, rely=0.81, anchor=tkinter.CENTER)

        self.listbox = tkinter.Listbox(self.playlist, bg='#4f4f4d', fg='#ffffff', selectbackground='#449e55',
                                       selectforeground='#ffffff', width=47,)
        self.listbox.pack(side="left", fill="both", expand=True)

        scrollbar = customtkinter.CTkScrollbar(self.playlist, command=self.listbox.yview)
        scrollbar.pack(side="right", fill="y")

        self.listbox.config(yscrollcommand=scrollbar.set)

        album_cover_image = customtkinter.CTkImage(light_image=Image.open("./images/default_album_cover.jpeg"),
                                                   dark_image=Image.open("./images/default_album_cover.jpeg"),
                                                   size=(250, 250))
        self.album_cover_label = customtkinter.CTkLabel(master=self.root, image=album_cover_image, text="")
        self.album_cover_label.place(relx=0.5, rely=0.25, anchor=tkinter.CENTER)

        volume_image = customtkinter.CTkImage(light_image=Image.open("images/volume_icon.png"),
                                              dark_image=Image.open("images/volume_icon.png"),
                                              size=(30, 30))
        volume_label = customtkinter.CTkLabel(master=self.root, image=volume_image, text="", fg_color="transparent")
        volume_label.place(relx=0.9, rely=0.048, anchor=tkinter.CENTER)

        self.current_volume = customtkinter.CTkLabel(master=self.root, text="50")
        self.current_volume.place(relx=0.9, rely=0.45, anchor=tkinter.CENTER)

    def play_music(self):
        checked_song = self.listbox.get(tkinter.ACTIVE)

        directory = ""
        for song in self.loaded_music:
            if song["file_name"] == checked_song:
                directory = song["directory"]

        self.display_album_cover(directory)

        if checked_song == self.active_song:
            if pygame.mixer.music.get_busy():
                pygame.mixer.music.pause()
                self.play_button.configure(text="▶")
            else:
                pygame.mixer.music.unpause()
                self.play_button.configure(text="▐▐")
        else:
            self.active_song = checked_song
            pygame.mixer.music.load(directory)
            pygame.mixer.music.play(loops=0)
            self.play_button.configure(text="▐▐")
            self.get_total_song_time(directory)
            self.progressbar.set(0)

        self.play_time()

    def skip_forward(self):
        current_song = self.listbox.curselection()

        next_song = current_song[0] + 1
        if next_song == self.listbox.size():
            next_song = 0

        self.listbox.selection_clear(0, tkinter.END)
        self.listbox.activate(next_song)
        self.listbox.selection_set(next_song, last=None)
        self.play_music()
        self.stopped = True

    def skip_backward(self):
        current_song = self.listbox.curselection()

        prev_song = current_song[0] - 1
        if prev_song < 0:
            prev_song = self.listbox.size() - 1

        self.listbox.selection_clear(0, tkinter.END)
        self.listbox.activate(prev_song)
        self.listbox.selection_set(prev_song, last=None)
        self.play_music()
        self.stopped = True

    def adjust_volume(self, value):
        pygame.mixer.music.set_volume(value)
        self.current_volume.configure(text=int(value * 100))

    def import_music(self):
        filetypes = (
            ('audio files', '*.mp3'),

        )
        file_paths = filedialog.askopenfilenames(title="Select audio files", filetypes=filetypes)

        for file_path in file_paths:
            file_name = ''
            is_looking = True
            i = -1
            while is_looking:
                if file_path[i] == "/":
                    is_looking = False
                else:
                    file_name += file_path[i]
                i -= 1
            reversed_name = file_name[::-1]
            reversed_name = reversed_name.replace(".mp3", "")
            self.loaded_music.append({
                "directory": file_path,
                "file_name": reversed_name
            })
            if reversed_name not in self.listbox.get(0, tkinter.END):
                self.listbox.insert(tkinter.END, reversed_name)
            if self.listbox.curselection() == ():
                self.listbox.activate(0)
                self.listbox.selection_set(0, last=0)

    def delete_song(self):
        self.listbox.delete(tkinter.ANCHOR)
        pygame.mixer.music.stop()
        self.play_button.configure(text="▶")
        self.current_time.configure(text="00:00")
        self.progressbar.set(0)

    def delete_all(self):
        self.listbox.delete(0, tkinter.END)
        pygame.mixer.music.stop()
        self.play_button.configure(text="▶")
        self.current_time.configure(text="00:00")
        self.progressbar.set(0)

    def play_time(self):

        if self.stopped:
            self.stopped = False
            return

        current_time = pygame.mixer.music.get_pos() / 1000

        converted_time = time.strftime("%M:%S", time.gmtime(current_time))

        if int(self.progressbar.get()) == int(self.progressbar.cget("to")):
            self.current_time.configure(text=time.strftime("%M:%S", time.gmtime(self.progressbar.cget("to"))))
            self.skip_forward()
        elif not pygame.mixer.music.get_busy():
            return
        elif int(self.progressbar.get()) == int(current_time):
            # progressbar unmoved
            current_time += 1
            self.progressbar.set(float(current_time))
            self.current_time.configure(text=converted_time)
        else:
            # progressbar moved
            self.progressbar.set(int(self.progressbar.get()))
            converted_time = time.strftime("%M:%S", time.gmtime(int(self.progressbar.get())))
            pygame.mixer.music.rewind()
            pygame.mixer.music.set_pos(self.progressbar.get())
            self.current_time.configure(text=converted_time)
            next_sec = int(self.progressbar.get()) + 1
            self.progressbar.set(next_sec)

        # self.current_time.configure(text=converted_time)

        self.current_time.after(1000, self.play_time)

    def get_total_song_time(self, song_directory):
        song = MP3(song_directory)
        song_length = song.info.length
        converted_time = time.strftime("%M:%S", time.gmtime(song_length))
        self.total_time.configure(text=converted_time)
        self.progressbar.configure(to=int(song_length))

    def display_album_cover(self, directory):

        audio = MP3(filename=directory, ID3=ID3)
        if audio.tags is None:
            my_image = customtkinter.CTkImage(light_image=Image.open("./images/default_album_cover.jpeg"),
                                              dark_image=Image.open("./images/default_album_cover.jpeg"),
                                              size=(250, 250))
            self.album_cover_label.configure(image=my_image)
        else:
            for tag in audio.tags.values():
                if tag.FrameID == "APIC":
                    image_data = BytesIO(tag.data)
                    image = Image.open(image_data)
                    my_image = customtkinter.CTkImage(light_image=image,
                                                      dark_image=image,
                                                      size=(250, 250))
                    self.album_cover_label.configure(image=my_image)
