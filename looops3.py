# Write a program to check how many times a character is repeated in a word?

# string=input('please enter your own word:')
# char=input('please enter your own character:')
# i=0
# count=0
# while(i<len(string)):
#     if(string[i] == char):
#         count=count+1
#     i=i+1
# print('the total number of times',char,' has occured=',count)

# lower=int(input('enter a lower range:'))
# higher=int(input('enter a higher range:'))
# print('prime number between',lower,'and',higher,'are:')
# for num in range(lower,higher+1):
#     if num>1:
#         for i in range(2,num):
#             if (num % i) == 0:
#                 break
#         else:
#             print(num)

num=int(input('enter the number:'))
t=num
numlen=0
while t>0:
    numlen=numlen+1
    t=int(t/10)
if numlen>=4:
    numlen = int(numlen/2)
    chk=0
    while num>0:
        rem= num%10
        if chk==numlen:
            midone= rem
        elif chk==(numlen-1):
            midtwo=rem
        num=int(num/10)
        chk=chk+1
    prod=midone*midtwo
    print('\nproduct of mid digits('+ str (midone)+"*"+str(midtwo)+')= ',prod)
else:
    print('\nit is an invalid number')