from os.path import exists

BLOCKSIZE = 256

def openDisk(filename, nBytes):
    if exists(filename) and nBytes == 0:
        f = open(filename, "r+b")
        return f
    
    f = open(filename, "w+b")
    # Write nBytes of 0
    for i in range(nBytes):
        byte = b"0"
        f.write(byte)
    f.seek(0)
    return f

def readBlock(disk, bNum, buffer):
    disk.seek(bNum*BLOCKSIZE)
    buffer['block'] = disk.read(BLOCKSIZE)
    disk.seek(0)


if __name__ == "__main__":
    f = openDisk("disk", 512)
    buffer = {}
    readBlock(f, 0, buffer)
    print(buffer['block'])
    f.close()
