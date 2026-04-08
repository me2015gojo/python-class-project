# Write a program to demonstrate a right angle triangle pattern?

# print("half pyramid pattern of starts(* ): ")
# n = int(input("enter the number of rows"))
# for i in range(n):
#     for j in range(i+1):
#         print("*", end="" )
#     print()




#reverse order
# print("half pyramid pattern of starts(* ): ")
# n = int(input("enter the number of rows"))
# for i in range(n,0,-1):
#     for j in range(i):
#         print("*", end="" )
#     print()

#floyyd triangle
# num=1
# n = int(input("enter the number of rows:"))
# for i in range(0,n):
#     for j in range(i+1):
#         print(num, end=" " )
#         num=num+1
#     print()

rowsize = int(input("enter the number of rows:"))
if rowsize%2==0:
    halfdiamrow= int(rowsize/2)
else:
    halfdiamrow = int(rowsize/2)+1
space=halfdiamrow-1
for i in range(1,halfdiamrow+1):
    for j in range(1, space+1):
        print(end=" ")
        