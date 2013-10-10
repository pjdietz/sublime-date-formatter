import sublime
import sublime_plugin

from datetime import datetime
import os
import subprocess

SETTINGS_FILE = "Date Formatter.sublime-settings"

if int(sublime.version()) > 3000:
    PACKAGE_DIRECTORY = __name__.split('.')[0]
else:
    PACKAGE_DIRECTORY = os.path.basename(os.getcwd())


class FormatDateCommand(sublime_plugin.WindowCommand):

    def __init__(self, *args, **kwargs):
        sublime_plugin.WindowCommand.__init__(self, *args, **kwargs)
        self.format = None
        self.formats = None
        self.settings = None

    def run(self):
        self.format = None
        self.settings = sublime.load_settings(SETTINGS_FILE)

        # Read the formats from settings. Normalize to [[format, description],]
        self.formats = self.settings.get("formats", [])
        for i in range(len(self.formats)):
            format = self.formats[i]
            if isinstance(format, str):
                self.formats[i] = [format,format]

        self.format_dates()

    def format_dates(self):

        # Check if the user selected a format already.
        # If not, abort the function and open the menu.
        if not self.format:
            self.select_format()
            return

        # Read the text of each selection into a list.
        dates = []
        view = self.window.active_view()
        for region in view.sel():
            dates.append(view.substr(region))

        # Use the PHP script to generate a list of all the selected dates
        # formatted using the user's selected format.
        args = [
            self.settings.get("php"),
            os.path.join(sublime.packages_path(), PACKAGE_DIRECTORY, 'format_dates.php'),
            self.format,
        ]
        args += dates
        proc = subprocess.Popen(args, stdout=subprocess.PIPE)
        output = proc.communicate()[0]
        returncode = proc.returncode

        if (returncode != 0):
            print("ERROR!")
            return

        # Update the selections with the formatted dates.
        dates = output.decode("ascii").split("\n")
        view.run_command("replace_dates", {"dates": dates})

    def select_format(self):

        # Read the first selected item.
        view = self.window.active_view()
        region = view.sel()[0]
        source = view.substr(region)
        if not source:
            source = "now"

        # Use the PHP script to generate a list of all the user's formats.
        args = [
            self.settings.get("php"),
            os.path.join(sublime.packages_path(), PACKAGE_DIRECTORY, 'format_date.php'),
            source,
        ]
        args += [format[0] for format in self.formats]
        print(args)
        proc = subprocess.Popen(args, stdout=subprocess.PIPE)
        output = proc.communicate()[0]
        returncode = proc.returncode

        if (returncode != 0):
            print("ERROR!")
            return

        # Display a list of the formats.
        formatted = output.decode("ascii").split("\n")
        menu_items = []
        for i in range(len(self.formats)):
            label = self.formats[i][1]
            sample = formatted[i]
            menu_items.append([label, sample])

        self.window.show_quick_panel(menu_items, self.on_select_format)

    def on_select_format(self, index):
        self.format = self.formats[index][0]
        self.format_dates()

class ReplaceDatesCommand(sublime_plugin.TextCommand):
    def run(self, edit, dates=None):
        regions = self.view.sel()
        if dates and len(dates) >= len(regions):
            for i in range(len(regions)):
                self.view.replace(edit, regions[i], dates[i])


"""
2013-09-01
9/1/2013
10/08/2013
yesterday
tomorrow

2013-09-01
9/1/2013
today
yesterday
tomorrow

"""
