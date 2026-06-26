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
            print("insuffisient balance")
    def check_balance(self):
        print(f'balance:{self.balance}')
atm=BANKATM(1000000000000000000000000000000000000000)
atm.check_balance()
atm.withdraw(3000)
atm.check_balance()

