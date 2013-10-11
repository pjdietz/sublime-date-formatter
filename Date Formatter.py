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

# Find the stirng class. (str for py3, basestring for py2)
string_class = str
try:
    # If Python 2, use basestring instead of str
    # noinspection PyStatementEffect
    basestring
    string_class = basestring
except NameError:
    pass


def show_php_error():
    message = "Unable to execute PHP script.\n\n" \
              "Make sure PHP is installed properly on your system " \
              "that the correct path to php is set in the settings " \
              "for this package."
    sublime.error_message(message)


class FormatDateCommand(sublime_plugin.WindowCommand):

    def __init__(self, *args, **kwargs):
        sublime_plugin.WindowCommand.__init__(self, *args, **kwargs)
        self.format = None
        self.formats = None
        self.settings = None

    def run(self, format=None):
        self.format = format
        self.settings = sublime.load_settings(SETTINGS_FILE)

        # Read the formats from settings. Normalize to [[format, description],]
        self.formats = self.settings.get("formats", [])
        for i in range(len(self.formats)):
            format = self.formats[i]
            if isinstance(format, string_class):
                self.formats[i] = [format, format]

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
            if region.empty():
                dates.append("now")
            else:
                dates.append(view.substr(region))

        # Use the PHP script to generate a list of all the selected dates
        # formatted using the user's selected format.
        args = [
            self.settings.get("php"),
            os.path.join(
                sublime.packages_path(),
                PACKAGE_DIRECTORY,
                'format_dates.php'),
            self.format,
        ]
        args += dates
        try:
            proc = subprocess.Popen(args, stdout=subprocess.PIPE)
        except OSError:
            show_php_error()
            return
        output = proc.communicate()[0]
        if (proc.returncode != 0):
            show_php_error()
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
            os.path.join(
                sublime.packages_path(),
                PACKAGE_DIRECTORY,
                'format_date.php'),
            source,
        ]
        args += [format[0] for format in self.formats]
        try:
            proc = subprocess.Popen(args, stdout=subprocess.PIPE)
        except OSError:
            show_php_error()
            return
        output = proc.communicate()[0]
        if (proc.returncode != 0):
            show_php_error()
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
