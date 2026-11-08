# bdh-app-device-control

Black Diamond Hub app: the lodge Controls page (scenes, lights, blinds, fireplaces, Gemstone Lights) via Home Assistant. Moved out of
[BlackDiamondHub](https://github.com/blackdiamondlodge/BlackDiamondHub) and
installed into the hub through the `blackdiamondhub.plugins` entry point
(see [bdh-sdk](https://github.com/blackdiamondlodge/bdh-sdk)).

Page: `/device_control/` (homepage tile "Controls").

Home Assistant scenes appear on the first tab and as homepage quick
actions. Set `BDH_DEVICE_CONTROL_SCENES_FILTER` (comma-separated
friendly names) to show only some of them; the old scenes-app names
`BDH_SCENES_FILTER` and `SCENE_FILTER` still work.

## Development

CI (`.github/workflows/ci.yml`) uses the reusable `app-ci.yml` from
bdh-sdk. It builds the wheel, installs it next to the hub, then runs
`hub_smoke`, the app tests and the selenium tests.

To release, bump `version` in `pyproject.toml`. When that lands on
`main`, `release.yml` tags it and publishes the wheel, and the release
notes include the hashed line for the hub's `sites/<site>/apps.txt`.
