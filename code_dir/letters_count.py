#!/usr/bin/env python3
import json


# https://docs.python.org/ja/3/library/typing.html
# 引数が
def count_letters(filename :str, letter1 :str, letter2 :str) -> str:
    f = open(filename, 'r')
    data = f.read()
    f.close()

    count_letter1 = data.count(letter1)
    count_letter2 = data.count(letter2)

    json_str = json.dumps({"letters1_count":count_letter1, "letter2_count":count_letter2})

    # f = open(outputfilename, 'w')
    # data = f.write(json_str)
    # f.close()

    # https://docs.python.org/ja/3/library/typing.html
    # TODO: ディレクトリを返す
    return json_str

#json_str = analyze_sample("sample.txt", letter1, letter2)
#print(json_str)
