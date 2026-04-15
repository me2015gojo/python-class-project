 #Write a program to create a function name well wishes that will give output hello, how are you!

# def wellwishes():
#     print("hello") 
#     print('how are you')

# wellwishes()

def add(P,Q):
    return P+Q
def subtraction(P,Q):
    return P-Q
def multiply(P,Q):
    return P * Q
def divide(P,Q):
    return P/Q

print('please select the operation')
print(" a. add")
print("b. subtraction")
print("c. multiply")
print("d. divide")
choice=input("please enter your choice:")
num1=int(input("enter the first number:"))
num2=int(input('enter the second number:'))
if choice == "a":
    print(num1, "+" ,num2, "=",add(num1,num2))
elif choice == "b":
    print(num1, "-" ,num2, "=",subtraction(num1,num2))
elif choice == "c":
    print(num1, "*" ,num2, "=",multiply(num1,num2))
elif choice == "d":
    print(num1, "/" ,num2, "=",divide(num1,num2))
else:
    print('this is invalid input')