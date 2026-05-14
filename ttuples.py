# def pallind(r):
#     e= len(r) -1
#     s=0
#     while(s<e):
#         if(r[s]!=r[e]):
#             return False
#         s+=1
#         e-=1
#     return True
# r=(1,2,3,4,5,7)
# if(pallind(r)):
#     print("the tuples is a Flip-Flop")
# else:
#     print("the tuple is not a flip-flop")

#Write a program to perform the following operations: 1. Create a tuple with different datatypes 2. Create another tuple of integers 3. Create a new tuple by adding 9 to the previous tuple 4. Count the occurrences of an element in the tuple 5. Perform slicing on the tuple

tuplex=("tuple",False,3,2,1)
print(tuplex)
tuplex = (3,6,32,34,3,3,3,3,43,4,3,4,34,34,34,3)
print(tuplex.count(6))
_slice=tuplex[8:15]
print(_slice)