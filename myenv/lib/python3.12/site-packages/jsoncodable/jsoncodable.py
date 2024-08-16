# ------------------------------------------------------------ Imports ----------------------------------------------------------- #

# System
from typing import Optional, Dict, Any, Union
import json, os, io, gzip

# Pip
from noraise import noraise
import jsonpickle

# Local
from ._compressor import Compressor
from .enums import CompressionAlgorithm

# -------------------------------------------------------------------------------------------------------------------------------- #



# ------------------------------------------------------ class: JsonCodable ------------------------------------------------------ #

class JSONCodable:

    # --------------------------------------------------- Public properties -------------------------------------------------- #

    @property
    def dict(self) -> Dict[str, Any]:
        '''Creates, dict from object.'''
        return self.to_dict(self, recursive=False)

    @property
    def json(self) -> Dict[str, Any]:
        '''Same as .dict, but converts all object values to JSONSerializable ones recursively'''
        return json.loads(jsonpickle.encode(self))


    # ---------------------------------------------------- Public methods ---------------------------------------------------- #

    def jsonstr(
        self,
        unpicklable: bool = True,
        indent: Optional[int] = None,
    ) -> str:
        '''Same as .json, but json encoded string'''
        return jsonpickle.encode(self, unpicklable=unpicklable, indent=indent)

    def save_to_file(
        self,
        path: str,
        indent: Optional[int] = 4,
        compression: Optional[CompressionAlgorithm] = None,
        ensure_compression_extension: bool = True
    ) -> str:
        if compression:
            if ensure_compression_extension:
                ext = '.{}'.format(compression._extension)

                if not path.endswith(ext):
                    path += ext
                    print('Added "{}" to the path so it will be "{}"'.format(ext, path))

            Compressor.write(
                path,
                compression,
                self.jsonstr(
                    unpicklable=True,
                    indent=None
                )
            )
        else:
            with open(path, 'w') as f:
                json.dump(self.json, f, indent=indent)

        return path

    # alias
    save = save_to_file

    @classmethod
    @noraise()
    def from_json(
        cls,
        json_file_or_json_file_path_or_json_str_or_dict: Union[
            Union[io.TextIOBase, io.BufferedIOBase, io.RawIOBase, io.IOBase],
            str,
            Dict[str, Any]
        ]
    ) -> Optional:
        return jsonpickle.decode(cls.__get_patched_json_str(json_file_or_json_file_path_or_json_str_or_dict))

    # aliases
    load = from_json
    from_json_file = from_json

    def printjson(
        self,
        unpicklable: bool = False,
        indent: Optional[int] = 4,
    ) -> None:
        print(
            self.jsonstr(
                unpicklable=unpicklable,
                indent=indent
            )
        )

    #alias
    jsonprint = printjson

    @classmethod
    def to_dict(cls, obj: Optional[Any], recursive: bool=True) -> Optional[Dict[str, Any]]:
        return json.loads(jsonpickle.encode(obj)) if recursive else cls.__real__dict__(obj, include_private=False)

    @classmethod
    def full_class_name(cls):
        module = cls.__module__

        if module == '__builtin__':
            return cls.__name__

        return module + '.' + cls.__name__

    # ---------------------------------------------------- Private methods --------------------------------------------------- #

    @classmethod
    @noraise()
    def __get_patched_json_str(
        cls,
        json_file_or_json_file_path_or_json_str_or_dict: Union[
            Union[io.TextIOBase, io.BufferedIOBase, io.RawIOBase, io.IOBase],
            str,
            Dict[str, Any]
        ]
    ) -> Optional[str]:
        d = cls.__get_dict(json_file_or_json_file_path_or_json_str_or_dict)
        d['py/object'] = cls.full_class_name()

        return json.dumps(d)

    @classmethod
    def __get_dict(
        cls,
        json_file_or_json_file_path_or_json_str_or_dict: Union[
            Union[io.TextIOBase, io.BufferedIOBase, io.RawIOBase, io.IOBase],
            str,
            Dict[str, Any]
        ]
    ) -> Dict[str, Any]:
        var = json_file_or_json_file_path_or_json_str_or_dict

        if isinstance(var, str):
            # json string, json file path, gzipped json file path

            possile_paths = [var]
            possile_paths.extend(['{}.{}'.format(var, ca._extension) for ca in CompressionAlgorithm])

            for path in possile_paths:
                if os.path.exists(path):
                    algo = Compressor.detect_algo(path)

                    if algo:
                        return json.loads(Compressor.read(path, algo).decode('utf-8'))
                    else:
                        with open(path, 'r') as f:
                            return json.load(f)

            # json str
            return json.loads(var)

        if (
            isinstance(var, io.TextIOBase)
            or
            isinstance(var, io.BufferedIOBase)
            or
            isinstance(var, io.RawIOBase)
            or
            isinstance(var, io.IOBase)
        ):
            # file
            return json.load(var)

        return var

    @staticmethod
    def __real__dict__(obj, include_private: bool = False) -> Dict[str, Any]:
        object_dict = {}

        for method_name in [method_name for method_name in dir(obj)]:
            if (
                (
                    not include_private and method_name.startswith('_')
                )
                or
                (
                    method_name in dir(JSONCodable())
                )
                or
                (
                    callable(getattr(obj, method_name))
                )
            ):
                continue

            object_dict[method_name] = getattr(obj, method_name)

        return object_dict


# -------------------------------------------------------------------------------------------------------------------------------- #