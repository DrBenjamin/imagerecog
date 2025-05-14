### `src/minio_utils.py`
### # Utility functions for MinIO connection
### Open-Source, hosted on https://github.com/DrBenjamin/Dateiablage
### Please reach out to ben@seriousbenentertainment.org for any questions
## Modules
import wx
from minio import Minio
from minio.error import S3Error
import src.globals as g

# Method to connect to MinIO
def connect_to_minio():
    try:
        client = Minio(
            g.minio_endpoint,
            access_key=g.minio_access_key,
            secret_key=g.minio_secret_key,
            secure=g.minio_secure,  # Using HTTP or HTTPS
            cert_check=False
        )
        return client
    except S3Error as e:
        wx.MessageBox(
            f"Fehler beim aufbauen der MinIO-Verbindung: {e}", "Fehler", wx.OK | wx.ICON_ERROR)
    return None

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
    bucket_name = bucket_display_name.replace(' ', '-').lower()

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
            new_bucket_name = new_bucket_display.replace(' ', '-').lower()
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
