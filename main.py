#!/usr/bin/env python3

import requests
import subprocess
import threading

DEFAULT_WORDLIST = "./default_wordlist.txt"


def main() -> None:
    shell_interact()


# Search for visible directories using brute force HTTP requests
def enumerate_directories_by_request(target, wordlist=DEFAULT_WORDLIST) -> list[str]:
    word_array = read_wordlist(wordlist)
    discovered_directories = []
    target = clean_target(target)
    for word in word_array:
        request = requests.get(target + word)
        if 200 <= int(request.status_code) < 400:
            print(word + " " + str(request.status_code))
            discovered_directories.append(word)
    return discovered_directories


# Helper method used for formatting URLs so that request can be sent
def clean_target(target) -> str:
    top_level_domains = ["com", "org", "gov", "edu", "net", "int", "it", "tv", "mil", "co", "uk", "aws"]
    if len(target.split("://")) < 2:
        target = "https://" + target  # make sure that a protocol is declared
    if target.split(".")[-1].replace("/", "") not in top_level_domains:
        target = cut_path(target)
        # trim the resource path if it exists
    if target[-1] != "/":
        target = target + "/"  # make sure the target URL ends with / so that requests can be made
    return target


# trim down URL so that requests are sent to the present working directory of the requested resource
# ex. if you input https://github.com/willisman31 the output would be https://github.com/
# ex2. if you input https://github.com/willisman31/Vuln-Uploader the output would be https://github.com/willisman31/
def cut_path(target) -> str:
    val = target[8:].rfind("/")
    return target[:val+8]


# trims down URL so requests are only sent to domain's base directory
# ex. if you input https://github.com/willisman31/Vuln-Uploader the output would be https://github.com/
def cut_full_path(target) -> str:
    val = target[8:].find("/")
    return target[:val+8]


# Return all possible directory levels to enumerate (this method needs the protocol specified at the beginning of the
# URL, ex. https://)
def trim_path(target) -> list[str]:
    temp = target[target.find("://")+3:].split("/")
    paths = [target.split("://")[0] + ":/"]
    position = 0
    for item in temp:
        paths.append(paths[position] + "/" + item + "/")
        position += 1
    return paths[1:-1]


# search for possible directories using html source code
def enumerate_directories_with_source_code(target) -> list[str]:
    response = requests.get(target)
    source_code = response.text
    discovered_directories = search_for_absolute_path(target, source_code) + search_for_relative_path(source_code)
    return discovered_directories


# Recursively enumerate source code for directory paths; this definitely needs to be refactored heavily
def deeply_enumerate_directories_with_source_code(target, directories=None, full_enum=None) -> set[str]:
    response = requests.get(target)
    source_code = response.text
    directories += search_for_absolute_path(target, source_code) + search_for_relative_path(source_code)
    for element in directories:
        full_enum.add(element)
    directories = directories.pop()
    if len(directories) > 0:
        deeply_enumerate_directories_with_source_code(target + directories[0], directories, full_enum)
    return full_enum


# search for a full address including domain
def search_for_absolute_path(target, raw_source_code) -> list[str]:
    split_source_code = raw_source_code.split('"')
    discovered_directories = []
    for item in split_source_code:
        if target in item:
            discovered_directories.append(item)
    return discovered_directories


def search_for_relative_path(raw_source_code) -> list[str]:
    split_source_code = raw_source_code.split('"')
    discovered_directories = []
    for item in split_source_code:
        if "./" in item or "../" in item:
            discovered_directories.append(item)
    return discovered_directories


def read_wordlist(wordlist=DEFAULT_WORDLIST) -> list[str]:
    word_array = []
    file = open(wordlist, "r")
    for line in file:
        if line[0] != "#" and len(line) >= 1:
            word_array.append(line)
    file.close()
    return word_array


# return information about server that is included in HTTP response; returns nothing if no server field in response
# header
def scan_header(target) -> str:
    request = requests.get(target)
    head = request.headers
    return head['server']


# send commands to shell
def shell_interact() -> None:
    p = subprocess.Popen(["bash"], stderr=subprocess.PIPE, shell=False, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    stop = False
    
    def read_stdout():
        while not stop:
            msg = p.stdout.readline()
            print("stdout: ", msg.decode())

    def read_stderro():
        while not stop:
            msg = p.stderr.readline()
            print("stderr: ", msg.decode())

    threading.Thread(target=read_stdout).start()
    threading.Thread(target=read_stderro).start()
    while not stop:
        res = input(">")
        p.stdin.write((res + '\n').encode())
        p.stdin.flush()


if __name__ == "__main__":
    main()
