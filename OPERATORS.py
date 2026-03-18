#there are five trees in Jack's front yard. He checks each tree to find out how tall it is in inches and writes the height on a sheet of paper. Jack's list: 98, 94, 41, 96, and 11. What is the average height of a tree in Jack's front yard?

# tree1=98
# tree2=94
# tree3=41
# tree4=96
# tree5=11

# sum=(tree1+tree2+tree3+tree4+tree5)
# avg=sum/5
# print('the average hight of a tree is ',avg)

#Write a program to calculate the number of notes in the given amount?

#4620

amt=int(input('enter the amount:'))
note500=amt//500
amt= amt % 500

note200=amt//200
amt= amt % 200

note100=amt//100
amt= amt % 100

note50=amt//50
amt= amt % 50

note20=amt// 20
amt= amt % 20

note10=amt//10

print('notes of 500:',note500)
print('notes of 200:',note200)
print('notes of 100:',note100)
print('notes of 50:',note50)
print('notes of 20:',note20)
print('notes of 10:',note10)
