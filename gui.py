import function
from tkinter import Button as tkbtn
import tkinter.font as tkFont
from tkinter import messagebox as tkmsg
from tkinter import Tk as tK

try:
    # Setting the GUI menu
    root = tK()
    root.title("In cell western counter")
    root.state('zoomed')

    # selecting the font
    helv36 = tkFont.Font(family='Helvetica', size=30, weight=tkFont.BOLD)

    # button for single plate
    btn_single = tkbtn(root, text = 'Single Well Counter',command=lambda: function.single_counter(),width=50, font=helv36)
    btn_single.pack(side = 'top')
    btn_single.config(width=50)

    # button for multi plate
    btn_plate = tkbtn(root, text='Plate Counter', command=lambda: function.plate_counter(), width=50, font=helv36)
    btn_plate.pack(side='top')
    btn_plate.config(width=50)

    # button for closing
    btn_close = tkbtn(root, text = 'Close!', command=root.destroy,width=50,font=helv36)
    btn_close.pack(side = 'bottom')
    btn_close.configure(width=50)
    root.mainloop()

except:
    tkmsg.showinfo(title='Error', message='Retry Button')
    pass