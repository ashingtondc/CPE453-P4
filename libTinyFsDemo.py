from libTinyFS import *


if __name__ == "__main__":
    fs = tinyFS()
    fs.tfs_mkfs()
    fs.tfs_mount(DEFAULT_DISK_NAME)
    fd = fs.tfs_open("hello.txt")
    print(f"FD: {fd}")
    fs.tfs_open("hello.txt") # testing opening the same file
    print(fs)
    data = {}
    data['bytes'] = "Record a short video (fewer than 5 minutes) demonstrating your file system (using your demo program described above). All members should discuss some of the design decisions you made, limitations of the system, as well as demonstrating the additional features you implemented."
    data['bytes'] = bytearray(data['bytes'], 'utf-8')

    print(len(data['bytes']))
    fs.tfs_write(fd, data)
    buffer = {}
    result = []
    # Test write/read
    while(fs.tfs_readByte(fd, buffer) == 0):
        result.append(chr(buffer['byte']))
    result = "".join(result)
    print(result)

    # Test seek
    fs.tfs_seek(fd, 250)
    result = []
    while(fs.tfs_readByte(fd, buffer) == 0):
        result.append(chr(buffer['byte']))
    result = "".join(result)
    print(len(result))
    print(result)


