### `BenBox.py`
### Main Phoenix application
### Open-Source, hosted on https://github.com/DrBenjamin/BenBox
### Please reach out to ben@seriousbenentertainment.org for any questions
# Modules
import wx  # wxPython / Phoenix
import src.globals as g
import types
import logging
from src.preferences import on_preferences
from src.files import (
    on_file_selected,
    on_file_activated,
    on_delete_file
)
from src.learning import (
    on_create_bucket,
    on_remove_bucket,
    on_elearning_item_selected,
    on_elearning_item_activated,
    on_upload_file_to_minio
)
from src.methods import (
    on_right_click,
    on_copy_path,
    on_about,
    on_contact,
    on_exit,
    load_streamlit_webview,
    refresh_ctrls,
    on_learning_ctrl_selected
)
HAS_WEBVIEW2 = False
try:
    import wx.html2
    HAS_WEBVIEW2 = True
except (ImportError, AttributeError):
    HAS_WEBVIEW2 = False

logger = logging.getLogger(__name__)

# Method to handle the Preferences menu item


def on_preferences_open(self, event):
    # Calling the `on_preferences` method
    self.on_preferences(event)

# Creating the main frame
class MyFrame(wx.Frame):
    def __init__(self, parent, title, size, config):
        super(MyFrame, self).__init__(parent=parent, title=title, size=size)
        self.config = config

        # Setting HAS_WEBVIEW2 as an instance attribute for handler access
        self.HAS_WEBVIEW2 = HAS_WEBVIEW2

        # Binding of methods from this file
        # Binding function as method to `self`
        self.on_preferences_open = types.MethodType(on_preferences_open, self)

        # Binding functions from other files as methods to `self`
        # Methods from `methods.py`
        self.on_right_click = types.MethodType(on_right_click, self)
        self.on_copy_path = types.MethodType(on_copy_path, self)
        self.on_about = types.MethodType(on_about, self)
        self.on_contact = types.MethodType(on_contact, self)
        self.on_exit = types.MethodType(on_exit, self)
        self.refresh_ctrls = types.MethodType(refresh_ctrls, self)

        # Methods from `learning.py`
        self.on_elearning_item_selected = types.MethodType(
            on_elearning_item_selected, self)
        self.on_elearning_item_activated = types.MethodType(
            on_elearning_item_activated, self)
        self.on_upload_file_to_minio = types.MethodType(
            on_upload_file_to_minio, self)  # Binding upload method
        self.on_remove_bucket = types.MethodType(
            on_remove_bucket, self)  # Binding remove bucket method

        # Methods from `files.py`
        self.on_file_selected = types.MethodType(on_file_selected, self)
        self.on_file_activated = types.MethodType(on_file_activated, self)
        self.on_delete_file = types.MethodType(on_delete_file, self)

        # Adding multi-selection handler as method
        self.on_learning_ctrl_selected = types.MethodType(
            on_learning_ctrl_selected, self)

        # Method from `preferences.py`
        self.on_preferences = types.MethodType(on_preferences, self)

        # Method from `minio_utils.py`
        self.on_create_bucket = types.MethodType(on_create_bucket, self)

        # Creating a menu bar
        menu_bar = wx.MenuBar()

        # Creating the `Datei` menu
        file_menu = wx.Menu()
        create_bucket_item = file_menu.Append(wx.ID_ANY, "Neuen Bucket erstellen")
        file_menu.AppendSeparator()
        upload_file_minio = file_menu.Append(wx.ID_ANY, "Datei(en) hochladen")
        exit_app = file_menu.Append(wx.ID_EXIT, "&Beenden")
        menu_bar.Append(file_menu, "&Datei")

        # Creating the `Bearbeiten` menu
        edit_menu = wx.Menu()
        remove_bucket_item = edit_menu.Append(wx.ID_ANY, "Bucket löschen")
        edit_menu.AppendSeparator()
        copy_path = edit_menu.Append(wx.ID_ANY, "Kopiere Pfad")
        delete_file_item = edit_menu.Append(wx.ID_ANY, "Datei löschen")
        edit_menu.AppendSeparator()
        preferences = edit_menu.Append(wx.ID_PREFERENCES, "Einstellungen")
        menu_bar.Append(edit_menu, "&Bearbeiten")

        # Creating the `Hilfe` menu
        help_menu = wx.Menu()
        help_contact = help_menu.Append(wx.ID_ANY, "&Kontakt")
        help_about = help_menu.Append(wx.ID_ANY, "&Über die App")
        menu_bar.Append(help_menu, "&Hilfe")

        # Setting the menu bar
        self.SetMenuBar(menu_bar)
        font = wx.Font(
            12,
            wx.FONTFAMILY_DEFAULT,
            wx.FONTSTYLE_NORMAL,
            wx.FONTWEIGHT_BOLD
        )
        try:
            menu_bar.SetFont(font)
        except Exception as e:
            print(e)

        # Creating a panel
        self.panel = wx.Panel(self)

        # Creating a vertical box sizer
        vbox_learning = wx.BoxSizer(wx.VERTICAL)
        vbox_tasks = wx.BoxSizer(wx.VERTICAL)

        # Creating the learning_ctrl with multi-selection enabled
        self.learning_ctrl = wx.ListCtrl(
            self.panel,
            style=wx.LC_LIST
            | wx.BORDER_SUNKEN
            | wx.LIST_ALIGN_SNAP_TO_GRID
        )

        # Creating the tasks_ctrl depending on WebView availability
        if HAS_WEBVIEW2:
            try:
                # Creating wx.html2.WebView for supported platforms
                self.tasks_ctrl = wx.html2.WebView.New(self.panel)

                # Using the helper to load the Streamlit webview with the current bucket
                load_streamlit_webview(self.tasks_ctrl, [g.minio_bucket_name])

                # Adding event handler to scroll to bottom after page load
                self.tasks_ctrl.Bind(
                    wx.html2.EVT_WEBVIEW_LOADED,
                    self.on_tasks_webview_loaded
                )
            except NotImplementedError:
                # Fallback to wx.ListCtrl if WebView is not implemented
                self.tasks_ctrl = wx.ListCtrl(
                    self.panel,
                    style=wx.LC_REPORT
                    | wx.BORDER_SUNKEN
                    | wx.LIST_ALIGN_SNAP_TO_GRID
                )
                self.tasks_ctrl.InsertColumn(0, "Hinweis")
                self.tasks_ctrl.InsertItem(
                    0, "WebView nicht verfügbar. Aufgabenanzeige deaktiviert.")
        else:
            # Creating a wx.ListCtrl if WebView is not available
            self.tasks_ctrl = wx.ListCtrl(
                self.panel,
                style=wx.LC_REPORT
                | wx.BORDER_SUNKEN
                | wx.LIST_ALIGN_SNAP_TO_GRID
            )
            # Adding a column and a message for unsupported platform
            self.tasks_ctrl.InsertColumn(0, "Hinweis")
            self.tasks_ctrl.InsertItem(
                0, "WebView nicht verfügbar. Aufgabenanzeige deaktiviert.")

        self.file_listbox = wx.ListBox(self.panel)

        # Adding titles for the controls
        learning_title = wx.StaticText(
            self.panel,
            label="Buckets",
            style=wx.ALIGN_LEFT
        )
        task_title = wx.StaticText(
            self.panel,
            label="Agents",
            style=wx.ALIGN_RIGHT
        )
        explorer_title = wx.StaticText(
            self.panel,
            label="Dateien",
            style=wx.ALIGN_LEFT
        )

        # Setting font style
        learning_title.SetFont(wx.Font(wx.FontInfo(11).Bold()))
        task_title.SetFont(wx.Font(wx.FontInfo(11).Bold()))
        explorer_title.SetFont(wx.Font(wx.FontInfo(11).Bold()))

        # Changing the text
        explorer_title.SetForegroundColour(wx.Colour(0, 51, 102))

        # Creating a horizontal box sizer
        hbox = wx.BoxSizer(wx.HORIZONTAL)

        # Adding the list controls to the horizontal box sizer
        vbox_learning.Add(learning_title, 0, wx.ALL | wx.LEFT, 5)
        vbox_learning.Add(self.learning_ctrl, 1, wx.ALL | wx.EXPAND, 5)
        vbox_tasks.Add(task_title, 0, wx.ALL | wx.RIGHT, 5)
        vbox_tasks.Add(self.tasks_ctrl, 1, wx.ALL | wx.EXPAND, 5)
        hbox.Add(vbox_learning, 1, wx.EXPAND)
        hbox.Add(vbox_tasks, 1, wx.EXPAND)

        # Creating a vertical box sizer
        vbox = wx.BoxSizer(wx.VERTICAL)

        # Adding the horizontal box sizer and the file listbox to the vertical box sizer
        vbox.Add(hbox, 1, wx.ALL | wx.EXPAND, 5)
        vbox.Add(explorer_title, 0, wx.ALL | wx.LEFT, 5)
        vbox.Add(self.file_listbox, 1, wx.ALL | wx.EXPAND, 5)

        # Setting the sizer for the frame and fit the panel
        self.panel.SetSizer(vbox)

        # Refreshing and displaying the learning_ctrl list at startup
        self.refresh_ctrls()

        # Listing files in the pre-selected bucket(s)/stage(s) on initial load
        self.on_learning_ctrl_selected(None)

        # Bindings of events
        # Updating the binding to use the multi-selection handler
        self.learning_ctrl.Bind(wx.EVT_LIST_ITEM_SELECTED,
                                self.on_learning_ctrl_selected)
        self.learning_ctrl.Bind(
            wx.EVT_LIST_ITEM_ACTIVATED, self.on_elearning_item_activated)
        # Binding the list control to the on_file_selected method
        self.file_listbox.Bind(wx.EVT_LISTBOX, self.on_file_selected)
        # Binding the list control to the on_file_activated method
        self.file_listbox.Bind(wx.EVT_LISTBOX_DCLICK, self.on_file_activated)

        # Binding of `Datei` methods to menu items
        # Binding the MinIO upload menu item to the upload handler
        self.Bind(wx.EVT_MENU, self.on_upload_file_to_minio, upload_file_minio)
        # Binding the create bucket menu item to the handler
        self.Bind(wx.EVT_MENU, self.on_create_bucket, create_bucket_item)
        # Binding the remove bucket menu item to the handler
        self.Bind(wx.EVT_MENU, self.on_remove_bucket, remove_bucket_item)
        # Binding the Exit menu item to the on_exit method
        self.Bind(wx.EVT_MENU, self.on_exit, exit_app)

        # Binding of `Bearbeiten` methods to menu items
        # Binding the Copy menu to the `on_copy` path method
        self.Bind(wx.EVT_MENU, self.on_copy_path, copy_path)
        # Binding the Delete file menu item to the delete handler
        self.Bind(wx.EVT_MENU, self.on_delete_file, delete_file_item)
        # Binding the Preferences menu item to the on_preferences method
        self.Bind(wx.EVT_MENU, self.on_preferences_open, preferences)

        # Binding of `Hilfemenü` methods to menu items
        # Binding the Contact menu to the on_contact method
        self.Bind(wx.EVT_MENU, self.on_contact, help_contact)
        # Binding the über die App menu to the on_about method
        self.Bind(wx.EVT_MENU, self.on_about, help_about)

        # Binding the right-click event
        self.file_listbox.Bind(wx.EVT_CONTEXT_MENU, self.on_right_click)

    # Adding the on_tasks_webview_loaded method as a class method
    def on_tasks_webview_loaded(self, event):
        """
        Scrolling the WebView to the bottom after content is loaded.
        """
        js_scroll_bottom = """
            window.scrollTo(0, document.body.scrollHeight);
            if (document.scrollingElement) {
                document.scrollingElement.scrollTop = document.scrollingElement.scrollHeight;
            }
        """
        self.tasks_ctrl.RunScript(js_scroll_bottom)

