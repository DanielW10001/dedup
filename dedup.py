"""Deduplicate files"""

__author__ = "Daniel (danielw10001@gmail.com)"

import argparse
import re
import os
import os.path
import stat
import typing
import hashlib

args = argparse.Namespace()
parser = argparse.ArgumentParser(description="Deduplicate files in the same dir recursively")
parser.add_argument('target', help="Target dir")
parser.add_argument('--no-hidden', action='store_true', help="No hidden dirs or files")
parser.parse_args(namespace=args)

def is_hidden(path: str) -> bool:
    name = os.path.split(path)[1]
    return re.search(r'^[._]', name) or os.stat(path).st_file_attributes & stat.FILE_ATTRIBUTE_HIDDEN

for root, subdirs, filenames in os.walk(args.target):
    hashtopath: typing.Dict[bytes, str] = {}
    for subdir in subdirs:
        subdirpath = os.path.join(root, subdir)
        if args.no_hidden and is_hidden(subdirpath):
            subdirs.remove(subdir)
    for filename in filenames:
        filepath = os.path.join(root, filename)
        if not args.no_hidden or not is_hidden(filepath):
            with open(filepath, mode='rb') as file:
                sha512 = hashlib.sha512(file.read()).hexdigest()
            if sha512 in hashtopath:
                print(f"INFO: Remove {filepath} due to {hashtopath[sha512]}")
                os.remove(filepath)
            else:
                hashtopath[sha512] = filepath
    for hash_str, path in set(hashtopath.items()):
        base, name = os.path.split(path)
        count = 2
        while True:
            try:
                targetname = re.sub(r'^IMG_', '', name)
                targetname = re.sub(r'\s*(?:（已编辑）|\(\d+\)|- 副本)', '', targetname)
                if targetname == name:
                    break
                targetpath = os.path.join(base, targetname)
                os.rename(path, targetpath)
            except OSError:
                name = re.sub(r'(?:_No\d+)?(?P<suffix>\.[^.]+)$', f'_No{count}'+r'\g<suffix>', name)
                count += 1
            else:
                hashtopath[hash_str] = targetpath
                print(f"INFO: Rename {path} to {targetpath}")
                break
