'''
#Python

print("Hello World")

#Variable

age = 20
print(age)

price = 19.95
print(price)

firstName = "AcEr"
is_inline = False  # boolean-python is  a case sensitive


print ("Check In")
print("Data=")
first_name = "John Smith"
age = 20
new_patient = True
print("Name:",first_name)
print("Age:",age,"Years Old")
print("New Patient?", new_patient)


#input

name = input("What is your name?")
print("Hello"+name)


#Type conversion - {int(),float(),bool(),str()}

birth_year = input("Enter your Birth year: ") # value as string is returned
my_age = 2025 - int(birth_year)
print(my_age)

# Basic Calculator

First_Num = input("Enter your First Number: ")
Second_Num = input("Enter your Second Number: ")

Sum =float(First_Num)+float(Second_Num)
print("Sum: " +Sum)
'''

#String

course = 'Python for Beginners'  # String objects
print(course.upper())           # method returns a  new string
print(course.find('for'))
print(course.replace('for','4')) #immutable
print('Python' in course)


#Arithmatic Operation

print(10 + 3)
print(10//3)
print(10**3)

# Augmented Assignment variable

x = 10
x = x+10
x += 10
print(x)

y = 10 + 3 * 2
print(y)

# Comparison Operator

q = 3 > 2
p = 3 == 2
print(q,p)

price = 25
print(price > 10 or price < 30)



#IF THEN ELSE

TEMP = 23

if TEMP> 30:
   print("It's a hot day")
   print("Drink Plenty of Water")
elif TEMP > 20:
    print("It's a nice day")
elif TEMP > 10:
    print("It's a bit cold")

#Exercise
'''
weight = float(input("Weight: "))  # Convert input to float
unit = input("(K)g or (L)bs: ")

if unit.upper() == "K":
    converted = weight / 0.45
    print("Weight in Lbs: ", converted)
elif unit.upper() == "L":
    converted = weight * 0.45
    print("Weight in Kgs: ", converted)
else:
    print("Invalid unit. Please enter 'K' or 'L'.") 
  
'''

# WHILE

i = 1
while i <= 5:
 print(i)
 i = i + 1

i = 1
while i <= 5:
 print(i* '*')
 i = i + 1


#Lists

names = ["John" , "Bob","Mosh","Sam","Mary"]
print(names)
print(names[0])
print(names[-1])
print(names[0:3])


#List Methods
'''
numbers = [1,2,3,4,5]

print(numbers)
print(1 in numbers)
print(len(numbers))
for item in numbers:
    print(item)

i=0
while i <= len(numbers):
    print(numbers[i])
    i = i + 1
numbers.clear()
'''

#range function

numbersRange = range(5,10,2)
for number in numbersRange:
    print(number)


