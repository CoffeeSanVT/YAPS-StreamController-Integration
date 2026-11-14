# YAPS StreamController Integration

## Requirements
- StreamController 1.5.0-beta.16 or later
- WebSocket server should be enable inside YAPS
- Git for cloning the repository. You can also download and extract the ZIP.

## Install
Close StreamController, then clone the repository and run the installer from your checkout.
```bash
git clone https://github.com/CoffeeSanVT/YAPS-StreamController-Integration.git
cd YAPS-StreamController-Integration
bash install.sh
```

If you downloaded the ZIP, extract it and run `bash install.sh` from the extracted folder.

The installer uses `~/.var/app/com.core447.StreamController/data/plugins` by default. If you use a custom StreamController data directory, pass its path to the installer.

```bash
bash install.sh "/path/to/StreamController/data"
```

If a separate copy of the plugin is already installed, move its folder out of the `plugins` directory before reinstalling. Restart StreamController after installation.

## Set up your keys

1. Open YAPS and enable its WebSocket server. The default address is `ws://localhost:19167`.
2. Open StreamController, select a key, and find **YAPS** in the action picker.
3. Add **Flip Model Horizontally**, **Toggle Expression**, **Toggle Item**, or **Apply Position Preset**.
4. For expressions, items, and presets, select an option in the key editor. Click **Refresh** to reload the list from YAPS.

To use a different address, open the **YAPS** plugin settings, edit **YAPS WebSocket URL**, and apply the change.

## Troubleshooting

- **YAPS is missing from the action picker.** Check the plugin folder and StreamController version, then restart StreamController.
- **The option list fails to load.** Confirm YAPS is running, its WebSocket server is enabled, and the URL matches. Click **Refresh** to retry.
- **A key's indicator is out of sync.** The indicators track commands sent by the plugin during the current session. Changing an expression, item, or model orientation directly in YAPS can leave its indicator out of sync.

## License
[MIT](LICENSE)
