#!/usr/bin/env python3

import requests

DEFAULT_WORDLIST = "./default_wordlist.txt"

def enumerateDirectories(target, wordlist = DEFAULT_WORDLIST):
    word_array=readWordlist(wordlist)
    discovered_directories=[];
    for (word in word_array):
        request = requests.get(target + "/" + word)
        if (int) request.status_code >= 200 && request.status_code < 400:
            print(word + " " + request.status_code)
            discovered_directories.append(word)
    return discovered_directories

def readWordlist(wordlist=DEFAULT_WORDLIST):
    word_array = []
    file=open(wordlist, "r")
    for line in file:
	if line[0] != "#" and len(line) >= 1:
            word_array.append(line)
    file.close()
    return word_array


