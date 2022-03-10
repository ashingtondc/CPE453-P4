from importlib.util import MAGIC_NUMBER

# from numpy import block
from libDisk import BLOCKSIZE
import libDisk as ld
from array import *


MAGIC_NUMBER = 0x5A
SUPERBLOCK = 0x00
ROOT_INODE = 0x01
DEFAULT_DISK_SIZE = 10240
DEFAULT_DISK_NAME = "tinyFSDisk"

class tinyFS:

    def __init__(self):
        self.mounted = False
        self.current_fs = ""
        self.current_disk = None
        
        """
        FREE BLOCK TABLE
        An array tracking whether a specific block is free or not. 
        The array is 0 indexed and the free blocks start at BLOCK #2 because the 
        superblock and root inode take up the first 2 blocks, 0 and 1 respectively. 
        To see if a block is free, access the following way:
        self.free_block_table[block_index - 2]
        For example, to check if block 2, the first open block, is free we do:
        self.free_block_table[2 - 2] -> self.free_block_table[0]

        This table is loaded upon mounting a disk. It is adjusted here for all disk operations.
        It is written back to the disk upon unmounting. 
        """
        self.free_block_table = None

        """
        ROOT INODE STRUCTURE
        First byte is the number of files in the directory
        Filename/inode pairs are stored as follows:
        9 bytes: 
        first byte is the block # of the inode
        next 8 bytes contain the filename: up to 8 characters
        This information is loaded into a self.file_table upon mounting.
        The Python dict is referenced and updated while the fs is mounted
        When unmounting, the Python dict is translated into the specified format
        and the block is written to the disk
        """
        self.file_table = None

    def __str__(self):
        return f"\
            Mounted: {self.current_fs}\n\
            Open Blocks: {len(self.free_block_table)}\n\
            Block table:\n\
            {self.free_block_table}\n\
            File table:\n\
            {self.file_table}"

    
    # Makes an empty TinyFS file system of size nBytes on the file specified by ‘filename’. 
    # This function should use the emulated disk library to open the specified file, and 
    # upon success, format the file to be mountable. This includes initializing all data 
    # to 0x00, setting magic numbers, initializing and writing the superblock and other 
    # metadata, etc. Must return a specified success/error code.
    def tfs_mkfs(self, filename=DEFAULT_DISK_NAME, nBytes=DEFAULT_DISK_SIZE):
        disk = ld.openDisk(filename, nBytes)
        """ if disk < 0: # error
            return disk # for now, return same error code """

        # don't need to initialize data to 0x00 because we're doing it in ld.openDisk
        
        
        # num of total blocks minus superblock and root inode
        num_free_blocks = int(nBytes/BLOCKSIZE - 2)

        # Store array of unsigned ints, each one 2 bytes. 
        # Index+2 corresponds to block number. Tracks whether or not the block is free. 
        free_bytes = BLOCKSIZE - 3 # number of remaining bytes in the superblock
        max_free_blocks = free_bytes # 1 byte to track each block
        if num_free_blocks <= max_free_blocks:
            free_block_table = [0]*num_free_blocks
        else:
            # Cannot support this disk size. Superblock does not have enough
            # space to track free blocks
            return -2
        
        
        # 1st byte of superblock is magic number
        # 2nd byte of superblock is root inode block number
        # 3rd byte of superblock is number of free blocks at disk creation
        # remaining bytes are a table tracking the free blocks

        # 1 byte max is 255. num_free_blocks will always be less than 255. 
        superblock_data = [MAGIC_NUMBER, ROOT_INODE, num_free_blocks] + free_block_table
        superblock = {"block": array('B', superblock_data)}
        ld.writeBlock(disk, SUPERBLOCK, superblock)



        # TODO: figure out inode structure
        # hold pairs: <filename>:<block # for corresponding inode>
        # first byte indicates number of files. initialize to 0
        root_inode = {"block": 0}
        ld.writeBlock(disk, ROOT_INODE, root_inode)

        # anything else that needs to be initialized?
        return disk

    # tfs_mount(char *filename) “mounts” a TinyFS file system located within ‘filename’. 
    # As part of the mount operation, tfs_mount should verify the file system is the correct
    # type. Only one file system may be mounted at a time.  Must return a specified success/error code.
    def tfs_mount(self, filename):
        disk = ld.openDisk(filename)
        """
        if disk < 0: # error
            return disk # for now, return same error code
        """
        

        # Superblock
        superblock = {}
        ld.readBlock(disk, SUPERBLOCK, superblock)
        superblock_data = bytearray(superblock['block'])
        # Verify filesystem type
        if superblock_data[0] != MAGIC_NUMBER:
            # Incorrect filesystem type. Exit.
            return -3
        num_free_blocks = superblock_data[2]
        free_block_table = superblock_data[3:num_free_blocks + 3]
        self.free_block_table = array('B', free_block_table)

        # Root inode
        file_table = {}
        root_inode = {}
        ld.readBlock(disk, ROOT_INODE, root_inode)
        root_inode_data = bytearray(root_inode['block'])
        num_files = root_inode_data[0]
        # Translate each filename/block pair
        for i in range(num_files):
            # Sliding window of 9 bytes since each pair is stored in 9 bytes
            start = 9*i + 1
            end = start + 9
            pair = root_inode_data[start:end]
            # first byte of each 9 byte sequence is the block number of the inode
            inode_block_num = pair[0]
            # build the name string from the remaining bytes
            inode_name = []
            for j in range(1, 9):
                # look for null terminator
                if pair[j] == 0:
                    break
                inode_name.append(str(pair[j]))
            inode_name = "".join(inode_name)
            file_table[inode_name] = inode_block_num

        self.file_table = file_table

        self.mounted = True
        self.current_disk = disk
        self.current_fs = filename

        return 0


    # tfs_unmount(void) “unmounts” the currently mounted file system.
    # Use tfs_unmount to cleanly unmount the currently mounted file system.
    # Write updated superblock back to disk
    # Write updated root inode back to disk
    def tfs_unmount(self):
        pass

    # Opens a file for reading and writing on the currently mounted file system. Creates 
    # a dynamic resource table entry for the file (the structure that tracks open files, 
    # the internal file pointer, etc.), and returns a file descriptor (integer) that can 
    # be used to reference this file while the filesystem is mounted.
    def tfs_open(self, name):
        if name not in self.file_table:
            # Find open block
            block_num = self.allocate(1)
            if block_num is None: 
                # No free blocks.
                return -4
            block_num = block_num[0]

            self.free_block_table[block_num - 2] = 1

            # Update the file table
            self.file_table[name] = block_num

            # Create the inode
            # TODO: write the code to build inode
            """
            Do we actually need to do anything here? With no idea of what's in the file
            yet, I think we can just reserve a block and fill in the inode later
            """
            # first 4 bytes of inode: size of file
            # Remaining bytes: Contiguous block numbers for data (written in the order they should be accessed)
        inode_num = self.file_table[name]
        # TODO: Complete this part
        """
        Since we can't return a real file descriptor, maybe create a class for it
        """
    
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

    # Allocate a certain number of free blocks.
    # Returns an array of the free block numbers, or None if not enough were found.
    def allocate(self, num_blocks):
        i = 0
        blocks = []
        while i < len(self.free_block_table) and len(blocks) < num_blocks:
            if self.free_block_table[i] == 0:
                blocks.append(i + 2)
        if len(blocks) == num_blocks:
            return blocks
        return None

    # free a data block
    def free(self, block_nums):
        for block in block_nums:
            self.free_block_table[block - 2] = 0


    class inode:

        def __init__(self):
            self.size = 0
            # for now, just direct blocks. might change later
            self.direct_blocks = []

        def encode(self):
            return bytearray([self.size] + self.direct_blocks)
