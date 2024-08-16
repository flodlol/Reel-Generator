# ------------------------------------------------------------ Imports ----------------------------------------------------------- #

# System
from typing import Dict

# -------------------------------------------------------------------------------------------------------------------------------- #



# ------------------------------------------------------ class: Capabilities ----------------------------------------------------- #

class Capabilities:

    # --------------------------------------------------------- Init --------------------------------------------------------- #

    def __init__(
        self,
        d: Dict[str, any]
    ):
        self.accept_insecure_certs       = d.get('acceptInsecureCerts')
        self.browser_name                = d.get('browserName')
        self.browser_version             = d.get('browserVersion')
        self.page_load_strategy          = d.get('pageLoadStrategy')
        self.platform_name               = d.get('platformName')
        self.platform_version            = d.get('platformVersion')
        self.rotatable                   = d.get('rotatable')
        self.set_window_rect             = d.get('setWindowRect')
        self.strict_file_interactability = d.get('strictFileInteractability')
        self.timeouts                    = d.get('timeouts')
        self.unhandled_prompt_behavior   = d.get('unhandledPromptBehavior')


# -------------------------------------------------------------------------------------------------------------------------------- #