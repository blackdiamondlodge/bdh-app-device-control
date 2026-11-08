from bdh_sdk import PluginSpec, Tile

spec = PluginSpec(
    id="device_control",
    app="device_control",
    urls="device_control.urls",
    status="device_control.homepage.status",
    shortcuts="device_control.homepage.shortcuts",
    run_shortcut="device_control.homepage.run_shortcut",
    tiles=(
        Tile(
            title="Controls",
            url_name="device_control",
            icon="device_control/hub/icon.svg",
            section="lodge",
            subtitle="Lights, shades, fireplaces & more",
            order=10,
        ),
    ),
)
