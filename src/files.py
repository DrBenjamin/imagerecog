### `src/files.py`
### Files Panel for the Dateiablage application
### Open-Source, hosted on https://github.com/DrBenjamin/Dateiablage
### Please reach out to ben@seriousbenentertainment.org for any questions
## Modules
import wx
import os
import subprocess
import platform
import xml.etree.ElementTree as ET
import src.globals as g
from minio.error import S3Error
from io import BytesIO

from src.minio_utils import connect_to_minio

# Method to list objects in a bucket
def list_objects(minio_client, bucket_name):
    bucket_name = bucket_name.lower().replace(' ', '-')
    try:
        objects = minio_client.list_objects(bucket_name, recursive=True)
        return [
            obj.object_name
            for obj in objects
        ]
    except S3Error as e:
        wx.MessageBox(
            f"Fehler beim auflisten der MinIO-Dateien: {e}", "Fehler", wx.OK | wx.ICON_ERROR)
    return

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
            for file_path in file_paths:
                file_name = os.path.basename(file_path)
                with open(file_path, "rb") as f:
                    file_data = f.read()
                    minio_client.put_object(
                        bucket_name,
                        file_name,
                        BytesIO(file_data),
                        len(file_data)
                    )
            wx.MessageBox(f"{len(file_paths)} Datei(en) erfolgreich in den Bucket '{bucket_name}' hochgeladen.", "Upload abgeschlossen", wx.OK | wx.ICON_INFORMATION)

            # Refreshing file list and restoring bucket selection
            from src.files import refresh_files_ctrl_with_minio
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

# Method to upload files to MinIO bucket
def upload_files(minio_client, bucket_name, files):
    bucket_name = bucket_name.lower().replace(' ', '-')
    for file in files:
        # Reading file
        file_content = file.read()

        # Uploading to MinIO
        minio_client.put_object(
            bucket_name,
            file.name,
            BytesIO(file_content),
            len(file_content)
        )

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
            minio_client.remove_object(bucket_name, object_name)
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
        bucket_name = g.minio_bucket_name
        object_name = g.file_path
        response = minio_client.get_object(bucket_name, object_name)
        # Save to a temporary file
        import tempfile
        import shutil
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