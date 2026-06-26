#Library System
# Build a simple library system using a class. Each book is an object. Your system lets users borrow and return books and tracks whether each book is currently available.

# What you need to use
# ------------------------------------------------------------------------
# 1.  Book class      →  __init__ sets title, author, and is_borrowed = False
# 2.  borrow()        →  sets is_borrowed to True and prints a confirmation
# 3.  return_book()   →  sets is_borrowed to False and prints a confirmation
# 4.  3 Book objects  →  demonstrate both borrow() and return_book()
# 5.  self            →  used to access and update attributes inside methods

class book:
    def __init__(self,author,title):
        self.author=author
        self.title=title
        self.is_borrowed=False
    def borrow(self):
        if not self.is_borrowed:
            self.is_borrowed=True
            print(f'conform {self.title}has been borrowed')
        else:
            print('sorry ur book has already been taken')
    def giveback(self):
        if  self.is_borrowed:
            self.is_borrowed= False
            print('thank you for da service ur book has been retuened')
        else:
            print("ur book hasn't been returned")



book1=book('me','harry potter')
book2=book('me1','lord of the rings 1')
book3=book('me2','lorad of da rings fake version')

book1.borrow()
book2.borrow()
book3.borrow()