##Write a program to create a class with the name Student and perform the following tasks - 1. Declare a variable grade 2. Print a sentence inside the class 3. Create an object of class student and see the output

# class student:
#     grade=12
#     print('hi my name is johnny b from class 12')

# ob=student()

# class vehicle:
#     def __init__(self,max_speed,mileage):
#         self.max_speed = max_speed
#         self.mileage= mileage

# modelX=vehicle(240,18)
# print("model max speed:",modelX.max_speed)
# print("model mileage:",modelX.mileage)

class parrot:
    species='birds'
    def __init__(self,name,age):
        self.name=name
        self.age=age
parrotobi=parrot('johhny boy',98)
print('i have a parrot called',parrotobi.name,'and he is',parrotobi.age,'years old')
print('it  also belongs to the',parrotobi.species,'species')