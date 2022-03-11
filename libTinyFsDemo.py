from libTinyFS import *


if __name__ == "__main__":
    fs = tinyFS()
    fs.tfs_mkfs()
    fs.tfs_mount(DEFAULT_DISK_NAME)
    print("Creating hello")
    fd = fs.tfs_open("hello")
    print(f"FD: {fd}")
    fs.tfs_open("hello") # testing opening the same file
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

    print(fs.free_fds)


    # Test closing and reopening file
    fs.tfs_close(fd)
    print("Reopening hello")
    fd = fs.tfs_open("hello")
    print(f"FD: {fd}")
    result = []
    # Test write/read
    fs.tfs_seek(fd, 0)
    while(fs.tfs_readByte(fd, buffer) == 0):
        result.append(chr(buffer['byte']))
    result = "".join(result)
    print(result)
    fs.tfs_delete(fd)


    # fs.tfs_close(fd)




