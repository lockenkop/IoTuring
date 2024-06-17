from IoTuring.Entity.Entity import Entity
from IoTuring.Configurator.MenuPreset import MenuPreset
from IoTuring.MyApp.SystemConsts import OperatingSystemDetection as OsD
from IoTuring.Entity.EntityData import EntityCommand, EntitySensor
from IoTuring.Logger.consts import STATE_OFF, STATE_ON


KEY = "wlrctl"
KEY_STATE = "wlrctl_state"


CONFIG_KEY_DOMAIN = "domain"
DOMAIN_CHOICES = [
    {"name": "Keyboard", "value": "keyboard"},
    {"name": "Pointer", "value": "pointer"},
    {"name": "Toplevel", "value": "toplevel"},
]

CONFIG_KEY_KEYBOARD_ACTION = "keyboard_action"
KEYBOARD_ACTIONS = [
    {"name": "Type", "value": "type"},
]
# actions are:
#   type <string> [modifiers]: Send a string to be typed into the focused client
#        modifiers <SHIFT,CTRL,ALT,SUPER>: Comma separated list of modifiers to be held while typing
TYPE_INSTRUCTION = """type <string> [modifiers]: Send a string to be typed into the focused client
                                    modifiers <SHIFT,CTRL,ALT,SUPER>: Comma separated list of modifiers to be held while typing"""

CONFIG_KEY_KEYBOARD_KEYS = "keys"

CONFIG_KEY_KEYBOARD_MODIFIERS = "modifiers"
CONFIG_KEY_KEYBOARD_MODIFIERS_YES = "keyboard_modifiers_yes"
KEYBOARD_MODIFIERS = [
    {"name": "Shift", "value": "SHIFT"},
    {"name": "Ctrl", "value": "CTRL"},
    {"name": "Alt", "value": "ALT"},
    {"name": "Super", "value": "SUPER"},
]


CONFIG_KEY_POINTER_ACTION = "pointer_action"
POINTER_ACTIONS = [
    {"name": "Click", "value": "click"},
    {"name": "Move", "value": "move"},
    {"name": "Scroll", "value": "scroll"},
]
POINTER_CLICK_INSTRUCTIONS = (
    'buttons are "left", "right", "middle", "back", "forward", "exra", "side"'
)
# actions are
#   click [button]: Click a mouse button. If unspecified, clicks the default (left) button.
#   move <dx> <dy>: Move the Curosor dx, dy pixels. dx is the displacement in positive-right direction, dy is the displacement in positive-downward direction, negatives allowed
#   scroll <dy> <dx>: Scroll the wheel dy units vertically and dx units horizontally, negatives allowed

CONFIG_KEY_POINTER_BUTTON = "button"
CONFIG_KEY_POINTER_DX = "dx"
CONFIG_KEY_POINTER_DY = "dy"


CONFIG_KEY_TOPLEVEL_ACTION = "toplevel_action"
TOPLEVEL_ACTIONS = [
    {"name": "Minimize", "value": "minimize"},
    {"name": "Maximize", "value": "maximize"},
    {"name": "Fullscreen", "value": "fullscreen"},
    {"name": "Focus", "value": "focus"},
    {"name": "Find", "value": "find"},
    {"name": "Wait", "value": "wait"},
    {"name": "Waitfor", "value": "waitfor"},
]
# actions are
#   minimize: Instruct the compositor to minimize matching windows
#   maximize: Instruct the compositor to maximize matching windows
#   fullscreen: Instruct the compositor to fullscreen matching windows
#   focus: Instruct the compositor to focus matching windows
#   find: Exit with a successful return code if there is at least one window matching the provided criteria
#   wait: Wait with a successfull return code until all mathcing windows have closed. If there are no matches, exit with a failing return code immediatlely
#   waitfor: Wwait to return a successfull return code until there is at least one window that matches the requested criteria

CONFIG_KEY_TOPLEVEL_APP_ID = "app_id"
CONFIG_KEY_TOPLEVEL_STATE = "state"
CONFIG_KEY_TOPLEVEL_TITLE = "title"


TOPLEVEL_STATE_CHOICES = [
    {"name": "Fullscreen", "value": "fullscreen"},
    {"name": "Maximized", "value": "maximized"},
    {"name": "Minimized", "value": "minimized"},
    {"name": "Active", "value": "active"},
    {"name": "Inactive", "value": "inactive"},
    {"name": "Unmaximized", "value": "unmaximized"},
    {"name": "Unminimized", "value": "unminimized"},
    {"name": "Unfullscreen", "value": "unfullscreen"},
]

CONFIG_KEY_OUTPUT_ACTION = "output_action"
OUTPUT_ACTIONS = [
    {"name": "List", "value": "list"},
]
# actions are:
#   list - lists all known outputs


