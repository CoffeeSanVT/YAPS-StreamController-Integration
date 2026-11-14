from concurrent.futures import ThreadPoolExecutor
from functools import partial

from gi.repository import Adw, GLib, Gtk

from src.backend.DeckManagement.InputIdentifier import Input
from src.backend.PluginManager.ActionHolder import ActionHolder
from src.backend.PluginManager.ActionInputSupport import ActionInputSupport
from src.backend.PluginManager.PluginBase import PluginBase

from .actions import Expression, Flip, Item, Preset
from .yaps import DEFAULT_URL, exchange


class YapsPlugin(PluginBase):
    def __init__(self):
        super().__init__()
        self.has_plugin_settings = True
        self.worker = ThreadPoolExecutor(max_workers=1, thread_name_prefix="yaps")
        self.active = {}
        self.url = self.get_settings().get("server_url") or DEFAULT_URL
        self.add_actions()
        self.register()

    def add_actions(self):
        support = {
            Input.Key: ActionInputSupport.SUPPORTED,
            Input.Dial: ActionInputSupport.UNSUPPORTED,
            Input.Touchscreen: ActionInputSupport.UNSUPPORTED,
            Input.TouchKey: ActionInputSupport.UNSUPPORTED,
            Input.Screen: ActionInputSupport.UNSUPPORTED,
        }
        for action in (Flip, Expression, Item, Preset):
            icon = self.get_asset_path("icon.png", subdirs=[action.asset])
            self.add_action_holder(ActionHolder(
                plugin_base=self,
                action_core=action,
                action_id_suffix=action.asset,
                action_name=action.title,
                icon=Gtk.Image.new_from_file(icon),
                action_support=support,
            ))

    def get_settings_area(self):
        row = Adw.EntryRow(title="YAPS WebSocket URL")
        row.set_text(self.url)
        row.set_show_apply_button(True)
        row.connect("apply", self.save_url)
        group = Adw.PreferencesGroup()
        group.add(row)
        return group

    def save_url(self, row):
        settings = self.get_settings()
        settings["server_url"] = row.get_text().strip() or DEFAULT_URL
        self.set_settings(settings)
        self.url = settings["server_url"]
        row.set_text(self.url)

    def submit(self, operation, callback):
        future = self.worker.submit(operation, self.url)
        future.add_done_callback(lambda result: GLib.idle_add(callback, result))

    def request(self, command, callback):
        self.submit(partial(exchange, command=command, response=True), callback)

    def toggle(self, asset, name, command, callback):
        def send(url):
            key = (url, asset)
            active = self.active.get(key, frozenset())
            enabled = name not in active
            exchange(url, f"{command}:{str(enabled).lower()}")
            if enabled and asset == Expression.asset:
                active = frozenset({name})
            elif enabled:
                active = active | {name}
            else:
                active = active - {name}
            self.active[key] = active

        self.submit(send, callback)

    def is_active(self, asset, name):
        return name in self.active.get((self.url, asset), ())
