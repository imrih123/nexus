import wx
import threading
import queue
import time
import humanize

class MyFrame(wx.Frame):
    def __init__(self, parent, title):
        super(MyFrame, self).__init__(parent, title=title, size=(500, 350))

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
        self.update_file_list()

        self.SetBackgroundColour(wx.Colour(240, 240, 240))  # Set background color

        self.upload_button.SetBackgroundColour(wx.Colour(0, 128, 255))  # Set button background color
        self.upload_button.SetForegroundColour(wx.Colour(255, 255, 255))  # Set button text color

        self.download_button.SetBackgroundColour(wx.Colour(0, 160, 0))
        self.download_button.SetForegroundColour(wx.Colour(255, 255, 255))

        self.Bind(wx.EVT_BUTTON, self.on_upload, self.upload_button)
        self.Bind(wx.EVT_BUTTON, self.on_download, self.download_button)

        self.Show()

    def on_upload(self, event):
        wildcard = "All files (*.*)|*.*"
        dialog = wx.FileDialog(self, "Choose a file", wildcard=wildcard, style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)

        if dialog.ShowModal() == wx.ID_OK:
            file_path = dialog.GetPath()
            print("Uploading:", file_path)

        dialog.Destroy()

    def on_download(self, event):
        selected_index = self.file_list_ctrl.GetFirstSelected()
        if selected_index != -1:
            selected_file = self.file_list[selected_index][0]
            print("Downloading:", selected_file)
            # Implement your download logic here
        else:
            wx.MessageBox("Please select a file to download.", "Error", wx.OK | wx.ICON_ERROR)

    def update_file_list(self, new_file_list=None):
        if new_file_list is not None:
            self.file_list = new_file_list

        self.file_list_ctrl.DeleteAllItems()
        for i, file_info in enumerate(self.file_list):
            self.file_list_ctrl.InsertItem(i, file_info[0])
            self.file_list_ctrl.SetItem(i, 1, f"{humanize.naturalsize(file_info[1])}".lower())
            self.file_list_ctrl.SetItem(i, 2, str(file_info[2]))
            self.file_list_ctrl.SetItem(i, 3, f"{round(file_info[1]/10240/file_info[2], 2)} seconds")



def file_updater_thread(file_queue, frame):
    while True:
        received_files = file_queue.get()
        frame.update_file_list(received_files)


def file_changer_thread(file_queue):
    time.sleep(3)
    file_queue.put([["file1.jpg", 256000, 5], ["file2.zip", 61240, 2], ["file3.jpg", 8, 1],["file1.jpg", 25600, 1], ["file2.zip", 44124, 2], ["file3.jpg", 1000000, 10],["file1.jpg", 2560000, 2], ["file2.zip", 6124, 2]])


if __name__ == "__main__":
    app = wx.App(False)
    frame = MyFrame(None, "nexus")

    file_queue = queue.Queue()
    threading.Thread(target=file_updater_thread, args=(file_queue, frame)).start()
    threading.Thread(target=file_changer_thread, args=(file_queue,)).start()

    app.MainLoop()