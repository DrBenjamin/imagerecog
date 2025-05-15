### `src/files.py`
### Files Panel for the Dateiablage application
### Open-Source, hosted on https://github.com/DrBenjamin/BenBox
### Please reach out to ben@seriousbenentertainment.org for any questions
## Modules
import wx
import os
import tempfile
import shutil
import subprocess
import platform
import src.globals as g
from minio.error import S3Error
from io import BytesIO
from src.minio_utils import (
    connect_to_minio,
    list_objects
)

# Method to upload file
def on_upload_file(self, event):
    wildcard = "Alle Dateien (*.*)|*.*" 
    dialog = wx.FileDialog(self, "Bitte wählen Sie eine oder mehrere Datei(en) aus:",
        wildcard=wildcard,
        style=wx.FD_OPEN | wx.FD_MULTIPLE
    )
    if dialog.ShowModal() == wx.ID_OK:
        file_paths = dialog.GetPaths()
        dialog.Destroy()

        # Upload to selected bucket
        minio_client = connect_to_minio()
        if minio_client is None:
            wx.MessageBox("MinIO-Verbindung konnte nicht hergestellt werden.", "Fehler", wx.OK | wx.ICON_ERROR)
            return
        bucket_name = g.minio_bucket_name
        if not bucket_name:
            wx.MessageBox("Kein Bucket ausgewählt.", "Fehler", wx.OK | wx.ICON_ERROR)
            return
        try:
            # Using the helper from minio_utils
            from src.minio_utils import upload_files
            upload_files(minio_client, bucket_name, file_paths)
            wx.MessageBox(f"{len(file_paths)} Datei(en) erfolgreich in den Bucket '{bucket_name}' hochgeladen.", "Upload abgeschlossen", wx.OK | wx.ICON_INFORMATION)

            # Refreshing file list and restoring bucket selection
            refresh_files_ctrl_with_minio(self)

            # Restoring bucket selection in learning_ctrl if available
            if hasattr(self, "learning_ctrl"):
                for idx in range(self.learning_ctrl.GetItemCount()):
                    display_name = self.learning_ctrl.GetItemText(idx, 0)
                    if display_name.replace(' ', '-').lower() == bucket_name:
                        self.learning_ctrl.Select(idx)
                        self.learning_ctrl.EnsureVisible(idx)
                        g.elearning_index = idx
                        break
        except Exception as e:
            wx.MessageBox(f"Fehler beim Hochladen zu MinIO: {e}", "Fehler", wx.OK | wx.ICON_ERROR)
    else:
        dialog.Destroy()



# Method to delete the selected file (object) from the selected MinIO bucket
def on_delete_file(self, event):
    bucket_name = g.minio_bucket_name
    object_name = g.file_path
    if not bucket_name or not object_name:
        wx.MessageBox("Kein Bucket oder keine Datei ausgewählt.", "Fehler", wx.OK | wx.ICON_ERROR)
        return
    dlg = wx.MessageDialog(self, f"Soll die Datei '{object_name}' wirklich gelöscht werden?", "Datei löschen", wx.YES_NO | wx.ICON_WARNING)
    if dlg.ShowModal() == wx.ID_YES:
        try:
            minio_client = connect_to_minio()
            if minio_client is None:
                wx.MessageBox("MinIO-Verbindung konnte nicht hergestellt werden.", "Fehler", wx.OK | wx.ICON_ERROR)
                return
            minio_client.remove_object(bucket_name.lower().replace(' ', '-'), object_name)
            wx.MessageBox(f"Datei '{object_name}' wurde gelöscht.", "Erfolg", wx.OK | wx.ICON_INFORMATION)

            # Refreshing file list
            from src.files import refresh_files_ctrl_with_minio
            refresh_files_ctrl_with_minio(self)
        except Exception as e:
            wx.MessageBox(f"Fehler beim Löschen der Datei: {e}", "Fehler", wx.OK | wx.ICON_ERROR)
    dlg.Destroy()

# Method to handle selected file
def on_file_selected(self, event):
    file_index = event.GetSelection()
    file_path = self.file_listbox.GetString(file_index)
    g.file_path = file_path

