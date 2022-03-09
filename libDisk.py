from os.path import exists

BLOCKSIZE = 256
DEFAULT_DISK_SIZE = 10240
DEFAULT_DISK_NAME = "tinyFSDisk"

def openDisk(filename, nBytes=0):
    try:
        if exists(filename) and nBytes == 0:
            f = open(filename, "r+b")
            return f
        
        f = open(filename, "w+b")
        # Write nBytes of 0
        init = bytes(nBytes)
        f.write(init)
    except:
        return -1
    return f

def readBlock(disk, bNum, buffer):
    try:
        disk.seek(bNum*BLOCKSIZE)
        buffer['block'] = disk.read(BLOCKSIZE)
        disk.seek(0)
    except:
        return -1
    return 0

def writeBlock(disk, bNum, buffer):
    try:
        disk.seek(bNum*BLOCKSIZE)
        data = bytearray(buffer['block'])
        # Only write BLOCKSIZE bytes to the disk
        if len(data) <= BLOCKSIZE:
            disk.write(data)
        else:
            disk.write(data[:BLOCKSIZE])
        disk.seek(0)
    except:
        return -1
    return 0

def closeDisk(disk):
    try:
        disk.close()
    except:
        return -1
    return 0
