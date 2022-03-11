from importlib.util import MAGIC_NUMBER

# from numpy import block
from libDisk import BLOCKSIZE
import libDisk as ld
from array import *
import math
from collections import deque

MAGIC_NUMBER = 0x5A
SUPERBLOCK = 0x00
ROOT_INODE = 0x01
DEFAULT_DISK_SIZE = 10240
DEFAULT_DISK_NAME = "tinyFSDisk"
MAX_OPEN_FILES = 20
MAX_FILENAME = 8

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
        # self.file_table = None
        self.file_table = [None] * MAX_OPEN_FILES # stores inode number at 
        self.free_fds = deque(range(0, MAX_OPEN_FILES), maxlen=MAX_OPEN_FILES)

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
        self.current_disk = disk

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
            self.free_block_table = [0]*num_free_blocks
        else:
            # Cannot support this disk size. Superblock does not have enough
            # space to track free blocks
            return -2

        # create root directory first
        # doing this in this order so free_block_table gets saved properly
        root = self.create_directory(mode="new", block=ROOT_INODE, parent=ROOT_INODE)
        data = {'block': root.inode.encode()}
        ld.writeBlock(disk, ROOT_INODE, data)

        # 1st byte of superblock is magic number
        # 2nd byte of superblock is root inode block number
        # 3rd byte of superblock is number of free blocks at disk creation
        # remaining bytes are a table tracking the free blocks

        # 1 byte max is 255. num_free_blocks will always be less than 255. 
        superblock_data = [MAGIC_NUMBER, ROOT_INODE, num_free_blocks] + self.free_block_table
        superblock = {"block": array('B', superblock_data)}
        ld.writeBlock(disk, SUPERBLOCK, superblock)

        self.current_disk = None

        return disk

    # tfs_mount(char *filename) “mounts” a TinyFS file system located within ‘filename’. 
    # As part of the mount operation, tfs_mount should verify the file system is the correct
    # type. Only one file system may be mounted at a time.  Must return a specified success/error code.
    def tfs_mount(self, filename):
        disk = ld.openDisk(filename)
        self.current_disk = disk

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

        root_directory = self.create_directory(mode="block", block=ROOT_INODE, parent=ROOT_INODE)
        self.root_dir_fd = self.free_fds.popleft()
        # store open file object, file pointer in file table
        self.file_table[self.root_dir_fd] = (root_directory, 0)
        print(root_directory)

        self.mounted = True
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
        root_dir = self.file_table[self.root_dir_fd][0]
        
        name = name.encode('utf-8')
        if name in root_dir.files:
            inode = root_dir.files[name]
            if name[-1] == "/":
                file = self.create_directory(mode="block", block=inode)
            else:
                file = self.create_file(mode="block", block=inode)

        else:
            # Find open block
            inode = self.allocate(1)
            if inode is None: 
                # No free blocks.
                return -4
            inode = inode[0]

            # Update the file table
            if name[-1] == "/":
                file = self.create_directory(mode="new", block=inode)
            else:
                file = self.create_file(mode="new")
            
            data = {'block': file.inode.encode()}
            ld.writeBlock(self.current_disk, inode, data)
            root_dir.add_file(name, inode)

        fd = self.free_fds.popleft()
        self.file_table[fd] = file
        
        return fd
    
    # Closes the file and removes dynamic resource table entry.
    def tfs_close(self, fs):
        # remove entry from file table, add file descriptor back to queue
        pass

    # Writes buffer ‘buffer’ of size ‘size’, which represents an entire file’s contents, 
    # to the file described by ‘FD’. Sets the file pointer to 0 (the start of file) when done. 
    # Returns success/error codes.
    # Caller must encode bytes
    def tfs_write(self, FD, buffer):
        # use file write() method
        data = buffer['bytes']
        return self.file_table[FD].write(data, len(data))
    
    # deletes a file and marks its blocks as free on disk.
    def tfs_delete(self, FD):
        pass

    # reads one byte from the file and copies it to ‘buffer’, using the current file pointer 
    # location and incrementing it by one upon success. If the file pointer is already at the 
    # end of the file then tfs_readByte() should return an error and not increment the file pointer.
    def tfs_readByte(self, FD, buffer):
        return self.file_table[FD].readByte(buffer)

    # Change the file pointer location to offset (absolute). Returns success/error codes.
    def tfs_seek(self, FD, offset):
        # update file pointer in file_table
        return self.file_table[FD].seek(offset)

    # Allocate a certain number of free blocks.
    # Returns an array of the free block numbers, or None if not enough were found.
    def allocate(self, num_blocks):
        i = 0
        blocks = []
        while i < len(self.free_block_table) and len(blocks) < num_blocks:
            if self.free_block_table[i] == 0:
                blocks.append(i + 2)
            i += 1
        for block in blocks:
            self.free_block_table[block - 2] = 1
        if len(blocks) == num_blocks:
            return blocks
        return None

    # free a data block
    def free(self, block_nums):
        for block in block_nums:
            print(f"free {block}")
            self.free_block_table[block - 2] = 0

    def create_file(self, mode="new", block=None):
        return self.File(self, mode, block)

    def create_directory(self, mode="new", block=None, parent=ROOT_INODE):
        return self.Directory(self, mode, block, parent)

    # pad bytes to ensure it is aligned to a certain size
    def pad(self, bytes, align):
        padding = b""
        if len(bytes) % align != 0:
            padding = b"\0" * (align - (len(bytes) % align))
        return bytes + padding

    class Inode:

        def __init__(self, filesystem, mode="new", filetype = 0, block=None):
            self.fs = filesystem
            if mode == "block" and block is not None: # initialize using preexisting block
                data = {}
                ld.readBlock(self.fs.current_disk, block, data)
                bytes = data['block']
                self.size = bytes[0]
                self.filetype = bytes[1] # 0 for regular file, 1 for directory
                self.num_blocks = bytes[2]
                self.data_blocks = bytes[3:3 + self.num_blocks] # for now, just direct blocks
            elif mode == "new": # create new Inode
                self.size = 0
                self.filetype = filetype
                self.num_blocks = 0
                self.data_blocks = []
            else: # wrong format
                raise ValueError(f"unknown mode type {mode}")

        def encode(self):
            return bytearray([self.size, self.filetype, self.num_blocks] + self.data_blocks)

        def __str__(self):
            return f"Inode(Size: {self.size}, Filetype: {self.filetype}, # Blocks: {self.num_blocks}, Blocks: {self.data_blocks})"


    class File:
        def __init__(self, filesystem, mode="new", block=None):
            self.fs = filesystem
            if mode == "block" and block is not None:
                self.inode = self.fs.Inode(self.fs, mode="block", block=block)
            elif mode == "new":
                self.inode = self.fs.Inode(self.fs, mode="new", filetype=0)
            # Acts as a file pointer. Points to a byte within the file.
            self.position = 0
        
        def write(self, bytes, size):
            # ensure bytes are aligned to blocksize
            bytes = self.fs.pad(bytes, BLOCKSIZE)
            num_blocks = math.ceil(size / BLOCKSIZE)
            if num_blocks > self.inode.num_blocks:
                new_blocks = self.fs.allocate(num_blocks - self.inode.num_blocks)
                if new_blocks:
                    self.inode.data_blocks = self.inode.data_blocks + new_blocks
                else:
                    return -4 # no space
            i = 0
            while i < num_blocks:
                start = i * BLOCKSIZE
                end = (i + 1) * BLOCKSIZE
                buffer = {}
                buffer['block'] = bytes[start:end]
                ld.writeBlock(self.fs.current_disk, self.inode.data_blocks[i], buffer)
                i += 1
            # if extra space, free unused blocks
            self.fs.free(self.inode.data_blocks[i:])
            self.inode.data_blocks = self.inode.data_blocks[:i]
            self.inode.size = size
            self.inode.num_blocks = i
            # Set fp to 0
            self.position = 0
            return 0

        def readByte(self, buffer):
            if self.position >= self.inode.size:
                # file pointer is past the file
                return -5
            # Relative block num
            block_num = self.position // BLOCKSIZE
            # Absolute block num
            block_num = self.inode.data_blocks[block_num]
            local_buffer = {}
            ld.readBlock(self.fs.current_disk, block_num, local_buffer)
            block = local_buffer['block']
            block = bytearray(block)
            byte_index = self.position % BLOCKSIZE
            buffer['byte'] = block[byte_index]
            self.position += 1
            return 0

        def seek(self, position):
            if position >= 0 and position < self.inode.size:
                self.position = position
                return 0
            # Specified position out of bounds
            return -6
            


    class Directory(File):
        
        MAX_FILES_PER_DIRECTORY = BLOCKSIZE // 9 # number of name/inode pairs that can fit within one data block

        def __init__(self, filesystem, mode="new", block=None, parent=ROOT_INODE):
            if block is None:
                raise ValueError("must provide Inode block number for directory")

            self.num_files = 0
            self.files = {}
            if mode == "block" and block is not None:
                super().__init__(filesystem=filesystem, mode=mode, block=block)
                self.files = {}
                num_files = self.inode.size // 9 # 1 byte for Inode number + 8 bytes for file name = 9 bytes per file

                data = {}
                ld.readBlock(self.fs.current_disk, self.inode.data_blocks[0], data)
                bytes = data['block']
                for i in range(num_files):
                    start = 9 * i
                    end = 9 * (i + 1)
                    pair = bytes[start:end]
                    # first byte of each 9 byte sequence is the block number of the Inode
                    inode_block_num = pair[0]
                    inode_name = []
                    for j in range(1, 9):
                        # look for null terminator
                        if pair[j] == 0:
                            break
                        inode_name.append(pair[j].to_bytes(1, byteorder='big'))
                    inode_name = b"".join(inode_name)
                    self.add_file(inode_name, inode_block_num)
                    i += 1

            elif mode == "new":
                self.fs = filesystem
                # initialize with pointers to self and parent
                self.inode = self.fs.Inode(self.fs, "new", filetype=1)
                self.write(b"\0" * BLOCKSIZE, BLOCKSIZE)
                self.add_file(self.fs.pad(b".", MAX_FILENAME), block)
                self.add_file(self.fs.pad(b"..", MAX_FILENAME), parent)
        
        def add_file(self, filename, inode):
            if self.num_files > self.MAX_FILES_PER_DIRECTORY:
                return -1 # too many files
            data = {}
            start = self.num_files * 9
            end = start + 9
            error = ld.readBlock(self.fs.current_disk, self.inode.data_blocks[0], data)
            # print(error)
            bytes = data['block']
            bytes = bytes[:start] + inode.to_bytes(1, byteorder='big') + filename
            self.num_files += 1
            self.write(bytes, self.num_files * 9)
            self.files[filename] = inode
        
        def __str__(self):
            return f"Directory(# Files: {self.num_files}, Files: {self.files})"