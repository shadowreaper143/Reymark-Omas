import json
from pathlib import Path


# ============================================================
# SETTINGS FILE
# ============================================================

SETTINGS_FILE = (
    Path(__file__).resolve().parent / "settings.json"
)


# ============================================================
# DEFAULT SETTINGS
# ============================================================

DEFAULT_SETTINGS = {

    "audio": {
        "sound_volume": 0.8
    },

    "controls": {
        "mobile_controls": True
    },

    "display": {
        "screen_width": 800,
        "screen_height": 600,
        "fullscreen": False
    },

    "player": {
        "default_username": "Player1",
        "default_email": "player1@example.com"
    },

    "database": {
        "host": "localhost",
        "port": 3306,
        "user": "root",
        "password": "",
        "database": "space_shooter"
    }
}


# ============================================================
# LOAD SETTINGS
# ============================================================

def load_settings():

    if not SETTINGS_FILE.exists():

        save_settings(DEFAULT_SETTINGS)

        return DEFAULT_SETTINGS.copy()

    try:

        with open(
            SETTINGS_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            settings = json.load(file)

        # Make sure missing sections are restored
        for section, values in DEFAULT_SETTINGS.items():

            if section not in settings:

                settings[section] = values.copy()

            elif isinstance(values, dict):

                for key, value in values.items():

                    if key not in settings[section]:

                        settings[section][key] = value

        return settings

    except (
        json.JSONDecodeError,
        OSError
    ):

        print(
            "Warning: settings.json could not be read."
        )

        print(
            "Restoring default settings."
        )

        save_settings(DEFAULT_SETTINGS)

        return DEFAULT_SETTINGS.copy()


# ============================================================
# SAVE SETTINGS
# ============================================================

def save_settings(settings):

    with open(
        SETTINGS_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            settings,
            file,
            indent=4
        )


# ============================================================
# UPDATE ONE SETTING
# ============================================================

def update_setting(
    section,
    key,
    value
):

    settings = load_settings()

    if section not in settings:

        settings[section] = {}

    settings[section][key] = value

    save_settings(settings)

    return settings


# ============================================================
# GET ONE SETTING
# ============================================================

def get_setting(
    section,
    key,
    default=None
):

    settings = load_settings()

    if section not in settings:

        return default

    return settings[section].get(
        key,
        default
    )


# ============================================================
# RESET SETTINGS
# ============================================================

def reset_settings():

    save_settings(DEFAULT_SETTINGS)

    return load_settings()