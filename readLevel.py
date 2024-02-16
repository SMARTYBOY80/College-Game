

import csv


def getLevel(level, block_size, HEIGHT, WIDTH, Block):
    array = []
    floor = []
    with open(level , mode ='r') as file:    
        csvFile = csv.reader(file)
        for lines in file.readlines():
                lines = lines.strip('\n')
                lines = lines.split('\t')
                
                array.append(lines)

    for counter in range(len(array)):
        for index in range(len(array[counter])):
            if array[counter][index] == '0':
                print('Empty ', end='')
            elif array[counter][index] == '1':
                floor.append([Block(block_size, HEIGHT - block_size, block_size)
                              (-WIDTH // block_size, (WIDTH * 2) // block_size)])
            elif array[counter][index] == '2':
                print('Block ', end='')
        print('\n')
    return floor