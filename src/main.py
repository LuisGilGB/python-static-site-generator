from os import path, listdir, mkdir
from shutil import copy, rmtree
from usecases import generate_page
import sys

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


def generate_pages_recursive(dir_path_content, template_path, dest_dir_path, basepath):
    if not path.exists(dir_path_content):
        print(f"Content directory {dir_path_content} does not exist")
        raise FileNotFoundError("Content directory does not exist")
    entries = listdir(dir_path_content)
    for entry in entries:
        if path.isfile(path.join(dir_path_content, entry)):
            new_name = path.join(dest_dir_path, entry.replace(".md", ".html"))
            generate_page(path.join(dir_path_content, entry), template_path, new_name, basepath)
        else:
            if not path.exists(path.join(dest_dir_path, entry)):
                mkdir(path.join(dest_dir_path, entry))
            generate_pages_recursive(path.join(dir_path_content, entry), template_path, path.join(dest_dir_path, entry), basepath)

def main():
    basepath = sys.argv[1] if len(sys.argv) > 1 else "/"
    source_dir = "static"
    destination_dir = "docs"
    copy_files_recursively(source_dir, destination_dir)
    generate_pages_recursive("content", "template.html", destination_dir, basepath)


main()

