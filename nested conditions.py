# Write a program to check whether the student can take an exam or not. Students will be allowed only in two conditions: If they have a medical cause (‘Y’ for yes and ‘N’ for no). If yes, then they will be allowed. If No, then check attendance If attendance is above 75, then allowed; otherwise, not allowed.


# medical_cause=(input('do you have a medical clause?(Y/N):'))
# if medical_cause=='Y':
#     print('you are admitted to the exam')
# else:
#     Attendence=int(input('enter your attendance details:'))
#     if Attendence>75:
#         print('you are admitted to the exam')
#     else: 
#         print('you have been disqualified from the exam')

# Write a program to calculate the electricity bill. The bill is calculated by checking the number of units consumed. Suppose the user is consuming less than 50 units. The per-unit cost will be 2.60, and the tax on that bill will be 25. If a user is consuming more than 50 but less than 100. Then the per-unit cost will be 3.25, and the tax on that bill will be 35 If the user is coming more than 100 and less than 200. Then the per-unit cost will be 5.26, and the tax will be 45 And above 200, the cost of the unit is 8.45, and the tax is 75.

units=int(input('enter the number of units consumed:'))

if units<50:
    amount=units*2.60
    tax=25
elif units<=100:
    amount=(50*2.60)+(units-50)*3.25
    tax=35
elif units<=200:
    amount=(50*2.60)+(50*3.25)+(units-100)*5.26
    tax=45
else:
    amount=(50*2.60)+(50*3.25)+(100*5.26)+(units-200)*8.45
    tax=75

total_bill=amount+tax
print('the total bill is:', round (total_bill,2))
