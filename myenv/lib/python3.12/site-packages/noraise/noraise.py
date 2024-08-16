# ------------------------------------------------------------ Imports ----------------------------------------------------------- #

# System
from typing import Optional, Union, List
import os, traceback
from functools import wraps

# -------------------------------------------------------------------------------------------------------------------------------- #



# -------------------------------------------------------- Public methods -------------------------------------------------------- #

def noraise(
    print_exc: bool = True,
    return_exception: bool = False,
    default_return_value: Optional[any] = None,
    ignored_error_types: Optional[List[any]] = None
) -> Union[Exception, any]:
    """surpasses Exception raise

    KwArgs:
        print_exc (bool, optional):                          If True, prints stacktrace.        Defaults to True.
        return_exception (bool, optional):                   If True, returns caught exception. Defaults to False.
        default_return_value (Optional[any], optional):      What to return upon caught exception if 'return_exception' is False. Defaults to None.
        ignored_error_types (Optional[List[any]], optional): In which cases should the stacktrace print be skipped if 'print_exc' is True. Defaults to None.

    Returns:
        Union[Exception, Any]: if a raise is caught. The exception is returned as result.
    """
    def real_decorator(function):
        @wraps(function)
        def wrapper(*args, **kwargs):
            try:
                return function(*args, **kwargs)
            except KeyboardInterrupt as e:
                raise e
            except Exception as e:
                if print_exc and (not ignored_error_types or type(e) not in ignored_error_types):
                    title = 'Caught with @noraise'
                    clr_start = '\033[1m\033[38;2;255;159;5m'
                    clr_end   = '\033[0m'
                    colored_title = clr_start + title + clr_end

                    print('\n\n{}\n'.format(__comment_line(title).replace(title, colored_title)))
                    traceback.print_exc()
                    print('\n{}\n\n'.format(__comment_line('', text_padding_char='')))

                return e if return_exception else default_return_value

        return wrapper
    return real_decorator


# -------------------------------------------------------- Private methods ------------------------------------------------------- #

def __comment_line(
    text: str,
    start_char: str = '<',
    end_char: str = '>',
    filler_char: str = '-',
    text_padding_char: str = ' ',
    start_end_char_padding_char: str = ' '
) -> str:
    import math

    text = text.strip()
    pre, post = '{}{}'.format(start_char, start_end_char_padding_char), '{}{}'.format(start_end_char_padding_char, end_char)
    needeed_len = os.get_terminal_size().columns - (len(text)+2*len(text_padding_char)) - len(pre) - len(post)

    pre_div_len = math.ceil(needeed_len/2)
    post_div_len = needeed_len - pre_div_len

    return '{}{}{}{}{}{}{}'.format(pre, pre_div_len*filler_char, text_padding_char, text, text_padding_char, post_div_len*filler_char, post)

# -------------------------------------------------------------------------------------------------------------------------------- #