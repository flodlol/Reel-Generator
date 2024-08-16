# ------------------------------------------------------------ Imports ----------------------------------------------------------- #

# System
from  typing import Optional, Dict, Union, Tuple
import os, tempfile, platform, subprocess

# Pip
from kproxy import Proxy

# Local
from .__resources.constants import Constants

# -------------------------------------------------------------------------------------------------------------------------------- #



# --------------------------------------------------------- class: Utils --------------------------------------------------------- #

class Utils:

    # ---------------------------------------------------- Public methods ---------------------------------------------------- #

    @classmethod
    def get_cache_paths(
        cls,
        profile_path: Optional[str] = None,
        profile_id: Optional[str] = None
    ) -> Tuple[str, str, str]:
        profile_path = cls.profile_folder_path(profile_path, profile_id)

        return (
            profile_path,
            os.path.join(profile_path, Constants.GENERAL_COOKIES_FOLDER_NAME),
            os.path.join(profile_path, Constants.USER_AGENT_FILE_NAME)
        )

    @staticmethod
    def profile_folder_path(
        profile_path: Optional[str] = None,
        profile_id: Optional[str] = None
    ) -> str:
        return profile_path or os.path.join(
            '/tmp' if platform.system() == 'Darwin' else tempfile.gettempdir(),
            profile_id or Constants.GENERAL_PROFILE_FOLDER_NAME
        )

    @classmethod
    def cookies_folder_path(
        cls,
        profile_path: Optional[str] = None,
        profile_id: Optional[str] = None
    ) -> str:
        return os.path.join(
            profile_path or cls.profile_folder_path(
                profile_path=profile_path,
                profile_id=profile_id
            ),
            Constants.GENERAL_COOKIES_FOLDER_NAME
        )

    @classmethod
    def user_agent_path(
        cls,
        profile_path: Optional[str] = None,
        profile_id: Optional[str] = None
    ) -> str:
        return os.path.join(
            profile_path or cls.profile_folder_path(
                profile_path=profile_path,
                profile_id=profile_id
            ),
            Constants.USER_AGENT_FILE_NAME
        )

    @staticmethod
    def user_agent(
        user_agent: Optional[str] = None,
        file_path: Optional[str] = None
    ) -> Optional[str]:
        if file_path and os.path.exists(file_path):
            with open(file_path, 'r') as f:
                return f.read().strip()
        elif user_agent:
            user_agent = user_agent.strip()

            if file_path:
                with open(file_path, 'w') as f:
                    f.write(user_agent)

            return user_agent

        return None

    @staticmethod
    def proxy(
        proxy: Optional[Union[Proxy, str]] = None,

        # proxy - legacy (kept for convenience)
        host: Optional[str] = None,
        port: Optional[int] = None,
    ) -> Optional[Proxy]:
        if not proxy:
            if not host and not port:
                return None

            proxy = Proxy(host=host, port=port)

        return proxy if isinstance(proxy, Proxy) else Proxy.from_str(proxy)


# -------------------------------------------------------------------------------------------------------------------------------- #