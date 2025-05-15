# `src/learning.py`
# Learning Panel for the Dateiablage application
### Open-Source, hosted on https://github.com/DrBenjamin/BenBox
### Please reach out to ben@seriousbenentertainment.org for any questions
# Modules
import wx
import os
import src.globals as g
from minio.error import S3Error
from io import BytesIO
from src.minio_utils import (
    connect_to_minio,
    list_buckets,
    upload_files
)

# Method to create a new bucket
def on_create_bucket(self, event):
    dlg = wx.TextEntryDialog(self, "Bitte geben Sie den Namen für den neuen Bucket ein:", "Neuen Bucket erstellen")
    if dlg.ShowModal() == wx.ID_OK:
        new_bucket = dlg.GetValue().strip().lower()
        if new_bucket:
            import subprocess
            try:
                result = subprocess.run([
                    "mc", "mb", f"myminio/{new_bucket}"
                ], capture_output=True, text=True)
                if result.returncode == 0:
                    # Checking with mc ls if the bucket is present
                    check_result = subprocess.run([
                        "mc", "ls", f"myminio/{new_bucket}"
                    ], capture_output=True, text=True)
                    if check_result.returncode == 0:
                        # Setting anonymous download policy
                        anon_result = subprocess.run([
                            "mc", "anonymous", "set", "download", f"myminio/{new_bucket}"
                        ], capture_output=True, text=True)
                        if anon_result.returncode == 0:
                            wx.MessageBox(f"Bucket '{new_bucket}' wurde erfolgreich erstellt und für anonymen Download freigegeben.", "Erfolg", wx.OK | wx.ICON_INFORMATION)
                        else:
                            wx.MessageBox(f"Bucket wurde erstellt, aber anonyme Freigabe fehlgeschlagen: {anon_result.stderr}", "Warnung", wx.OK | wx.ICON_WARNING)

                        # Refreshing and selecting the new bucket
                        self.refresh_learning_ctrl_with_minio(select_bucket_name=new_bucket)
                    else:
                        wx.MessageBox(f"Bucket wurde scheinbar nicht erstellt (mc ls gibt Fehler): {check_result.stderr}", "Fehler", wx.OK | wx.ICON_ERROR)
                else:
                    wx.MessageBox(f"Fehler beim Erstellen des Buckets: {result.stderr}", "Fehler", wx.OK | wx.ICON_ERROR)
            except Exception as e:
                wx.MessageBox(f"Fehler beim Ausführen von mc: {e}", "Fehler", wx.OK | wx.ICON_ERROR)
    dlg.Destroy()

# Method for deleting a bucket
def on_remove_bucket(self, event):
    """
    Removing the selected MinIO bucket after user confirmation.
    """
    selected_index = self.learning_ctrl.GetFirstSelected()
    if selected_index == -1:
        wx.MessageBox(
            "Bitte wählen Sie einen Bucket zum Löschen aus.",
            "Kein Bucket ausgewählt",
            wx.OK | wx.ICON_WARNING
        )
        return

    bucket_display_name = self.learning_ctrl.GetItemText(selected_index, 0)
    bucket_name = bucket_display_name.upper()

    dlg = wx.MessageDialog(
        self,
        f"Sind Sie sicher, dass Sie den Bucket '{bucket_display_name}' und alle darin enthaltenen Objekte löschen möchten?",
        "Bucket löschen bestätigen",
        wx.YES_NO | wx.NO_DEFAULT | wx.ICON_WARNING
    )
    if dlg.ShowModal() != wx.ID_YES:
        dlg.Destroy()
        return
    dlg.Destroy()

    try:
        minio_client = connect_to_minio()
        if minio_client is None:
            wx.MessageBox(
                "MinIO-Verbindung konnte nicht hergestellt werden.",
                "Fehler",
                wx.OK | wx.ICON_ERROR
            )
            return

        # Normalizing bucket name before MinIO operations
        bucket_name = bucket_name.lower().replace(' ', '-')

        # Deleting all objects in the bucket
        objects = minio_client.list_objects(bucket_name, recursive=True)
        for obj in objects:
            minio_client.remove_object(bucket_name, obj.object_name)
        minio_client.remove_bucket(bucket_name)
        wx.MessageBox(
            f"Bucket '{bucket_display_name}' wurde erfolgreich gelöscht.",
            "Bucket gelöscht",
            wx.OK | wx.ICON_INFORMATION
        )

        # Refreshing the bucket list and restoring selection
        self.refresh_learning_ctrl_with_minio()
        item_count = self.learning_ctrl.GetItemCount()
        if item_count > 0:
            # Selecting the next logical bucket (same index or previous if last was deleted)
            new_index = selected_index if selected_index < item_count else item_count - 1
            new_bucket_display = self.learning_ctrl.GetItemText(new_index, 0)
            new_bucket_name = new_bucket_display.upper()
            self.refresh_learning_ctrl_with_minio(select_bucket_name=new_bucket_name)
        else:
            g.elearning_index = -1
            g.minio_bucket_name = ""
            from src.files import refresh_files_ctrl_with_minio
            refresh_files_ctrl_with_minio(self)

    except S3Error as e:
        wx.MessageBox(
            f"Fehler beim Löschen des Buckets: {e}",
            "Fehler",
            wx.OK | wx.ICON_ERROR
        )
    except Exception as e:
        wx.MessageBox(
            f"Unerwarteter Fehler beim Löschen des Buckets: {e}",
            "Fehler",
            wx.OK | wx.ICON_ERROR
        )

