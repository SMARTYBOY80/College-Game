

import csv

level = 'levelOne.csv'
array = []

with open(level , mode ='r') as file:    
       csvFile = csv.reader(file)
       for lines in file.readlines():
            lines = lines.strip('\n')
            lines = lines.split('\t')
            
            array.append(lines)

for counter in range(len(array)):
    for index in range(len(array[counter])):
        if array[counter][index] == '0':
            print('Air ', end='')
        elif array[counter][index] == '1':
             print('Ground ', end='')
        elif array[counter][index] == '2':
            print('Block ', end='')
    print('\n')