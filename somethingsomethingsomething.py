# from tkinter import *
# window=Tk()
# window.title('demo window')
# window.geometry("400x300")
# window.mainloop()

from  tkinter import *
from datetime import date
root=Tk()

root.title('getting started with wigits')
root.geometry('400x300')
lbl=Label(text="hey there",bg="blue",fg="red")
lblbnoob=Label(text="full name",bg="#201508")
namenoobynoobnoob=Entry()
def display():
    name=namenoobynoobnoob.get()
    global Message
    Message="greeting elder application!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\nToday's young date is:"
    groot="hello "+name+"\n"
    text_box.insert(END,groot)
    text_box.insert(END,Message)
    text_box.insert(END, date.today())

text_box=Text(height=5)

msg=Button(text="Begin",command=display,height=1,bg="#999997")
lbl.pack()
lblbnoob.pack()
namenoobynoobnoob.pack()
msg.pack()
text_box.pack()
root.mainloop()