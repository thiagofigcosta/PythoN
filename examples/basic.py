#!/bin/python3

import math
import sys
import basic_external_file as ext

print('This is Pytho{\}')
print('')
print('Running over Python {}.{}.{}'.format(sys.version_info[0],sys.version_info[1],sys.version_info[2]))
print('Several  tabs            here')
print('Is 13 greater than 14?')

if 13 > 14{ # comments after curly brackets
    print('Unfortunately not')
} else {  # fixed else if whitespace
    print('NEVER')
}
print('')
print('10 reasons why you should use Pytho{\}')
for i in range(10){
print ("{} Because I rate : and tab".format(i)) # no ident here
}

empty_dictionary = {}
single_line_dictionary={"do we support dictionaries?":"Yes, we do support dictionaries"}
multi_line_dictionary={
    "Pytho{\}":"Rocks"
}

print()

print(single_line_dictionary['do we support dictionaries?'])

for key,value in multi_line_dictionary.items(){
    print(key,value)
}

ext.print_ext_file()

dict_arr=[]
dict_arr.append({'dictionaries':'appended inline to array are now supported'})
dict_arr.append({'help us to improve':'send issues'})
dict_arr.append({'Workaround Oriented Programming':'for the win'})
print()
for dictionary in dict_arr{
    for k,v in dictionary.items(){
        print('{} {}'.format(k,v))
    }
}