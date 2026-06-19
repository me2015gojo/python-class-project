# class myclass:
#     __privateVar = 27
#     def __privmeth(self):
#         print(self)
#         print('im in myclass')
#     def hello(self):
#         print('private variable:',myclass.__privateVar)

# foo= myclass()
# foo.hello()
# foo.hello
# foo.__privmeth








class point:
    def __init__(self,x=0,y=0):
        self.x=x
        self.y=y
        


    def __str__(self):
        return "({0},{1})".format(self.x,self.y)
    
p1=point(2,3)
print