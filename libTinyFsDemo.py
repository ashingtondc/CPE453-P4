from libTinyFS import *


if __name__ == "__main__":
    fs = tinyFS()
    fs.tfs_mkfs()
    fs.tfs_mount(DEFAULT_DISK_NAME)
    fd = fs.tfs_open("hello.txt")
    print(f"FD: {fd}")
    fs.tfs_open("hello.txt") # testing opening the same file
    print(fs)