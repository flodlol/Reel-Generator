# ------------------------------------------------------------ Imports ----------------------------------------------------------- #

# System
from enum import Enum
import gzip, lzma, bz2#, zipfile

# -------------------------------------------------------------------------------------------------------------------------------- #



# -------------------------------------------------- enum: CompressionAlgorithm -------------------------------------------------- #

class CompressionAlgorithm(Enum):
    GZIP = 0
    LZMA = 1
    BZ2  = 2
    # ZIP  = 3


    # --------------------------------------------------- Public properties -------------------------------------------------- #

    @property
    def _extension(self) -> str:
        return {
            CompressionAlgorithm.GZIP: 'gz',
            CompressionAlgorithm.LZMA: 'xz',
            CompressionAlgorithm.BZ2:  'bz2',
            # CompressionAlgorithm.ZIP:  'zip'
        }[self]

    @property
    def _init_method(self):
        return {
            CompressionAlgorithm.GZIP: gzip.GzipFile,
            CompressionAlgorithm.LZMA: lzma.LZMAFile,
            CompressionAlgorithm.BZ2:  bz2.BZ2File,
            # CompressionAlgorithm.ZIP:  zipfile.ZipFile
        }[self]

    @property
    def _magic_signature(self):
        return {
            CompressionAlgorithm.GZIP: b'\x1f\x8b\x08',
            CompressionAlgorithm.LZMA: b'\x5a\x57\x53',
            CompressionAlgorithm.BZ2:  b'\x42\x5a\x68',
            # CompressionAlgorithm.ZIP:  b'\x50\x4b\x03\x04'
        }[self]

    @property
    def _read_mode(self) -> str:
        return {
            CompressionAlgorithm.GZIP: 'rb',
            CompressionAlgorithm.LZMA: 'rb',
            CompressionAlgorithm.BZ2:  'rb',
            # CompressionAlgorithm.ZIP:  'r'
        }[self]

    @property
    def _write_mode(self) -> str:
        return {
            CompressionAlgorithm.GZIP: 'wb',
            CompressionAlgorithm.LZMA: 'wb',
            CompressionAlgorithm.BZ2:  'wb',
            # CompressionAlgorithm.ZIP:  'w'
        }[self]


# -------------------------------------------------------------------------------------------------------------------------------- #