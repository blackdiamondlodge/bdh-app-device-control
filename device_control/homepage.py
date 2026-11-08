from bdh_sdk import ALL_MODES, INFO, ON, Shortcut, Status

from .device_config import TABS
from .ha_client import call_service, get_all_states
from .scenes import activate_scene, get_scenes
from .views import _napoleon_registry

FIREPLACES_OFF = "fireplaces_off"
SCENE_PREFIX = "scene-"


def _fireplaces(states=None):
    """Napoleon fireplace climate entities with their current state."""
    registry = _napoleon_registry()
    climates = {
        eid for eid in registry["entities"] if eid.startswith("climate.")
    }
    if states is None:
        states = get_all_states()
    return [s for s in states if s.get("entity_id") in climates]


def _is_on(state):
    return state.get("state") not in ("off", "unavailable", "unknown", None)


def _configured_lights():
    return {
        dev["entity_id"]
        for tab in TABS
        for devices in tab["devices"].values()
        for dev in devices
        if dev.get("type") == "light"
    }


def _lights_on(states):
    # Only lights shown in the app count, so AP LEDs and appliance lights
    # don't inflate the number.
    lights = _configured_lights()
    return sum(
        1 for s in states
        if s.get("entity_id") in lights and s.get("state") == "on"
    )


def _fireplace_text(fireplaces):
    on = sum(1 for s in fireplaces if _is_on(s))
    if on == 0:
        return "Fireplaces off" if len(fireplaces) > 1 else "Fireplace off"
    if len(fireplaces) == 1:
        return "Fireplace on"
    return f"{on} of {len(fireplaces)} fireplaces on"


def status():
    states = get_all_states()
    lights = _lights_on(states)
    fireplaces = _fireplaces(states)
    parts = [f"{lights} light{'s' if lights != 1 else ''} on" if lights else "All lights off"]
    if fireplaces:
        parts.append(_fireplace_text(fireplaces))
    anything_on = lights or any(_is_on(s) for s in fireplaces)
    return Status(" · ".join(parts), ON if anything_on else INFO)


def shortcuts():
    states = get_all_states()
    items = [
        Shortcut(
            id=SCENE_PREFIX + scene["id"].removeprefix("scene."),
            title=scene["name"],
            icon=scene["icon"],
            order=10,
            modes=ALL_MODES,
        )
        for scene in get_scenes(states)
    ]
    fireplaces = _fireplaces(states)
    if any(_is_on(s) for s in fireplaces):
        items.append(Shortcut(
            id=FIREPLACES_OFF,
            title="Fireplaces off" if len(fireplaces) > 1 else "Fireplace off",
            icon="fa-solid fa-fire",
            order=50,
            modes=ALL_MODES,
        ))
    return items


def run_shortcut(shortcut_id):
    if shortcut_id.startswith(SCENE_PREFIX):
        scene_id = "scene." + shortcut_id.removeprefix(SCENE_PREFIX)
        if scene_id not in {s["id"] for s in get_scenes()}:
            raise ValueError(shortcut_id)
        activate_scene(scene_id)
        return None
    if shortcut_id != FIREPLACES_OFF:
        raise ValueError(shortcut_id)
    lit = [s["entity_id"] for s in _fireplaces() if _is_on(s)]
    for entity_id in lit:
        ok, err = call_service("climate", "turn_off", entity_id)
        if not ok:
            raise RuntimeError(err)
    if not lit:
        return "Fireplaces are already off"
    return None
