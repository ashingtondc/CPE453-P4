

class tinyFS:

    def __init__(self):
        self.mounted = False
        self.current_fs = None

    def tfs_mkfs(self, filename, nBytes):
        pass

    def tfs_mount(self, filename):
        pass

    def tfs_unmount(self):
        pass

    def tfs_open(self, name):
        pass

    def tfs_close(self, fs):
        pass

    def tfs_write(self, FD, buffer, size):
        pass

    def tfs_delete(self, FD):
        pass

    def tfs_readByte(FD, buffer):
        pass

    def tfs_seek(FD, offset):
        pass

