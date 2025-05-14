### `src/methods.py`
### Various methods for the Dateiablage application
### Open-Source, hosted on https://github.com/DrBenjamin/Dateiablage
### Please reach out to ben@seriousbenentertainment.org for any questions
## Modules
import wx
import webbrowser
import src.globals as g
from docx import Document
from src.files import list_files
from src.learning import display_learning

# Method to handle the right click event
def on_right_click(self, event):
    # Creating the context menu
    menu = wx.Menu()
    open_item = menu.Append(wx.ID_ANY, "Öffnen")
    copy_path = menu.Append(wx.ID_ANY, "Kopiere Pfad")
    convert_item = menu.Append(wx.ID_ANY, "Konvertiere srt in vtt")

    # Binding handlers
    self.Bind(wx.EVT_MENU, self.on_file_activated, open_item)
    self.Bind(wx.EVT_MENU, self.on_copy_path, copy_path)
    self.Bind(wx.EVT_MENU, self.on_convert, convert_item)

    # Showing the menu
    self.PopupMenu(menu, event.GetPosition())
    menu.Destroy()

# Method to handle the Copy Path menu item
def on_copy_path(self, event):
    if g.file_path is not None:
        minio_endpoint = g.minio_endpoint
        if not minio_endpoint.startswith("http"):
            minio_endpoint = "http://" + minio_endpoint

        # Removing trailing slash if present
        minio_endpoint = minio_endpoint.rstrip("/")
        bucket = g.minio_bucket_name
        object_name = g.file_path.lstrip("/")
        url = f"{minio_endpoint}/{bucket}/{object_name}"
        wx.TheClipboard.Open()
        wx.TheClipboard.SetData(wx.TextDataObject(url))
        wx.TheClipboard.Close()
    else:
        wx.MessageBox("Keine Datei ausgewählt", "Error", wx.OK | wx.ICON_ERROR)

# Method to handle `Über die App` menu item
def on_about(self, event):
    # Creating a new user-defined window
    frame = wx.Frame(None, title="Über die App", size=(400, 550))
    panel = wx.Panel(frame)
    sizer = wx.BoxSizer(wx.VERTICAL)

    # Adding message
    message = (
        "Name der Anwendung:\n"
        "Dateiablage\n\n"
    )
    message_label = wx.StaticText(panel, label = message)
    sizer.Add(message_label, 0, wx.ALL, 10)

    # Adding logo
    #logo = wx.Bitmap("_internal/images/logo.png", wx.BITMAP_TYPE_PNG)
    #logo_image = wx.StaticBitmap(panel, bitmap=logo)
    #sizer.Add(logo_image, 0, wx.ALL, 10)

    # Adding 2nd message
    message2 = (
        "Versionsnummer:\n"
        "0.2.0 (build 2025-05-14)\n\n"
        "**** Beschreibung ****\n"
        "Die Dateiablage ist eine Anwendung zur unkomplizierten Verwaltung von "
        "e-Learning-Inhalten.\n\n"
        "**** Support ****\n"
        "Bei Fragen oder technischen Problemen kontaktieren Sie bitte unseren Support.\n\n"
    )
    message_label2 = wx.StaticText(panel, label = message2)
    sizer.Add(message_label2, 0, wx.ALL, 10)

    # Adding web link to support page
    support_label = wx.StaticText(panel, label="Weitere Informationen finden Sie auf unserer Support-Seite.")
    support_label.SetForegroundColour((0, 0, 255))  # Link-Farbe (Blau)
    font = support_label.GetFont()
    font.SetUnderlined(True)  # Unterstrichen hinzufügen
    support_label.SetFont(font)

    # Adding click event for the link
    support_label.Bind(wx.EVT_LEFT_DOWN, lambda event: webbrowser.open("https://www.seriousbenentertainment.org"))
    sizer.Add(support_label, 0, wx.ALL, 10)

    # Adding message
    thanks_label = wx.StaticText(panel, label="Vielen Dank, dass Sie unsere Anwendung verwenden!")
    thanks_label.SetForegroundColour((0, 128, 0))  # Grüne Farbe für Freundlichkeit
    sizer.Add(thanks_label, 0, wx.ALL, 10)

    # Setting sizer and display window
    panel.SetSizer(sizer)
    frame.Show()

# Method to handle the Contact menu item
def on_contact(self, event):
    mailto_link = "mailto:ben@seriousbenentertainment.org?subject=Supportanfrage&body=Hallo%20Support-Team"
    wx.LaunchDefaultBrowser(mailto_link)

# Method to handle the Refresh menu item
def on_refresh(self, event):
    # Clearing the ctrl lists
    self.learning_ctrl.DeleteAllItems()
    self.tasks_ctrl.DeleteAllItems()

    # Refreshing the ctrl lists
    try:
        if g.folder_path is not None:
            list_files(self, g.folder_path)
    except Exception as e:
        print(f"Error: {e}")
    try:
        if g.df_elearning is not None:
            display_learning(self, g.df_elearning)
    except Exception as e:
        print(f"Error: {e}")
    try:
        if g.df_tasks is not None:
            on_import_tasks(self, None)
    except Exception as e:
        print(f"Error: {e}")

# Method to handle the Exit menu item
def on_exit(self, event):
    self.Close(True)
