# import turtle 
# turtle.Screen().bgcolor("orange")
# turtle.Screen().setup(300,400)
# polygon=turtle.Turtle()

# num_sides= int(input("enter number of sides:")) 
# side_length= int(input("enter the length:"))
# angle = 360.0 / num_sides
# for i in range(num_sides):
#     polygon.forward(side_length)
#     polygon.right(angle)
# turtle.done()

import turtle 
turtle.Screen().bgcolor("orange")
turtle.Screen().setup(300,400)
t=turtle.Turtle()

num_sides= 3
side_length= 100
angle = 360.0 / num_sides
t.width(3)
t.pencolor("sky blue")
for i in range(num_sides):
    t.forward(side_length)
    t.right(angle)
t.penup()
t.goto(0,-50)
t.pendown()
for i in range(num_sides):
     t.forward(side_length)
     t.left(angle)
turtle.done()
