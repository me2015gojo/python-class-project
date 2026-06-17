# class IOString():

#     def __init__(self):
#         self.str1=""
#     def get_string(self):
#         self.str1 = input("enter string:")
#     def print_self(self):
#         print("result is:",self.str1.upper())
# str1 =IOString()
# str1.get_string()
# str1.print_self()'

class Employee:
    def __init__(self):
        print('employee created')
    def __del__(self):
        print("destructor called")
def create_obj():
    print('making object...')
    obj=Employee()
    print('function end....')
    return obj
print("calling create_obj() function...")
obj = create_obj()
print("programme end")