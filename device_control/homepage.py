from bdh_sdk import ALL_MODES, INFO, ON, Shortcut, Status

from .ha_client import call_service, get_all_states
from .views import _napoleon_registry

FIREPLACES_OFF = "fireplaces_off"


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


def _lights_on(states):
    # Light groups list their members in an entity_id attribute; skip them
    # so each bulb is counted once.
    return sum(
        1 for s in states
        if s.get("entity_id", "").startswith("light.")
        and s.get("state") == "on"
        and "entity_id" not in (s.get("attributes") or {})
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
    fireplaces = _fireplaces()
    if not fireplaces:
        return []
    return [
        Shortcut(
            id=FIREPLACES_OFF,
            title="Fireplaces off" if len(fireplaces) > 1 else "Fireplace off",
            icon="fa-solid fa-fire",
            order=50,
            modes=ALL_MODES,
        )
    ]


def run_shortcut(shortcut_id):
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
