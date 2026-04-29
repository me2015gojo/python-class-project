# v=int(input('enter a number from one to infinity '))
# for i in range (1,11):
#     print( v, 'x' ,i, '=',v*i )



try:
    marks=int(input("enter the marks between 0 to 100:"))
    if marks <0 or marks>100:
        raise ValueError 
    else:
        print("your marks are",marks)
        if marks<50:
            print("you fail")
        else:
            print('you pass')
    
except ValueError as ie:
    print("Marks out of the range")t
    
    
