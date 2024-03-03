import wx
from humanize import naturaldelta, naturalsize
import os
from pubsub import pub
from allcode import settingCli
import shutil


class MyFrame(wx.Frame):
    def __init__(self, parent, title, queue, logo_path):
        """
        create the frame and all the buttons
        :param parent: None
        :param title: the title
        :param queue: the queue to put the messages
        :param logo_path: the path to the logo
        """
        super(MyFrame, self).__init__(parent, title=title, size=(680, 350))
        self.panel = wx.Panel(self)
        self.panel.SetBackgroundColour(f"#001f3f")
        self.queue = queue
        # List of lists: [file_name, size, number of clients]
        self.file_list = []
        self.progress_dialog = None
        self.total_bytes_download = 0

        # upload button
        self.upload_button = wx.Button(self.panel, label="Upload", pos=(30, 220), size=(100, 60))
        font = wx.Font(11, wx.DEFAULT, wx.NORMAL, wx.NORMAL, faceName="Avenir")
        self.upload_button.SetFont(font)

        # download button
        self.download_button = wx.Button(self.panel, label="Download", pos=(160, 220), size=(100, 60))
        font = wx.Font(11, wx.DEFAULT, wx.NORMAL, wx.NORMAL, faceName="Avenir")
        self.download_button.SetFont(font)

        # the table of the files
        self.file_list_ctrl = wx.ListCtrl(self.panel, style=wx.LC_REPORT | wx.BORDER_SUNKEN, pos=(35, 15),
                                          size=(600, 170))
        self.file_list_ctrl.SetBackgroundColour(wx.Colour(255, 255, 255))
        self.file_list_ctrl.InsertColumn(0, 'File Name', width=140)
        self.file_list_ctrl.InsertColumn(1, 'Size', width=140)
        self.file_list_ctrl.InsertColumn(2, 'Clients', width=130)
        self.file_list_ctrl.InsertColumn(3, 'estimated time', width=165)

        # change the colors to the button
        self.download_button.SetBackgroundColour(F"#36bf81")
        self.download_button.SetForegroundColour(wx.Colour(255, 255, 255))

        # change the colors to the button
        self.upload_button.SetBackgroundColour(F"#36bf81")
        self.upload_button.SetForegroundColour(wx.Colour(255, 255, 255))

        # set the func to call when the button is click
        self.Bind(wx.EVT_BUTTON, self.on_upload, self.upload_button)
        self.Bind(wx.EVT_BUTTON, self.on_download, self.download_button)

        # put the logo
        image_path = logo_path
        image = wx.Image(image_path, wx.BITMAP_TYPE_ANY)
        image = image.Scale(380, 115, wx.IMAGE_QUALITY_HIGH)
        wx.StaticBitmap(self.panel, bitmap=wx.Bitmap(image), pos=(280, 195))

        self.Show()

        # bind the func to the strings
        pub.subscribe(self.update_file_list, "new list")
        pub.subscribe(self.show_download_progress, "new part")
        pub.subscribe(self.file_exists_error, "file exists")

    def file_exists_error(self):
        """
        show error when file already exists
        """
        wx.MessageBox("file with that name already exists in the system",
                               "Error",
                               wx.OK | wx.ICON_WARNING)

    def on_upload(self, event):
        """
        shows the file explorer and let the user choose a file
        """
        wildcard = "All files (*.*)|*.*"
        dialog = wx.FileDialog(self, "Choose a file", wildcard=wildcard, style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)

        if dialog.ShowModal() == wx.ID_OK:
            file_path = dialog.GetPath()
            file_size = os.path.getsize(file_path)
            # if file size is too big
            if file_size > 5 * 1024 * 1024 * 1024:
                wx.MessageBox("File size exceeds the maximum allowed (5GB). Please choose a smaller file.", "Error",
                              wx.OK | wx.ICON_ERROR)
            else:
                # let the logic know upload is requested
                self.queue.put(("upload", file_path))

        dialog.Destroy()

    def on_download(self, event):
        """
        after a click on the download start the download
        """
        selected_index = self.file_list_ctrl.GetFirstSelected()
        if selected_index != -1:
            selected_file = self.file_list[selected_index][0]
            # if file exists in the nitur file
            if os.path.exists(f"{settingCli.NITUR_FOLDER}\\{selected_file}"):
                result = wx.MessageBox("already have this file, copy file to downloads ?",
                                       "Error",
                                       wx.YES_NO | wx.ICON_WARNING)
                # if the user want to copy
                if result == wx.YES:
                    shutil.copy2(f"{settingCli.NITUR_FOLDER}\\{selected_file}",
                                 f"{settingCli.PATH_TO_SAVE_FILES}\\{selected_file}")
            # if the user choose dirctory
            elif os.path.isdir(selected_file):
                wx.MessageBox("cant download directory, compress to zip file", "Error", wx.OK | wx.ICON_ERROR)

            else:
                # let the logic know download is requested
                self.queue.put(("download", selected_file))
                self.upload_button.Enable(False)
                self.download_button.Enable(False)
        else:
            wx.MessageBox("Please select a file to download.", "Error", wx.OK | wx.ICON_ERROR)

    def show_download_progress(self, bytes_downloaded, total_bytes, name_of_file, first_part):
        """

        :param bytes_downloaded: the number of byte downloaded
        :param total_bytes: the total bytes to download
        :param name_of_file: the name of the file
        """
        # If progress dialog doesn't exist and its the first part, create it
        if self.progress_dialog is None and first_part:
            self.progress_dialog = wx.ProgressDialog("Downloading", "Downloading file...", maximum=total_bytes,
                                                     parent=self, style=wx.PD_AUTO_HIDE | wx.PD_CAN_ABORT)
        # if the progress dialog if open
        if self.progress_dialog is not None:
            self.total_bytes_download += bytes_downloaded

            abort = self.progress_dialog.Update(self.total_bytes_download)

            # If download is complete, destroy the progress dialog and rest the progress screen
            if total_bytes == self.total_bytes_download or not abort[0]:
                self.progress_dialog.Destroy()
                self.progress_dialog = None
                self.upload_button.Enable(True)
                self.download_button.Enable(True)
                self.total_bytes_download = 0
                if not abort[0]:
                    self.queue.put(("abort", name_of_file))
                    wx.MessageBox(f"download of {name_of_file} was cancel ",
                                  "Error",
                                  wx.OK | wx.ICON_WARNING)
                else:
                    # Show a message box when the download is complete
                    wx.MessageBox(f"Download of {name_of_file} complete!", "Success", wx.OK | wx.ICON_INFORMATION, self)

    def update_file_list(self, new_file_list):
        """
        add the item to the table
        :param new_file_list: the list of files
        """

        self.file_list = new_file_list
        self.file_list_ctrl.DeleteAllItems()
        if self.file_list != [[]]:
            for i, file_info in enumerate(self.file_list):
                self.file_list_ctrl.InsertItem(i, file_info[0])
                self.file_list_ctrl.SetItem(i, 1, f"{naturalsize(file_info[1])}".lower())
                self.file_list_ctrl.SetItem(i, 2, file_info[2])
                self.file_list_ctrl.SetItem(i, 3, f"{naturaldelta(int(file_info[1]) / 81920 / int(file_info[2]))}")

