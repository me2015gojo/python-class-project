# n = int(input('enter the value of terms:'))
# sum=0
# i=1
# while i<=n:
#     sum=sum+i
#     i=i+1
# print('\nsum=', sum)

# i=0
# while i<=0: 
#     print("i will run forever")
num= int(input('enter a 3 digit number:'))
sum=0
temp=num
while temp>0:
    digit=temp%10
    sum+=digit**3
    temp//=10
if num == sum:
    print(num,'num is an amrmstrong number')
else:
    print(num,('num is not a armstrong number'))