# empty_list=[]
# print()
# numbers= [1,2,3,4,5]
# print(numbers)
# triples= [1,2,3]*3
# print(triples)
# aList=[100,200,300,400,500]
# aList= aList[::-1]
# print(aList,"\n")

# def match_word(words):
#     ctr=0
#     lst=[]
#     for word in words:
#         if len (word)> 1 and word[0] == word[-1]:
#             ctr += 1
#             lst.append(word)
#     print('list of words with the first letter and last character same \n', lst)
#     return ctr
# count=match_word(['abc','cfc','bbc','bcb','msn','fghf','71011'])
# print('number of words having first and last character same:',count)

num=[7,10,11]
print(max(num))
sum=0
for i in num:
    sum+=i
print(sum)
avg=sum/len(num)
print(avg)
