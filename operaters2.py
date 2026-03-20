# a = 45
# b = 89
# c = 0

# if a and b and c:
#     print('all the booleans are true')
# else:
#     print('atleast one number is false')

# a= -10
# b = -9
# c= 0

# if a>0 or b>0:
#     print('either of the nums are greater than 0')
# else:
#     print('none of the nums are greater than 0')

# Write a program to calculate the BMI of a person?

weight= float(input('enter weight in kgs:'))
height= float(input('enter height in meters:'))
BMI= weight/(height*height)

print('you BMI is', BMI)

if BMI <= 18.4:
    print('you are underweight') # 34.9 39.9
elif BMI <= 24.9:
    print('you are normal')
elif BMI <= 29.9:
    print('print you are over weight')
elif BMI <= 34.9:
    print(' you are severly over weight')
elif BMI <= 39.9:
    print('you are obese')
else:
    print('you are severly obese')






