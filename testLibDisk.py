from libDisk import *

if __name__ == "__main__":
    disk = openDisk("testDisk")
    data = {
        "block": b"was a destructive tropical cyclone that affected Jamaica, northeastern Mexico, the Republic of Texas, and the Southeastern United States in September and October 1837, killing an estimated 105 people. It was named after the Royal Navy ship HMS Racer, which encountered the cyclone in the northwestern Caribbean Sea. Matamoros, on the southern bank of the Rio Grande, faced hurricane conditions for several days, with significant damage to"
    }
    # writeBlock(disk, 0, data)
    newData = {}
    readBlock(disk, 0, newData)
    print(newData)
    """
    readBlock(disk, 1, newData)
    print(newData)
    readBlock(disk, 2, newData)
    print(newData)
    """
    closeDisk(disk)
