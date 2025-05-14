# `src/learning.py`
# Learning Panel for the Dateiablage application
# Open-Source, hosted on https://github.com/DrBenjamin/Dateiablage
# Please reach out to ben@seriousbenentertainment.org for any questions
# Modules
import wx
import os
import src.globals as g
from minio.error import S3Error
from io import BytesIO
from src.minio_utils import connect_to_minio

# Method to list buckets
def list_buckets(minio_client):
    try:
        buckets = minio_client.list_buckets()
        return [
            bucket.name.replace('-', ' ').title()
            for bucket in buckets
        ]
    except S3Error as e:
        wx.MessageBox(
            f"Fehler beim auflisten der MinIO-Buckets: {e}", "Fehler", wx.OK | wx.ICON_ERROR)
    return

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

        # Selecting the correct bucket
        selected_idx = 0
        if select_bucket_name:
            for idx, display_name in enumerate(buckets):
                if display_name.replace(' ', '-').lower() == select_bucket_name:
                    selected_idx = idx
                    break
        elif g.minio_bucket_name:
            for idx, display_name in enumerate(buckets):
                if display_name.replace(' ', '-').lower() == g.minio_bucket_name:
                    selected_idx = idx
                    break

        if buckets:
            g.elearning_index = selected_idx

            # Setting only the intended item as selected and focused
            self.learning_ctrl.SetItemState(
                selected_idx,
                wx.LIST_STATE_SELECTED | wx.LIST_STATE_FOCUSED,
                wx.LIST_STATE_SELECTED | wx.LIST_STATE_FOCUSED
            )
            self.learning_ctrl.EnsureVisible(selected_idx)

            # Setting the selected bucket and show its objects
            bucket_name = buckets[selected_idx].replace(' ', '-').lower()
            g.minio_bucket_name = bucket_name
            from src.files import refresh_files_ctrl_with_minio
            refresh_files_ctrl_with_minio(self)

        # Setting the window title safely
        self.SetTitle("Dateiablage - Buckets")
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
    bucket_name = self.learning_ctrl.GetItemText(g.elearning_index, 0).replace(' ', '-').lower()
    g.minio_bucket_name = bucket_name

    # Showing objects in the selected bucket in the file explorer
    from src.files import refresh_files_ctrl_with_minio
    refresh_files_ctrl_with_minio(self)

    self.SetTitle(f"Dateiablage - {bucket_name}")

# Method to handle the activation of an item in the learning_ctrl
def on_elearning_item_activated(self, event):
    item_index = event.GetIndex()
    item_text = self.learning_ctrl.GetItemText(item_index, 0)
    display_tasks(self, g.df_tasks)
    g.ticket_chosen = True

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

            # Uploading each file
            for file_path in file_paths:
                file_name = os.path.basename(file_path)
                with open(file_path, "rb") as f:
                    file_data = f.read()
                    minio_client.put_object(
                        g.minio_bucket_name,
                        file_name,
                        BytesIO(file_data),
                        len(file_data)
                    )
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
