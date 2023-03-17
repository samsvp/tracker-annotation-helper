from tkinter import *    
from PIL import Image, ImageTk


class ExampleApp(Frame):
    def __init__(self,master):
        Frame.__init__(self,master=None)
        self.x = 0
        self.y = 0
        self.curX = 0
        self.curY = 0
        self.canvas = Canvas(self, cursor="cross")

        self.canvas.grid(row=0,column=0,sticky=N+S+E+W)

        self.canvas.bind("<ButtonPress-1>", self.on_button_press)
        self.canvas.bind("<B1-Motion>", self.on_move_press)
        self.canvas.bind("<ButtonRelease-1>", self.on_button_release)

        self.rect = None

        self.start_x = None
        self.start_y = None

        self.im = Image.open("frame_271.jpg")
        self.master = master
        self.master.geometry(f"{self.im.width}x{self.im.height}")
        self.master.bind("<Configure>", self.resize_image)

        self.canvas.config(
            width=self.im.width, height=self.im.height,
            scrollregion=(0, 0, self.im.width, self.im.height))
        self.tk_im = ImageTk.PhotoImage(self.im)
        self.canvas_image = self.canvas.create_image(0,0,anchor="nw",image=self.tk_im)   


    def on_button_press(self, event):
        # save mouse drag start position
        self.start_x = self.canvas.canvasx(event.x)
        self.start_y = self.canvas.canvasy(event.y)

        # create rectangle if not yet exist
        if not self.rect:
            self.rect = self.canvas.create_rectangle(self.x, self.y, 1, 1, outline='red')


    def on_move_press(self, event):
        self.curX = self.canvas.canvasx(event.x)
        self.curY = self.canvas.canvasy(event.y)

        w, h = self.canvas.winfo_width(), self.canvas.winfo_height()
        if event.x > 0.9*w:
            self.canvas.xview_scroll(1, 'units') 
        elif event.x < 0.1*w:
            self.canvas.xview_scroll(-1, 'units')
        if event.y > 0.9*h:
            self.canvas.yview_scroll(1, 'units') 
        elif event.y < 0.1*h:
            self.canvas.yview_scroll(-1, 'units')

        # expand rectangle as you drag the mouse
        self.canvas.coords(self.rect, self.start_x, self.start_y, self.curX, self.curY)    


    def on_button_release(self, event):
        print(self.start_x, self.start_y, self.curX, self.curY)
        pass    


    def resize_image(self, event):
        new_width = event.width - 10
        new_height = event.height - 10
        photo1 = ImageTk.PhotoImage(self.im.resize((new_width, new_height), Image.BICUBIC))
        self.canvas.image = photo1
        self.canvas.itemconfig(self.canvas_image, image=photo1)


if __name__ == "__main__":
    root = Tk()
    app = ExampleApp(root)
    app.pack()
    root.mainloop()