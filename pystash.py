import base64
import os
import sys
from dataclasses import asdict, dataclass

from cefpython3 import cefpython as cef
from jinja2 import Environment, FileSystemLoader, select_autoescape

# class AppHandler:
#     def OnAfterCreated(self, browser, *args, **kwargs):
#         """Called after a new browser is created."""
#         # Errors here will be intercepted in DisplayHandler.OnConsoleMessage.
#         print("GlobalHandler.OnAfterCreated", args, kwargs)


class BrowserHandler:
    def OnLoadingStateChange(self, browser, is_loading, *args, **kwargs):
        """Called when the loading state has changed."""
        if not is_loading:
            browser.ExecuteFunction(
                "js.set_item_list",
                [
                    {"id": 1, "name": 1},
                    {"id": 2, "name": 2},
                    {"id": 3, "name": 3},
                    {"id": 4, "name": 4},
                ],
            )


# BrowserSettings = {"universal_access_from_file_urls_allowed": True}


class App:
    def __init__(self):
        sys.excepthook = cef.ExceptHook
        env = Environment(
            loader=FileSystemLoader("templates"), autoescape=select_autoescape(["html"])
        )
        cef.Initialize(
            settings={
                "command_line_args_disabled": True,
                "downloads_enabled": False,
                "user_agent": "PyStash/0.0.1",
                "context_menu": {
                    "enabled": True,
                    "navigation": False,
                    "print": False,
                    "view_source": False,
                    "external_browser": False,
                    # "devtools": False,
                },
            }
        )
        # cef.SetGlobalClientHandler(AppHandler())

        browser = cef.CreateBrowserSync(
            # url=cef.GetDataUrl(env.get_template("test.html").render(test="hi")),
            url=os.path.join(os.path.dirname(os.path.realpath(__file__)), "public/index.html"),
            window_title="PyStash",
            # settings=BrowserSettings,
        )
        browser.SetClientHandler(BrowserHandler())

        bindings = cef.JavascriptBindings()
        bindings.SetObject("py", self)
        browser.SetJavascriptBindings(bindings)

        self.browser = browser

        cef.MessageLoop()
        cef.Shutdown()


if __name__ == "__main__":
    App()
