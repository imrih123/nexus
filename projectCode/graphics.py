import wx
import threading
import queue
import time
import humanize
from pubsub import pub

class MyFrame(wx.Frame):
    def __init__(self, parent, title, queue):
        super(MyFrame, self).__init__(parent, title=title, size=(500, 350))
        self.queue = queue
        self.panel = wx.Panel(self)
        self.panel.SetBackgroundColour(wx.Colour(240, 240, 240))

        self.file_list = []  # List of lists: [file_name, size, number of clients]

        self.upload_button = wx.Button(self.panel, label="Upload", pos=(30, 240), size=(100, 40))
        self.download_button = wx.Button(self.panel, label="Download", pos=(160, 240), size=(100, 40))

        self.file_list_ctrl = wx.ListCtrl(self.panel, style=wx.LC_REPORT | wx.BORDER_SUNKEN, pos=(30, 30),
                                          size=(440, 150))
        self.file_list_ctrl.InsertColumn(0, 'File Name', width=100)
        self.file_list_ctrl.InsertColumn(1, 'Size', width=100)
        self.file_list_ctrl.InsertColumn(2, 'Clients', width=100)
        self.file_list_ctrl.InsertColumn(3, 'estimated time', width=115)
        # self.update_file_list()

        self.SetBackgroundColour(wx.Colour(240, 240, 240))  # Set background color

        self.upload_button.SetBackgroundColour(wx.Colour(0, 128, 255))  # Set button background color
        self.upload_button.SetForegroundColour(wx.Colour(255, 255, 255))  # Set button text color

        self.download_button.SetBackgroundColour(wx.Colour(0, 160, 0))
        self.download_button.SetForegroundColour(wx.Colour(255, 255, 255))

        self.Bind(wx.EVT_BUTTON, self.on_upload, self.upload_button)
        self.Bind(wx.EVT_BUTTON, self.on_download, self.download_button)

        self.Show()

        pub.subscribe( self.update_file_list, "new list")

    def on_upload(self, event):
        """

        :param event:
        :return:
        """
        wildcard = "All files (*.*)|*.*"
        dialog = wx.FileDialog(self, "Choose a file", wildcard=wildcard, style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)

        if dialog.ShowModal() == wx.ID_OK:
            file_path = dialog.GetPath()
            self.queue.put(("upload", file_path))

        dialog.Destroy()

    def on_download(self, event):
        """

        :param event:
        :return:
        """
        selected_index = self.file_list_ctrl.GetFirstSelected()
        if selected_index != -1:
            selected_file = self.file_list[selected_index][0]
            self.queue.put(("download", selected_file))
            # Implement your download logic here
        else:
            wx.MessageBox("Please select a file to download.", "Error", wx.OK | wx.ICON_ERROR)

    def update_file_list(self, new_file_list=None):
        """

        :param new_file_list:
        :return:
        """
        print("in update.....", new_file_list)

        if new_file_list is not None:
            self.file_list = new_file_list

        self.file_list_ctrl.DeleteAllItems()
        print(self.file_list)
        if self.file_list != [[]]:
            for i, file_info in enumerate(self.file_list):
                self.file_list_ctrl.InsertItem(i, file_info[0])
                self.file_list_ctrl.SetItem(i, 1, f"{humanize.naturalsize(file_info[1])}".lower())
                self.file_list_ctrl.SetItem(i, 2, file_info[2])
                self.file_list_ctrl.SetItem(i, 3, f"{round(int(file_info[1])/81920/int(file_info[2]), 2)} seconds")



