from MusicPlayer import MusicPlayer
import customtkinter

customtkinter.set_appearance_mode("System")
customtkinter.set_default_color_theme("green")

root = customtkinter.CTk()
MusicPlayer(root)

root.mainloop()
