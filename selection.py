import time
from tkinter import *

import numpy as np
from PIL import ImageTk
import pyautogui


class AreaSelection:
    def __init__(self, window, callback):
        self.window = window
        self.window.withdraw()
        self.callback = callback

        self.screen = Toplevel(window)
        self.screen.attributes('-fullscreen', True)
        time.sleep(0.3)

        self.image_screen = pyautogui.screenshot()

        self.canvas = Canvas(self.screen, width=self.image_screen.width, height=self.image_screen.height)
        self.canvas.pack()

        self.selection = None
        self.start_x = None
        self.start_y = None

        """
        размещение скриншота экрана для 
        дальнейшего отображения на нем выделенной области
        """
        self.photo = ImageTk.PhotoImage(self.image_screen)
        self.canvas.config(scrollregion=self.canvas.bbox("all"))
        self.canvas.create_image(0, 0, anchor="nw", image=self.photo)

        """
        реакция на мышь
        """
        self.canvas.bind("<ButtonPress-1>", self.on_click)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        self.screen.bind("<Escape>", self.close_screen)

    def close_screen(self, event):
        self.screen.destroy()
        self.window.deiconify()
        self.callback(None)

    def on_click(self, event):
        self.start_x = self.canvas.canvasx(event.x)
        self.start_y = self.canvas.canvasy(event.y)

        if self.selection:
            self.canvas.delete(self.selection)

        self.selection = self.canvas.create_rectangle(self.start_x, self.start_y, self.start_x, self.start_y,
                                                      outline="red")
    """
    действие при зажатии
    """
    def on_drag(self, event): # при перетаскивании
        cur_x = self.canvas.canvasx(event.x)
        cur_y = self.canvas.canvasy(event.y)

        self.canvas.coords(self.selection, self.start_x, self.start_y, cur_x, cur_y)
    """
    действие при перетаскивании
    """
    def on_release(self, event):  # при отпускании
        cur_x = self.canvas.canvasx(event.x)
        cur_y = self.canvas.canvasy(event.y)
        self.show_selected_area(cur_x, cur_y)
    """
    действие при отпускании
    """
    def show_selected_area(self, cur_x, cur_y):
        x1, y1, x2, y2 = self.canvas.coords(self.selection)
        label_text = "Сделать снимок"
        label = Label(self.screen, text=label_text)
        label.pack(pady=0)
        label.config(fg="blue", cursor="hand2")
        label_coords = (max(x1, x2), max(y1, y2))
        label.place(x=label_coords[0], y=label_coords[1], anchor=SE)
        label.bind("<ButtonRelease-1>", lambda event: self.end_show())

    def end_show(self):
        x1, y1, x2, y2 = self.canvas.coords(self.selection)
        coords = (
                int(min(x1,x2)),
                int(min(y1,y2)),
                int(max(x1,x2)),
                int(max(y1,y2)),
        )

        self.image_screen = self.image_screen.crop(coords)

        image_tk = ImageTk.PhotoImage(self.image_screen)
        img_txt = np.array(ImageTk.getimage(image_tk))

        self.screen.destroy()
        self.window.deiconify()

        self.callback(img_txt)