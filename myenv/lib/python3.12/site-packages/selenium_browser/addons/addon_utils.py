# ------------------------------------------------------------ Imports ----------------------------------------------------------- #

# System
from typing import Optional, List
import os

# Local
from .models import AddonInstallSettings

# -------------------------------------------------------------------------------------------------------------------------------- #



# ------------------------------------------------------- class: AddonUtils ------------------------------------------------------ #

class AddonUtils:

    # ---------------------------------------------------- Public methods ---------------------------------------------------- #

    @classmethod
    def get_all_addons(
        cls,
        supported_addon_file_extensions: List[str],
        addons_folder_path: Optional[str] = None,
        user_addon_settings: Optional[List[AddonInstallSettings]] = None,
        lib_addon_settings: Optional[List[AddonInstallSettings]] = None
    ) -> List[AddonInstallSettings]:
        addon_settings = lib_addon_settings or []

        if user_addon_settings:
            addon_settings.extend(user_addon_settings)

        if addons_folder_path and os.path.exists(addons_folder_path):
            addon_settings.extend(cls.addons_from_folder(addons_folder_path, supported_addon_file_extensions))

        return addon_settings

    @staticmethod
    def addons_from_folder(
        folder_path: str,
        supported_addon_file_extensions: List[str]
    ) -> List[AddonInstallSettings]:
        for (dirpath, _, filenames) in os.walk(folder_path):
            return [
                AddonInstallSettings(os.path.join(dirpath, f))
                for f in filenames if f.split('.')[-1] in supported_addon_file_extensions
            ]


# -------------------------------------------------------------------------------------------------------------------------------- #