# Method to handle the list control item activated event
def on_file_activated(self, event):
    # Downloading the file from MinIO to a buffer and open it with the default application
    try:
        minio_client = connect_to_minio()
        if minio_client is None:
            wx.MessageBox("MinIO-Verbindung konnte nicht hergestellt werden.", "Fehler", wx.OK | wx.ICON_ERROR)
            return

        # Handling multi-selection: g.minio_bucket_name may be a list
        bucket_name = g.minio_bucket_name
        object_name = g.file_path

        # If bucket_name is a list, extract from file_path prefix
        if isinstance(bucket_name, list):
            # Expecting file_path in format "bucket/file"
            if "/" in object_name:
                bucket_name, object_name = object_name.split("/", 1)
            else:
                wx.MessageBox("Dateipfad ungültig für Multi-Bucket-Auswahl.", "Fehler", wx.OK | wx.ICON_ERROR)
                return

        # Ensuring bucket_name is valid (MinIO expects lowercase, hyphenated)
        bucket_name = bucket_name.lower().replace(' ', '-')

        # Avoiding double prefix in object_name (e.g. test/test/file.pdf)
        if object_name.startswith(f"{bucket_name}/"):
            object_name = object_name[len(bucket_name) + 1 :]

        # Getting the object from MinIO
        try:
            response = minio_client.get_object(bucket_name, object_name)
        except S3Error as e:
            wx.MessageBox(
                f"Datei konnte nicht geöffnet oder heruntergeladen werden: {e}\n\nbucket_name: {bucket_name}, object_name: {object_name}",
                "Error", wx.OK | wx.ICON_ERROR
            )
            return

        # Saving to a temporary file
        suffix = os.path.splitext(object_name)[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
            shutil.copyfileobj(response, tmp_file)
            tmp_file_path = tmp_file.name
        response.close()
        response.release_conn()

        # Opening the file with the default application
        if platform.system() == "Windows":
            os.startfile(tmp_file_path)
        elif platform.system() == "Darwin":  # macOS
            subprocess.call(["open", tmp_file_path])
        else:  # Linux
            subprocess.call(["xdg-open", tmp_file_path])
    except Exception as e:
        wx.MessageBox(f"Datei konnte nicht geöffnet oder heruntergeladen werden: {e}", "Error", wx.OK | wx.ICON_ERROR)

# Method to list the files in the selected folder
def list_files(self, list_files):
    # Clearing the existing file list
    g.file_list = list_files

    # Displaying in the File Explorer
    self.file_listbox.Set(g.file_list)

# Method to refresh and display MinIO bucket files in the learning_ctrl
def refresh_files_ctrl_with_minio(self):
    try:
        # Checking for empty endpoint and bucket_name
        if not g.minio_endpoint:
            wx.MessageBox(
                "MinIO-Endpunkt ist nicht gesetzt. Bitte tragen Sie einen gültigen Wert in der Konfiguration ein.",
                "Fehler",
                wx.OK | wx.ICON_ERROR
            )
            return
        if not g.minio_bucket_name:
            wx.MessageBox(
                "MinIO-Bucket ist nicht gesetzt. Bitte prüfen Sie die Konfiguration.",
                "Fehler",
                wx.OK | wx.ICON_ERROR
            )
            return

        # Connecting to MinIO and listing objects
        minio_client = connect_to_minio()
        if minio_client is None:
            wx.MessageBox(
                "MinIO-Verbindung konnte nicht hergestellt werden.",
                "Fehler",
                wx.OK | wx.ICON_ERROR
            )
            return

        # Listing objects from the selected bucket (g.minio_bucket_name)
        files = list_objects(minio_client, g.minio_bucket_name)
        if files is None:
            files = []
        list_files(self, files)

    except Exception as e:
        wx.MessageBox(
            f"Fehler beim Laden der MinIO-Dateien: {e}", "Fehler", wx.OK | wx.ICON_ERROR)

# Adding a helper to handle multi-selection and update files/webview
def on_learning_ctrl_selected(self, event):
    """
    Handling multi-selection in the learning_ctrl to show files from several buckets.
    Always refreshes file list and reloads the webview with the selected buckets.
    """
    # Getting all selected bucket indexes
    selected_indexes = []
    idx = self.learning_ctrl.GetFirstSelected()
    while idx != -1:
        selected_indexes.append(idx)
        idx = self.learning_ctrl.GetNextSelected(idx)

    # Getting all selected bucket names (MinIO style)
    selected_buckets = [
        self.learning_ctrl.GetItemText(i, 0).replace(' ', '-').lower()
        for i in selected_indexes
    ]

    # Setting global state for single or multi selection
    if len(selected_buckets) == 1:
        g.minio_bucket_name = selected_buckets[0]
        g.elearning_index = selected_indexes[0]
    else:
        g.minio_bucket_name = selected_buckets
        g.elearning_index = selected_indexes[0] if selected_indexes else 0

    # Updating the file list to show all files from all selected buckets
    files_combined = []
    minio_client = None
    try:
        from src.minio_utils import connect_to_minio
        minio_client = connect_to_minio()
    except Exception:
        pass
    if minio_client:
        from src.files import list_objects
        for bucket in selected_buckets:
            try:
                files = list_objects(minio_client, bucket)
                if files:
                    # Prefix files with bucket name for clarity
                    files_combined.extend([f"{bucket}/{f}" for f in files])
            except Exception:
                continue

    # Setting and displaying combined files in the file_listbox
    g.file_list = files_combined
    self.file_listbox.Set(g.file_list)

    # Reloading the webview with the actual buckets query
    if hasattr(self, "tasks_ctrl") and hasattr(self, "HAS_WEBVIEW2") and self.HAS_WEBVIEW2:
        try:
            # Using the helper to load the Streamlit webview with the selected buckets
            from src.methods import load_streamlit_webview
            load_streamlit_webview(self.tasks_ctrl, selected_buckets)
        except Exception:
            pass