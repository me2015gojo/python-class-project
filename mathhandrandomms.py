# import math
# print('the floor and the ceiling value of 23.56 are:' + str(math.ceil(23.56))+ str(math.floor(23.56)))

# x= 10
# y= -15
# print('the value of x after copying the sign from y is:: ' + str(math.copysign(x, y)))
# print( 'absolute value of - 96 and 56 are:' + str(math.fabs(-96)) + ',' + str(math.fabs(56)))
# print('the GCD  of 24 and 56:' + str(math.gcd(24, 56)))
# print(math.factorial(5))
# print(math.pow(2,3))
# print(math.fsum([1,2,3,4]))
# print(math.prod([2,6,8]))

import random
playing = True
number = str(random.randint(0,9))
print("i will generate a number from 0 to 9, and you have to guess the number one digit at a time.")
print(' the game ends when you  get 1 hero!!')
while playing:
    guess=input("give me your best guess!  \n")
    print('you win the game ')
    print("the number was",number)
    break
else:
    print("your guess isn't quite right, try again \n")
