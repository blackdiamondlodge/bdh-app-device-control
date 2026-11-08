"""Home Assistant scenes: the Scenes tab and the homepage scene shortcuts."""

import logging

from bdh_sdk.settings import app_setting

from .ha_client import call_service, get_all_states

logger = logging.getLogger(__name__)

DEFAULT_ICON = "fas fa-question-circle"

# Home Assistant mdi icons -> Font Awesome classes.
HA_TO_FA_ICON_MAPPING = {
    # ⚡ Power & Energy
    "mdi:lightbulb": "fa-solid fa-lightbulb",  # Light
    "mdi:power-plug": "fa-solid fa-plug",  # Power plug
    "mdi:flash": "fa-solid fa-bolt",  # Electricity
    "mdi:solar-power": "fa-solid fa-solar-panel",  # Solar power

    # 🏠 Home & Rooms
    "mdi:home": "fa-solid fa-house",  # Home
    "mdi:sofa": "fa-solid fa-couch",  # Living room
    "mdi:bed": "fa-solid fa-bed",  # Bedroom
    "mdi:toilet": "fa-solid fa-toilet",  # Bathroom
    "mdi:silverware-fork-knife": "fa-solid fa-utensils",  # Dining room

    # 💡 Lights & Devices
    "mdi:lamp": "fa-solid fa-lightbulb",  # Lamp
    "mdi:ceiling-light": "fa-solid fa-lightbulb",  # Ceiling light
    "mdi:led-strip": "fa-solid fa-grip-lines",  # LED strip
    "mdi:television": "fa-solid fa-tv",  # TV
    "mdi:remote": "fa-solid fa-gamepad",  # Remote control

    # 🔥 Heating & Cooling
    "mdi:thermometer": "fa-solid fa-temperature-high",  # Thermometer
    "mdi:fire": "fa-solid fa-fire",  # Fireplace
    "mdi:snowflake": "fa-solid fa-snowflake",  # Air conditioning

    # 🚗 Garage & Doors
    "mdi:garage": "fa-solid fa-warehouse",  # Garage
    "mdi:garage-open": "fa-solid fa-warehouse",  # Garage (open)
    "mdi:door": "fa-solid fa-door-open",  # Door open
    "mdi:lock": "fa-solid fa-lock",  # Lock
    "mdi:lock-open": "fa-solid fa-unlock",  # Unlock

    # 🍳 Cooking & Kitchen
    "mdi:stove": "fa-solid fa-fire-burner",  # Stove
    "mdi:fridge": "fa-solid fa-icicles",  # Refrigerator
    "mdi:coffee": "fa-solid fa-mug-hot",  # Coffee machine
    "mdi:microwave": "fa-solid fa-wave-square",  # Microwave

    # 🎬 Entertainment & Media
    "mdi:movie": "fa-solid fa-film",  # Movies
    "mdi:popcorn": "fa-solid fa-popcorn",  # Movie night
    "mdi:speaker": "fa-solid fa-volume-up",  # Speaker
    "mdi:headphones": "fa-solid fa-headphones",  # Music
    "mdi:radio": "fa-solid fa-radio",  # Radio
    "mdi:gamepad": "fa-solid fa-gamepad",  # Gaming console

    # 🚗 Vehicles & Travel
    "mdi:car": "fa-solid fa-car",  # Car
    "mdi:bicycle": "fa-solid fa-bicycle",  # Bicycle
    "mdi:train": "fa-solid fa-train",  # Train
    "mdi:bus": "fa-solid fa-bus",  # Bus
    "mdi:airplane": "fa-solid fa-plane",  # Airplane

    # 🌡 Weather
    "mdi:weather-sunny": "fa-solid fa-sun",  # Sunny
    "mdi:weather-partly-cloudy": "fa-solid fa-cloud-sun",  # Partly cloudy
    "mdi:weather-cloudy": "fa-solid fa-cloud",  # Cloudy
    "mdi:weather-rainy": "fa-solid fa-cloud-showers-heavy",  # Rain
    "mdi:weather-snowy": "fa-solid fa-snowflake",  # Snow
    "mdi:weather-lightning": "fa-solid fa-bolt",  # Thunderstorm

    # 🔔 Alerts & Security
    "mdi:bell": "fa-solid fa-bell",  # Notifications
    "mdi:security": "fa-solid fa-shield-halved",  # Security system
    "mdi:alarm-light": "fa-solid fa-exclamation-triangle",  # Alarm
    "mdi:cctv": "fa-solid fa-video",  # Security camera

    # 📦 Sensors & Smart Devices
    "mdi:motion-sensor": "fa-solid fa-running",  # Motion sensor
    "mdi:water": "fa-solid fa-tint",  # Water sensor
    "mdi:smoke-detector": "fa-solid fa-smoking-ban",  # Smoke detector
    "mdi:gas-cylinder": "fa-solid fa-gas-pump",  # Gas sensor
    "mdi:battery": "fa-solid fa-battery-half",  # Battery

    # 🚪 Doors & Windows
    "mdi:window-closed": "fa-solid fa-window-close",  # Window closed
    "mdi:window-open": "fa-solid fa-window-maximize",  # Window open

    # 🌱 Outdoor & Gardening
    "mdi:flower": "fa-solid fa-seedling",  # Gardening
    "mdi:tree": "fa-solid fa-tree",  # Tree
    "mdi:grass": "fa-solid fa-leaf",  # Lawn
    "mdi:pool": "fa-solid fa-swimmer",  # Pool
    "mdi:sprinkler": "fa-solid fa-tint",  # Sprinkler system

    # 🔋 Power & Electricity
    "mdi:car-battery": "fa-solid fa-car-battery",  # Car battery
    "mdi:solar-panel": "fa-solid fa-solar-panel",  # Solar panel

    "mdi:theater": "fas fa-tv",
    "mdi:chef-hat": "fas fa-blender",
    "mdi:briefcase": "fas fa-briefcase",
    "mdi:food": "fas fa-utensils",
    "mdi:account-voice": "fas fa-glass-cheers",
}


def scene_filter():
    """Lower-cased scene names to show (empty = all).

    BDH_DEVICE_CONTROL_SCENES_FILTER, or the old scenes-app names
    BDH_SCENES_FILTER / SCENE_FILTER.
    """
    value = app_setting("device_control", "scenes_filter", "",
                        legacy=("BDH_SCENES_FILTER", "SCENE_FILTER"))
    if isinstance(value, str):
        value = value.split(",")
    return [name.strip().lower() for name in value if name.strip()]


def icon_for(ha_icon):
    icon = HA_TO_FA_ICON_MAPPING.get(ha_icon, DEFAULT_ICON)
    if icon == DEFAULT_ICON and ha_icon:
        logger.info("Unsupported Home Assistant icon: %s", ha_icon)
    return icon


def get_scenes(states=None):
    """Scenes as ``{"id", "name", "icon"}`` dicts. Raises HAError when HA is down."""
    if states is None:
        states = get_all_states()
    wanted = scene_filter()
    scenes = []
    for state in states:
        entity_id = state.get("entity_id", "")
        if not entity_id.startswith("scene."):
            continue
        attrs = state.get("attributes") or {}
        name = attrs.get("friendly_name", entity_id)
        if wanted and name.lower() not in wanted:
            continue
        scenes.append({"id": entity_id, "name": name, "icon": icon_for(attrs.get("icon"))})
    return scenes


def activate_scene(scene_id):
    ok, err = call_service("scene", "turn_on", scene_id)
    if not ok:
        raise RuntimeError(err or "Scene failed")
