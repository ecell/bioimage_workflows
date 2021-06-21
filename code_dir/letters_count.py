#!/usr/bin/env python3
import json

letter1="a"
letter2="e"

f = open('sample.txt', 'r')
data = f.read()
f.close()

count_letter1 = data.count(letter1)
count_letter2 = data.count(letter2)
print(count_letter1)
print(count_letter2)
json_str = json.dumps({"letters1_count":count_letter1, "letter2_count":count_letter2})
print(json_str)
