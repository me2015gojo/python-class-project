from tkinter import *

root=Tk()
root.title('Login App')
root.geometry('400x400')
frame=Frame(master=root, height=200, width=360,bg="#c2c1d9")
lblnoob1=Label(frame,text="full name",bg="#2015D8")
lblnoob2=Label(frame,text="enter de email",bg="#be3535")
lblnoob99=Label(frame,text="enter je passworde",bg="#12125f")

name_entry=Entry(frame)
email_entry=Entry(frame)
pass_entry=Entry(frame, show="*")
def display():
    name=name_entry.get()
    greet="hey" +name
    message="\nCongratulations for your new account papoi "
    textbox.insert(END,greet)
    textbox.insert(END,message)

textbox=Text(bg="#040101", fg="white")
btn=Button(text="create account",command=display,bg="grey")
frame.place(x=20,y=0)
lblnoob1.place(x=20,y=20)
name_entry.place(x=150, y=20)
lblnoob2.place(x=20,y=80)
email_entry.place(x=150,y=80)
lblnoob99.place(x=20,y=140)
pass_entry.place(x=150,y=140)
btn.place(x=130,y=210)
textbox.place(y=250)
root.mainloop()