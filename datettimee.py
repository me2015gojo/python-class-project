# from datetime import date, time, datetime
# today=date.today()
# now = datetime.now()
# print("today's date is",today)
# print('\nCurrent Date and time is', now)

# print('\nDate components',today.year, today.month , today.day)


# import calendar
# year= int(input("enter the year:"))
# month = int(input("enter the month:"))
# calendar.setfirstweekday(calendar.SUNDAY)
# print(calendar.month(year, month))
# import calendar
# print('the calendar year of',year,'is:')
# print(calendar.calendar(year))

def hotel_cost(nights):
    return 140*nights
def plane_ride_cost(city):
   if 'jaipur' == city:
       return 183
   elif "tokyo":
       return 220
   elif "disneyland":
       return 222
   elif "new york" == city:
       return 475
   
def rental_car_cost(days):
    if days>=7:
        return 40*days - 50
    elif days>=3:
        return 40*days - 50
    else:
        return 40*days
    
def trip_cost(city,days, spending_money ):
    return rental_car_cost(days)+hotel_cost(days)+plane_ride_cost(city)+spending_money

print(":cost of rental car:",rental_car_cost(5))
print(":cost of plane ride:",plane_ride_cost("new york"))
print(":cost of hotel room:",hotel_cost(7))
print(": total cost of trip:",trip_cost("new york",7,500))
print(trip_cost("tokyo",7,000))
