#!/usr/bin/env python3

import requests

DEFAULT_WORDLIST = "./default_wordlist.txt"

def enumerateDirectories(target, wordlist = DEFAULT_WORDLIST):
    word_array=readWordlist(wordlist)
    for (word in word_array):
        request = requests.get(target + "/" + word)
        if (int) request.status_code >= 200 && request.status_code < 500:
            print(word + " " + request.status_code)

def readWordlist(wordlist=DEFAULT_WORDLIST):
    word_array = []
    file=open(wordlist, "r")
    for line in file:
        word_array.append(line)
    file.close()


