# class vehicle:
#     def __init__(self,name,max_speed,mileage):
#         self.name = name
#         self.max_speed=max_speed
#         self.mileage=mileage
# class bus(vehicle):
#         pass
# school_bus=bus('school volvo',180,12)
# print('vehicle:',school_bus.name,'speed:',school_bus.max_speed,'mileage:',school_bus.mileage)

class person:
    def __init__(self,name,idnumber):
        self.name=name
        self.idnumber=idnumber
    def display(self):
        print('name:',self.name,'\n id number:',self.idnumber)
class employee(person):
    def __init__(self,name,idnumber, salary,post):
        self.salary=salary
        self.post=post
        person.__init__(self,name,idnumber)
achil=employee=employee('rahuul david',300000,23,23)
achil.display()