# Method to refresh and display MinIO buckets in the learning_ctrl
def refresh_learning_ctrl_with_minio(self, select_bucket_name=None):
    """
    Refreshing and displaying MinIO buckets in the learning_ctrl.
    Optionally selects a bucket by name after refresh.
    """
    try:
        # Checking for empty endpoint
        if not g.minio_endpoint:
            wx.MessageBox(
                "MinIO-Endpunkt ist nicht gesetzt. Bitte tragen Sie einen gültigen Wert in der Konfiguration ein.",
                "Fehler",
                wx.OK | wx.ICON_ERROR
            )
            return

        # Connecting to MinIO and listing buckets
        minio_client = connect_to_minio()
        if minio_client is None:
            wx.MessageBox(
                "MinIO-Verbindung konnte nicht hergestellt werden.",
                "Fehler",
                wx.OK | wx.ICON_ERROR
            )
            return
        buckets = list_buckets(minio_client)
        if buckets is None:
            buckets = []
        display_learning(self, buckets)

        # Clearing all selections before selecting the intended one
        for idx in range(self.learning_ctrl.GetItemCount()):
            self.learning_ctrl.SetItemState(idx, 0, wx.LIST_STATE_SELECTED | wx.LIST_STATE_FOCUSED)

        # Setting the correct bucket selection logic
        selected_idx = 0
        target_bucket = None

        # Prefer explicit select_bucket_name, then g.minio_bucket_name, else first bucket
        if select_bucket_name:
            target_bucket = select_bucket_name.upper()
        elif g.minio_bucket_name:
            target_bucket = g.minio_bucket_name.upper()

        if target_bucket and target_bucket in buckets:
            selected_idx = buckets.index(target_bucket)
        elif buckets:
            selected_idx = 0
            target_bucket = buckets[0]

        if buckets:
            g.elearning_index = selected_idx
            g.minio_bucket_name = target_bucket

            # Setting only the intended item as selected and focused
            self.learning_ctrl.SetItemState(
                selected_idx,
                wx.LIST_STATE_SELECTED | wx.LIST_STATE_FOCUSED,
                wx.LIST_STATE_SELECTED | wx.LIST_STATE_FOCUSED
            )
            self.learning_ctrl.EnsureVisible(selected_idx)

            # Setting the selected bucket and show its objects
            from src.files import refresh_files_ctrl_with_minio
            refresh_files_ctrl_with_minio(self)
    except Exception as e:
        wx.MessageBox(
            f"Fehler beim Laden der MinIO-Buckets: {e}", "Fehler", wx.OK | wx.ICON_ERROR)

# Method to display_learning
def display_learning(self, files):
    self.learning_ctrl.DeleteAllItems()  # Only remove items
    for idx, file_name in enumerate(files, start=0):
        self.learning_ctrl.InsertItem(idx, file_name)

    # Selecting the first item if available
    if files:
        g.elearning_index = 0
        self.learning_ctrl.Select(0)
        self.learning_ctrl.EnsureVisible(0)

# Method to handle the selection of an item in the learning_ctrl
def on_elearning_item_selected(self, event):
    g.elearning_index = event.GetIndex()
    bucket_name = self.learning_ctrl.GetItemText(g.elearning_index, 0).upper()
    g.minio_bucket_name = bucket_name

    # Showing objects in the selected bucket in the file explorer
    from src.files import refresh_files_ctrl_with_minio
    refresh_files_ctrl_with_minio(self)

# Method to handle the activation of an item in the learning_ctrl
def on_elearning_item_activated(self, event):
    item_index = event.GetIndex()
    item_text = self.learning_ctrl.GetItemText(item_index, 0)

# Method to upload file(s) to MinIO via wx dialog
def on_upload_file_to_minio(self, event):
    """
    Handling file selection and uploading to MinIO bucket.
    """
    wildcard = "Alle Dateien (*.*)|*.*"
    dialog = wx.FileDialog(
        self,
        "Bitte wählen Sie eine oder mehrere Dateien zum Hochladen aus:",
        wildcard=wildcard,
        style=wx.FD_OPEN | wx.FD_MULTIPLE
    )
    if dialog.ShowModal() == wx.ID_OK:
        file_paths = dialog.GetPaths()
        try:
            # Connecting to MinIO
            minio_client = connect_to_minio()
            if not g.minio_bucket_name:
                wx.MessageBox(
                    "MinIO-Bucket ist nicht gesetzt. Bitte prüfen Sie die Konfiguration.",
                    "Fehler",
                    wx.OK | wx.ICON_ERROR
                )
                return
            if minio_client is None:
                wx.MessageBox(
                    "MinIO-Verbindung konnte nicht hergestellt werden.",
                    "Fehler",
                    wx.OK | wx.ICON_ERROR
                )
                return

            # Creating bucket if it does not exist
            if not minio_client.bucket_exists(g.minio_bucket_name):
                minio_client.make_bucket(g.minio_bucket_name)

            # Uploading files using the helper
            upload_files(minio_client, g.minio_bucket_name, file_paths)

            wx.MessageBox(
                f"{len(file_paths)} Datei(en) erfolgreich hochgeladen.",
                "Upload abgeschlossen",
                wx.OK | wx.ICON_INFORMATION
            )

            # Refreshing the learning control and keeping the current bucket selected
            self.refresh_learning_ctrl_with_minio(select_bucket_name=g.minio_bucket_name)
        except Exception as e:
            wx.MessageBox(
                f"Fehler beim Hochladen zu MinIO: {e}",
                "Fehler",
                wx.OK | wx.ICON_ERROR
            )
    dialog.Destroy()
