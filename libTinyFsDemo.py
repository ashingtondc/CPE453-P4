from libTinyFS import *


if __name__ == "__main__":
    print("TinyFS Demo")
    print("\nTesting mkfs, mount, open\n")
    fs = tinyFS()
    fs.tfs_mkfs()
    fs.tfs_mount(DEFAULT_DISK_NAME)
    print("Creating hello")
    fd = fs.tfs_open("hello")
    print(f"FD: {fd}")
    fs.tfs_open("hello") # testing opening the same file
    print(fs)
    print("\nTesting writing and reading\n")
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

    print("\nTesting seek\n")

    # Test seek
    fs.tfs_seek(fd, 250)
    result = []
    while(fs.tfs_readByte(fd, buffer) == 0):
        result.append(chr(buffer['byte']))
    result = "".join(result)
    print(len(result))
    print(result)

    print("\nClosing and reopening the same file: \n")

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

    print("\nCreating a different file\n")

    fs.tfs_close(fd)
    # Open new file
    fd1 = fs.tfs_open("newfile")
    data = {}
    data['bytes'] = "This is a different file"
    data['bytes'] = bytearray(data['bytes'], 'utf-8')
    fs.tfs_write(fd1, data)
    # Read the new file as well
    result = []
    while(fs.tfs_readByte(fd1, buffer) == 0):
        result.append(chr(buffer['byte']))
    result = "".join(result)
    print(result)

    print("\nOpening hello to delete it\n")
    fd = fs.tfs_open("hello")
    print(fs.free_block_table)
    fs.tfs_delete(fd)
    print(fs.free_block_table)
    # Unmount
    print("\nTesting unmount\n")
    fs.tfs_unmount()




