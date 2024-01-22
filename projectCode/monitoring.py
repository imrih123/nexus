import os
import win32file
import win32con
import win32event
from datetime import datetime
import shutil
import win32com.client
import threading
import queue


class monitoring(object):
    def __init__(self, path_to_monitor, queue):
        """

        :param path_to_monitor:
        :param queue:
        """
        self.path_to_monitor = path_to_monitor
        self.msgs_queue = queue
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
            win32con.FILE_NOTIFY_CHANGE_FILE_NAME | win32con.FILE_NOTIFY_CHANGE_DIR_NAME | win32con.FILE_NOTIFY_CHANGE_SIZE

        )
        try:
            while True:
                result = win32event.WaitForSingleObject(change_handle, win32event.INFINITE)
                # check if there are any changes
                if result == win32event.WAIT_OBJECT_0:

                    for action, filename in win32file.ReadDirectoryChangesW(change_handle, 1024, True,
                                                                            win32con.FILE_NOTIFY_CHANGE_FILE_NAME | win32con.FILE_NOTIFY_CHANGE_DIR_NAME | win32con.FILE_NOTIFY_CHANGE_LAST_WRITE):
                        if action == 1:
                            self.msgs_queue.put(("1", filename))

                        elif action == 2:
                            self.msgs_queue.put(("2", filename))

                        elif action == 3:
                            self.msgs_queue.put(("3", filename))

                        elif action == 5:
                            self.msgs_queue.put(("5", filename))

        except Exception as e:
            win32file.FindCloseChangeNotification(change_handle)


# time = datetime.now().strftime("%H:%M:%S")

# with open("log.txt", "a", encoding="utf-8") as log_file:
                            #     log_file.write(filename + "\n")

# with open("log.txt", "a", encoding="utf-8") as log_file:
                            #     log_file.write(time + "  -  file has been changed:  " + filename + "\n")

# with open("log.txt", "a", encoding="utf-8") as log_file:
                            #     log_file.write(time + "  -  file removed:  " + filename + "\n")

# with open("log.txt", "a", encoding="utf-8") as log_file:
                                # log_file.write(time + "  -  new file:  " + filename + "\n")
if __name__ == '__main__':
    q = queue.Queue()
    c = monitoring(fr"T:\public\יב\imri\nexus\projectCode\files", q)
    while True:
        print(q.get())
