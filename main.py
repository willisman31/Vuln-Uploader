#!/usr/bin/env python3

import requests, sys

DEFAULT_WORDLIST = "./default_wordlist.txt"

def main() -> None:
    pass

def enumerateDirectoriesByRequest(target, wordlist = DEFAULT_WORDLIST) -> list[str]:
    word_array=readWordlist(wordlist)
    discovered_directories=[];
    for word in word_array:
        request = requests.get(target + "/" + word)
        if int(request.status_code) >= 200 and int(request.status_code) < 400:
            print(word + " " + request.status_code)
            discovered_directories.append(word)
    return discovered_directories

def cleanTarget(target) -> str:
    if len(target.split("://")) < 2:
        target = "https://" + target
    if target[-1] == "/":
        target = target[:-1]
    return target

def enumerateDirectoriesWithSourceCode(target) -> list[str]:
    response = requests.get(target)
    source_code = response.text
    discovered_directories= searchForAbsolutePath(target, source_code) + searchForRelativePath(source_code)
    return discovered_directories

def searchForAbsolutePath(target, raw_source_code) -> list[str]:
    split_source_code = raw_source_code.split('"')
    discovered_directories=[]
    for item in split_source_code:
        if target in item:
            discovered_directories.append(item)
    return discovered_directories

def searchForRelativePath(raw_source_code) -> list[str]:
    split_source_code = raw_source_code.split('"')
    discovered_directories=[]
    for item in split_source_code:
        if "./" in item or "../" in item:
            discovered_directories.append(item)
    return discovered_directories

def readWordlist(wordlist=DEFAULT_WORDLIST) -> list[str]:
    word_array = []
    file=open(wordlist, "r")
    for line in file:
        if line[0] != "#" and len(line) >= 1:
            word_array.append(line)
    file.close()
    return word_array

def scanHeader(target) -> str:
    request = requests.get(target)
    head = request.headers
    return head['server']

if __name__=="__main__":
    main()

