from importlib.util import MAGIC_NUMBER
from pickle import NONE
import libDisk as ld


MAGIC_NUMBER = 0x5A
SUPERBLOCK = 0x00
ROOT_INODE = 0x01

class tinyFS:

    def __init__(self):
        self.mounted = False
        self.current_fs = None

    # Makes an empty TinyFS file system of size nBytes on the file specified by ‘filename’. 
    # This function should use the emulated disk library to open the specified file, and 
    # upon success, format the file to be mountable. This includes initializing all data 
    # to 0x00, setting magic numbers, initializing and writing the superblock and other 
    # metadata, etc. Must return a specified success/error code.
    def tfs_mkfs(self, filename, nBytes):
        disk = ld.openDisk(filename, nBytes)
        if disk < 0: # error
            return disk # for now, return same error code

        # don't need to initialize data to 0x00 because we're doing it in ld.openDisk
        # TODO: figure out a mechanism to manage free blocks
        superblock = {"block": [MAGIC_NUMBER, ROOT_INODE]}
        ld.writeBlock(disk, SUPERBLOCK, superblock)

        # TODO: figure out inode structure
        root_inode = {"block": None}
        ld.writeBlock(disk, ROOT_INODE, root_inode)

        # anything else that needs to be initialized?

    # tfs_mount(char *filename) “mounts” a TinyFS file system located within ‘filename’. 
    # As part of the mount operation, tfs_mount should verify the file system is the correct
    # type. Only one file system may be mounted at a time.  Must return a specified success/error code.
    def tfs_mount(self, filename):
        pass

    # tfs_unmount(void) “unmounts” the currently mounted file system.
    # Use tfs_unmount to cleanly unmount the currently mounted file system.
    def tfs_unmount(self):
        pass

    # Opens a file for reading and writing on the currently mounted file system. Creates 
    # a dynamic resource table entry for the file (the structure that tracks open files, 
    # the internal file pointer, etc.), and returns a file descriptor (integer) that can 
    # be used to reference this file while the filesystem is mounted.
    def tfs_open(self, name):
        pass
    
    # Closes the file and removes dynamic resource table entry.
    def tfs_close(self, fs):
        pass

    # Writes buffer ‘buffer’ of size ‘size’, which represents an entire file’s contents, 
    # to the file described by ‘FD’. Sets the file pointer to 0 (the start of file) when done. 
    # Returns success/error codes.
    def tfs_write(self, FD, buffer, size):
        pass
    
    # deletes a file and marks its blocks as free on disk.
    def tfs_delete(self, FD):
        pass

    # reads one byte from the file and copies it to ‘buffer’, using the current file pointer 
    # location and incrementing it by one upon success. If the file pointer is already at the 
    # end of the file then tfs_readByte() should return an error and not increment the file pointer.
    def tfs_readByte(FD, buffer):
        pass

    # Change the file pointer location to offset (absolute). Returns success/error codes.
    def tfs_seek(FD, offset):
        pass

