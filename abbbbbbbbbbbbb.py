from abc import ABC, abstractmethod

class ATM(ABC):
    @abstractmethod
    def withdraw(self,amount):
        pass
    @abstractmethod
    def check_balance(self):
        pass
class BANKATM(ATM):
    def __init__(self,balance):
        self.balance=balance

    def  withdraw(self,amount):
        if amount<= self.balance:
            self.balance-=amount
            print(f"withdrawn:{amount}")
        else:
            print("insuffeisient balance")
atm=BANKATM(100000)
atm.check_balance()
atm.withdraw(3000)
atm.check_balance()

