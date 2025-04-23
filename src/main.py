from textnode import TextNode, TextType
from os import path, listdir, mkdir
from shutil import copy, rmtree

def copy_files_recursively(source_dir, destination_dir):
    if not path.exists(source_dir):
        raise FileNotFoundError(f"Source directory {source_dir} does not exist")
    if not path.exists(destination_dir):
        mkdir(destination_dir)
    else:
        rmtree(destination_dir)

    def recursive_copy(source, destination):
        if path.isfile(source):
            print(f"Copying file: {source} -> {destination}")
            copy(source, destination)
        else:
            if not path.exists(destination):
                mkdir(destination)
            entries = listdir(source)
            for entry in entries:
                recursive_copy(path.join(source, entry), path.join(destination, entry))

    recursive_copy(source_dir, destination_dir)


def main():
    source_dir = "static"
    destination_dir = "public"
    copy_files_recursively(source_dir, destination_dir)


main()

