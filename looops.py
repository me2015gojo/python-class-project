# #Write a program to calculate the sum of whole numbers.
# n=int(input('enter a number:'))
# sum=0
# for i in range(1,n+1):
#     sum=sum+i
# print('\nSum=',sum)

#Write a program to reverse the string entered by the user.
# string=input('pls enter your own string;')
# string2=('')
# for i in string:
#     string2=i+string2
# print('\nTh eoriginal String=',string)
# print('\the reversed string=', string2)

n=int(input('enter the value of n:'))
print('numbers {0} to {1} are:'. format(n,1))
for i in range(n,0,-1):
    print(i)