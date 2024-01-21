import os
import win32file
import win32con
import win32event
from datetime import datetime
import shutil
import win32com.client
import threading


class monitoring(object):
    def __init__(self, path_to_monitor):
        self.path_to_monitor = path_to_monitor
        threading.Thread(target=self._monitoring_folder).start()

    def _monitoring_folder(self):
        '''
        monitor a directory and record the changes in a file and on the screen
        :return:
        '''
        # set up the notification handle
        change_handle = win32file.FindFirstChangeNotification(
            self.path_to_monitor,
            0,
            win32con.FILE_NOTIFY_CHANGE_FILE_NAME | win32con.FILE_NOTIFY_CHANGE_DIR_NAME | win32con.FILE_NOTIFY_CHANGE_LAST_WRITE
        )
        try:
            while True:
                result = win32event.WaitForSingleObject(change_handle, win32event.INFINITE)
                # check if there are any changes
                if result == win32event.WAIT_OBJECT_0:

                    for action, filename in win32file.ReadDirectoryChangesW(change_handle, 1024, True,
                                                                            win32con.FILE_NOTIFY_CHANGE_FILE_NAME | win32con.FILE_NOTIFY_CHANGE_DIR_NAME | win32con.FILE_NOTIFY_CHANGE_LAST_WRITE):
                        time = datetime.now().strftime("%H:%M:%S")
                        if action == 1:
                            print(f"{time}  -  new file:  {filename}")
                            with open("log.txt", "a", encoding="utf-8") as log_file:
                                log_file.write(time + "  -  new file:  " + filename + "\n")
                        elif action == 2:
                            print(f"{time}  -  file removed:  {filename}")
                            with open("log.txt", "a", encoding="utf-8") as log_file:
                                log_file.write(time + "  -  file removed:  " + filename + "\n")
                        elif action == 3:
                            print(f"{time}  -  file has been changed:  {filename}")
                            with open("log.txt", "a", encoding="utf-8") as log_file:
                                log_file.write(time + "  -  file has been changed:  " + filename + "\n")
                        elif action == 4:
                            print(f"{time}  -  filename changed from:  {filename}  to:  ", end='')
                            with open("log.txt", "a", encoding="utf-8") as log_file:
                                log_file.write(time + "  -  filename changed from:  " + filename + "  to:  ")
                        elif action == 5:
                            print(f"{filename}")
                            with open("log.txt", "a", encoding="utf-8") as log_file:
                                log_file.write(filename + "\n")
        except Exception as e:
            win32file.FindCloseChangeNotification(change_handle)


c = monitoring("T:\public\יב\imri\nexus\projectCode\files")
# # get the monitoring directory
# monitor_dir = input("please enter the path directory you would like to monitor: ")
# while not os.path.exists(monitor_dir):
#     monitor_dir = input("please enter an existing path directory: ")
#
# # get the picture directory
# pics_dir = input("please enter the path directory for pictures: ")
# while not os.path.exists(pics_dir):
#     pics_dir = input("please enter an existing path directory: ")
#
# # start monitoring the directory
# threading.Thread(target=monitor, args=[monitor_dir]).start()
#
# # ask the user for pictures and open in Internet Explorer
# while True:
#     pic_name = input("enter pic name: ")
#     ie = win32com.client.Dispatch("InternetExplorer.Application")
#     ie.Navigate('http://www.google.com/search?q=<'+pic_name+'>&tbm=isch')
#     ie.Visible = 1