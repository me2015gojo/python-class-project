numbers1=[1,2,3]
numbers2=[4,5,6]
result = map(lambda x,y:x+y,numbers1,numbers2)
print('addition of two lists')
print(list(result))
nums=[1,2,3,4,5]
def sq(n):
    return n*n
square = list(map(sq,nums))
print('square of numbers in list')
print(square)
s1 = {2,3,1}
s2={'b','a','c'}
s3= list(zip(s1,s2))
print(s3,'\n')




list1=[10,20,30,40]
list2 = [100,200,300,400]

for x, y in zip(list1,list2[::-1]):
    print(x,y)

stocks=['reliance', 'infossys','tcs']
prices=[2175,1127,2750]


new_dict = {stocks: prices for stocks,
            prices in zip(stocks,prices)}

print('\n{}'.format(new_dict))

