# try:
#     number = int(input("enter a number:"))
#     print("the number entered is", number)
# except ValueError as ex:
#     print("exception:", ex)

#multiple exceptions

# try:
#     num1,num2= eval(input("enter two numbers, seperated by the comma:"))
#     result=num1/num2
#     print("result is",result)
# except ZeroDivisionError:
#     print("division by Zero")
# except SyntaxError:
#     print("Comma is missing. enter numbers seperated by comma like this 1,2")
# except:
#     print("wrong input")
# else:
#     print("no exceptions")
# finally:
#     print("This will execute no matter what ")

valid=False
while not valid:
    try:
        n=int(input("enter a number:"))
        while n%2==0:
            print("bye")
        valid=True
    except ValueError:
        print("Invalid")
