from gi.repository import Adw, Gtk
from loguru import logger

from src.backend.DeckManagement.InputIdentifier import Input
from src.backend.PluginManager.ActionCore import ActionCore
from src.backend.PluginManager.EventAssigner import EventAssigner


class YapsAction(ActionCore):
    list_command = None
    response_field = None
    choice_label = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.has_configuration = self.list_command is not None
        self.displayed = None
        self.add_event_assigner(EventAssigner(
            id="activate",
            ui_label=self.title,
            callback=self.activate,
            default_event=Input.Key.Events.DOWN,
        ))

    def on_ready(self):
        self.draw()

    def on_tick(self):
        if self.get_is_present() and self.displayed != self.display_state():
            self.draw()

    def display_state(self):
        name = self.get_settings().get("name", "")
        enabled = self.asset == Preset.asset or self.plugin_base.is_active(self.asset, name)
        return name or self.title, enabled

    def draw(self):
        title, enabled = self.display_state()
        icon = "key-on.png" if enabled else "key-off.png"
        self.set_bottom_label(title, update=False)
        self.set_media(media_path=self.get_asset_path(icon, subdirs=[self.asset]))
        self.displayed = title, enabled

    def activate(self, _data=None):
        name = self.get_settings().get("name", "")
        if self.has_configuration and not name:
            self.show_error(2)
            return

        command = f"{self.command}:{name}" if self.has_configuration else self.command
        if self.asset == Preset.asset:
            self.plugin_base.request(command, self.finish)
        else:
            self.plugin_base.toggle(self.asset, name, command, self.finish)

    def finish(self, result):
        try:
            result.result()
        except Exception as error:
            logger.warning("YAPS {}: {}", self.title, error)
            if self.get_is_present():
                self.show_error(2)
        else:
            if self.get_is_present():
                self.draw()

    def get_config_rows(self):
        if not self.has_configuration:
            return []

        current = self.get_settings().get("name", "")
        row = Adw.ComboRow(title=self.choice_label)
        self.set_choices(row, [current] if current else [], current)
        row.connect("notify::selected", self.save_choice)

        refresh = Gtk.Button(label="Refresh")
        refresh.set_valign(Gtk.Align.CENTER)
        row.add_suffix(refresh)
        refresh.connect("clicked", lambda _button: self.refresh_choices(row, refresh))
        self.refresh_choices(row, refresh)
        return [row]

    def refresh_choices(self, row, refresh):
        refresh.set_sensitive(False)
        row.set_subtitle("Loading from YAPS…")

        def finish(result):
            refresh.set_sensitive(True)
            try:
                entries = result.result()[self.response_field]
                names = [self.choice_name(entry) for entry in entries]
            except Exception as error:
                row.set_subtitle(f"Could not load options from YAPS. {error}")
                return

            current = self.get_settings().get("name", "")
            names = list(dict.fromkeys(name for name in [*names, current] if name))
            self.set_choices(row, names, current)
            row.set_subtitle("" if entries else "No options available in YAPS.")

        self.plugin_base.request(self.list_command, finish)

    def set_choices(self, row, names, current):
        row.yaps_loading = True
        row.yaps_names = ["", *names]
        row.set_model(Gtk.StringList.new(["Select…", *names]))
        row.set_selected(row.yaps_names.index(current))
        row.yaps_loading = False

    def save_choice(self, row, _property):
        index = row.get_selected()
        if row.yaps_loading or index >= len(row.yaps_names):
            return
        settings = self.get_settings()
        settings["name"] = row.yaps_names[index]
        self.set_settings(settings)
        if self.get_is_present():
            self.draw()

    def choice_name(self, entry):
        return entry


class Flip(YapsAction):
    title = "Flip Model Horizontally"
    asset = "flip-model"
    command = "set_flip"


class Expression(YapsAction):
    title = "Toggle Expression"
    asset = "expression"
    command = "set_emotion"
    list_command = "get_emotions"
    response_field = "emotions"
    choice_label = "Expression"


class Item(YapsAction):
    title = "Toggle Item"
    asset = "items"
    command = "set_item"
    list_command = "get_items"
    response_field = "items"
    choice_label = "Item"

    def choice_name(self, entry):
        return entry["name"]


class Preset(YapsAction):
    title = "Apply Position Preset"
    asset = "position-preset"
    command = "apply_preset"
    list_command = "get_presets"
    response_field = "presets"
    choice_label = "Position Preset"
