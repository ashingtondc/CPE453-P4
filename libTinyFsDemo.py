from libTinyFS import *


if __name__ == "__main__":
    fs = tinyFS()
    fs.tfs_mkfs()
    fs.tfs_mount(DEFAULT_DISK_NAME)
    fs.tfs_open("hello.txt")
    print(fs)