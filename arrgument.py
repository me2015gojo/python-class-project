#Let's create a function total_calc() that helps us calculate and print out the total amount paid at a restaurant. Given a bill amount and the percentage of the bill amount you decide to pay us a tip (tip_perc ), this function calculates the total amount you should pay.


# def total_calc(bill_amount , tip_perc):
#     tip=bill_amount * (tip_perc / 100)
#     total= bill_amount + tip
#     print(f'please play ${total}')
# bill = float(input("enter bill amount:"))
# tip = float(input("enter tip percentage:"))
# total_calc(bill ,tip)

# def cube(number):
#     return number*number*number
# def by_three(number):
#     if number %3 ==0:
#         return cube(number)
#     else:
#         return False
# print(by_three(9))
# print(by_three(3))


def factorial(n):
    if n == 0 or n == 1:
        return 1
    else:
        return n * factorial(n-1)
number = int(input("enter a number:"))
result= factorial(number)
print(f"the factorial of {number} is {result}.")