# Creating the wx App
class MyApp(wx.App):
    def OnInit(self):
        # Initializing config
        self.config = wx.Config("BenBox")

        # Setting default values if they do not exist
        if not self.config.HasEntry("user_choice"):
            self.config.Write("user_choice", "Alle")
        if not self.config.HasEntry("xml_import_enabled"):
            self.config.WriteBool("xml_import_enabled", True)
        if not self.config.HasEntry("xml_import_one_file"):
            self.config.WriteBool("xml_import_one_file", True)
        if not self.config.HasEntry("srt_converter_overwrite"):
            self.config.WriteBool("srt_converter_overwrite", False)
        if not self.config.HasEntry("drive_mapping_enabled"):
            self.config.WriteBool("drive_mapping_enabled", False)
        if not self.config.HasEntry("drive_mapping_letter"):
            self.config.Write("drive_mapping_letter", "")
        if not self.config.HasEntry("date_today"):
            self.config.WriteBool("date_today", False)

        # Adding os specific settings
        if not wx.Platform == "__WXMSW__":
            self.config.WriteBool("drive_mapping_enabled", False)
            self.config.Write("drive_mapping_letter", "")

        # Creating the frame
        frame = MyFrame(None, title="BenBox",
                        size=(1024, 768),
                        config=self.config)

        # Setting icon
        frame.Show(True)
        if wx.Platform == "__WXMAC__":
            frame.SetIcon(
                wx.Icon("_internal/images/icon.icns", wx.BITMAP_TYPE_ICON))
        # Removing icon setting on Linux (__WXGTK__)
        # else:
        #     frame.SetIcon(wx.Icon("_internal/images/icon.ico", wx.BITMAP_TYPE_ICO))

        self.SetTopWindow(frame)
        return True

# Initializing the wx App
app = MyApp(False)
print("App start")
app.MainLoop()