class Wlrctl(Entity):
    """Entity to control Wayland compositor"""

    NAME = "Wlrctl"
    ALLOW_MULTI_INSTANCE = True

    def Initialize(self):
        self.domain = ""
        self.action = ""
        self.keys = ""
        self.modifiers_yes = ""
        self.modifiers = ""
        self.button = ""
        self.dx = ""
        self.dy = ""
        self.command = ""
        self.matchspec = ""
        self.hasValue = False
        self.hasCommand = False
        self.state = ""

        self.domain = self.GetFromConfigurations(CONFIG_KEY_DOMAIN)
        self.Log(self.LOG_DEBUG, f"initializing wlrctl {self.domain}")
        # get the configuration depending on the domain
        if self.domain == "keyboard":
            self.action = self.GetFromConfigurations(CONFIG_KEY_KEYBOARD_ACTION)
            if self.action == "type":
                self.keys = self.GetFromConfigurations(CONFIG_KEY_KEYBOARD_KEYS)
                self.modifiers_yes = self.GetFromConfigurations(
                    CONFIG_KEY_KEYBOARD_MODIFIERS_YES
                )
                self.modifiers = self.GetFromConfigurations(
                    CONFIG_KEY_KEYBOARD_MODIFIERS
                )
                if self.modifiers_yes == "N":
                    self.command = f"wlrctl {self.domain} {self.action} '{self.keys}'"
                else:
                    self.command = f"wlrctl {self.domain} {self.action} '{self.keys}' modifiers {self.modifiers}"
            else:
                self.Log(
                    self.LOG_DEBUG, f"Keyboard Action {self.action} not implemented"
                )
                raise Exception("Action not implemented")

        elif self.domain == "pointer":
            self.action = self.GetFromConfigurations(CONFIG_KEY_POINTER_ACTION)
            if self.action == "click":
                self.button = self.GetFromConfigurations(CONFIG_KEY_POINTER_BUTTON)
                self.command = f"wlrctl {self.domain} {self.action} {self.button}"
            elif self.action == "move":
                self.dx = self.GetFromConfigurations(CONFIG_KEY_POINTER_DX)
                self.dy = self.GetFromConfigurations(CONFIG_KEY_POINTER_DY)
                self.command = f"wlrctl {self.domain} {self.action} {self.dx} {self.dy}"
            elif self.action == "scroll":
                self.dx = self.GetFromConfigurations(CONFIG_KEY_POINTER_DX)
                self.dy = self.GetFromConfigurations(CONFIG_KEY_POINTER_DY)
                self.command = f"wlrctl {self.domain} {self.action} {self.dy} {self.dx}"
            else:
                self.Log(
                    self.LOG_DEBUG, f"Pointer Action {self.action} not implemented"
                )
                raise Exception("Action not implemented")

        elif self.domain == "toplevel":
            self.action = self.GetFromConfigurations(CONFIG_KEY_TOPLEVEL_ACTION)
            app_id = self.GetFromConfigurations(CONFIG_KEY_TOPLEVEL_APP_ID)
            title = self.GetFromConfigurations(CONFIG_KEY_TOPLEVEL_TITLE)
            state = self.GetFromConfigurations(CONFIG_KEY_TOPLEVEL_STATE)
            if app_id:
                self.matchspec += f"app_id:{app_id}"
            if title:
                self.matchspec += f" title:{title}"
            if state:
                self.matchspec += f" state:{state}"
            self.command = f"wlrctl {self.domain} {self.action} {self.matchspec}"
            if self.action in ["find", "wait", "waitfor"]:
                self.hasValue = True
                self.RegisterEntitySensor(EntitySensor(self, KEY_STATE))

        elif self.domain == "output":
            self.action = self.GetFromConfigurations(CONFIG_KEY_OUTPUT_ACTION)
            self.command = f"wlrctl {self.domain} {self.action}"

        self.RegisterEntitySensor(
            EntitySensor(self, KEY_STATE, supportsExtraAttributes=True)
        )

        self.RegisterEntityCommand(EntityCommand(self, KEY, self.Callback, KEY_STATE))
        self.hasCommand = True

    def Update(self):
        if self.hasValue:
            self.Log(self.LOG_DEBUG, f"Running {self.command}")
            command = self.RunCommand(self.command)
            self.state = STATE_ON if command.returncode == 0 else STATE_OFF

            self.SetEntitySensorValue(KEY_STATE, self.state)

        else:
            pass

    def Callback(self, message):
        self.Log(self.LOG_DEBUG, f"Running {self.command}")
        command = self.RunCommand(self.command)

        if command.returncode != 0:
            self.Log(self.LOG_ERROR, f"Error running {self.command}")
            return False

    @classmethod
    def ConfigurationPreset(cls) -> MenuPreset:
        preset = MenuPreset()
        preset.AddEntry(
            name="Select domain",
            key=CONFIG_KEY_DOMAIN,
            mandatory=True,
            question_type="select",
            choices=DOMAIN_CHOICES,
        )

        #
        # keyboard domain
        #
        preset.AddEntry(
            name="Select keyboard action",
            instruction=TYPE_INSTRUCTION,
            key=CONFIG_KEY_KEYBOARD_ACTION,
            mandatory=True,
            question_type="select",
            choices=KEYBOARD_ACTIONS,
            display_if_key_value={CONFIG_KEY_DOMAIN: "keyboard"},
        )

        preset.AddEntry(
            name="Which string should be sent?",
            key=CONFIG_KEY_KEYBOARD_KEYS,
            mandatory=True,
            question_type="text",
            display_if_key_value={CONFIG_KEY_KEYBOARD_ACTION: "type"},
        )
        # TODO modifiers work janky in my testing
        # ask yes or no for modifiers
        # preset.AddEntry(
        #     name="Should a modifier be used?",
        #     key=CONFIG_KEY_KEYBOARD_MODIFIERS_YES,
        #     mandatory=True,
        #     question_type="yesno",
        #     choices=POINTER_ACTIONS,
        #     display_if_key_value={CONFIG_KEY_KEYBOARD_ACTION: "type"},
        # )
        # asking for multiple modifiers requires ability to select multiple choices TODO
        # preset.AddEntry(
        #     name="Select keyboard modifiers",
        #     key=CONFIG_KEY_KEYBOARD_MODIFIERS,
        #     mandatory=True,
        #     question_type="select",
        #     choices=KEYBOARD_MODIFIERS,
        #     display_if_key_value={CONFIG_KEY_KEYBOARD_MODIFIERS_YES: "Y"},
        # )

        #
        # pointer domain
        #
        preset.AddEntry(
            name="Select pointer action",
            key=CONFIG_KEY_POINTER_ACTION,
            mandatory=True,
            question_type="select",
            choices=POINTER_ACTIONS,
            display_if_key_value={CONFIG_KEY_DOMAIN: "pointer"},
        )
        #
        # click
        #
        preset.AddEntry(
            name="Select button",
            key=CONFIG_KEY_POINTER_BUTTON,
            instruction=POINTER_CLICK_INSTRUCTIONS,
            mandatory=True,
            question_type="text",
            display_if_key_value={CONFIG_KEY_POINTER_ACTION: "click"},
        )

        #
        # move
        #
        for direction in ["x", "y"]:
            preset.AddEntry(
                name=f"How much moving in {direction}-direction",
                key=CONFIG_KEY_POINTER_DX
                if direction == "x"
                else CONFIG_KEY_POINTER_DY,
                mandatory=True,
                question_type="integer",
                display_if_key_value={CONFIG_KEY_POINTER_ACTION: "move"},
            )
        #
        # scroll
        #
        for direction in ["x", "y"]:
            preset.AddEntry(
                name=f"How much scrolling in {direction}-direction",
                key=CONFIG_KEY_POINTER_DY
                if direction == "y"
                else CONFIG_KEY_POINTER_DX,
                mandatory=True,
                question_type="integer",
                display_if_key_value={CONFIG_KEY_POINTER_ACTION: "scroll"},
            )

        #
        # window domain
        #
        preset.AddEntry(
            name="Select topleve action",
            key=CONFIG_KEY_TOPLEVEL_ACTION,
            mandatory=True,
            question_type="select",
            choices=TOPLEVEL_ACTIONS,
            display_if_key_value={CONFIG_KEY_DOMAIN: "toplevel"},
        )
        preset.AddEntry(
            name="Matchspec app_id?",
            key=CONFIG_KEY_TOPLEVEL_APP_ID,
            question_type="text",
            display_if_key_value={CONFIG_KEY_DOMAIN: "toplevel"},
        )
        preset.AddEntry(
            name="Matchspec title?",
            key=CONFIG_KEY_TOPLEVEL_TITLE,
            question_type="text",
            display_if_key_value={CONFIG_KEY_DOMAIN: "toplevel"},
        )
        preset.AddEntry(
            name="Matchspec state",
            key=CONFIG_KEY_TOPLEVEL_STATE,
            question_type="select",
            choices=TOPLEVEL_STATE_CHOICES,
            display_if_key_value={CONFIG_KEY_DOMAIN: "toplevel"},
        )

        #
        # output domain
        #
        preset.AddEntry(
            name="Select output action",
            key=CONFIG_KEY_TOPLEVEL_ACTION,
            mandatory=True,
            question_type="select",
            choices=OUTPUT_ACTIONS,
            display_if_key_value={CONFIG_KEY_DOMAIN: "output"},
        )

        return preset

    @classmethod
    def CheckSystemSupport(cls):
        if OsD.IsLinux():
            pass
        else:
            raise NotImplementedError("Wlrctl is only supported on Linux")