# ------------------------------------------------------------ Imports ----------------------------------------------------------- #

# System
from typing import Optional, Union
import os

# Local
from .enums import CompressionAlgorithm

# -------------------------------------------------------------------------------------------------------------------------------- #



# ------------------------------------------------------- class: Compressor ------------------------------------------------------ #

class Compressor:

    # ---------------------------------------------------- Public methods ---------------------------------------------------- #

    @classmethod
    def read(
        cls,
        path: str,
        algo: Optional[CompressionAlgorithm] = None
    ) -> Optional:
        algo = algo or cls.detect_algo(path)

        if not algo:
            return None

        return algo._init_method(path, algo._read_mode).read()

    @classmethod
    def write(
        cls,
        path: str,
        algo: CompressionAlgorithm,
        data
    ) -> bool:
        if isinstance(data, str):
            data = data.encode('utf-8')

        algo._init_method(path, algo._write_mode).write(data)

        return os.path.exists(path)

    @staticmethod
    def detect_algo(path: str) -> Optional[CompressionAlgorithm]:
        for algo in CompressionAlgorithm:
            if path.endswith('.{}'.format(algo._extension)):
                return algo

        with open(path, 'rb') as f:
            for algo in CompressionAlgorithm:
                magic_signature = algo._magic_signature

                if f.read(len(magic_signature)) == magic_signature:
                    return algo

        return None


# -------------------------------------------------------------------------------------------------------------------------------- #