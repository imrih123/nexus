import os
import win32file
import win32con
import win32event
from datetime import datetime
import shutil
import win32com.client
import threading
import queue
import os
import ctypes


class monitoring(object):
    def __init__(self, path_to_monitor, queue):
        """

        :param path_to_monitor:
        :param queue:
        """
        self.path_to_monitor = path_to_monitor
        self.msgs_queue = queue
        self.list_of_new_files = []
        if not os.path.exists(path_to_monitor):
            os.mkdir(path_to_monitor)
        attrs = os.stat(self.path_to_monitor).st_file_attributes

        # Check if the 'hidden' attribute is set
        if not attrs & 2 == 2:
            # Get the file attributes
            attrs = ctypes.windll.kernel32.GetFileAttributesW(self.path_to_monitor)
            # Add the 'hidden' attribute
            ctypes.windll.kernel32.SetFileAttributesW(self.path_to_monitor, attrs | 2)

        self._send_existing_files()
        threading.Thread(target=self._monitoring_folder).start()
        self.first_change()

    def first_change(self):
        """

        :return:
        """
        path = f"{self.path_to_monitor}\\a.txt"
        with open(path, 'w') as f:
            f.write("imri")
        if os.path.exists(fr"{path}"):
            os.remove(fr"{path}")

    def _send_existing_files(self):
        """

        :return:
        """
        list_of_file = os.listdir(self.path_to_monitor)
        for file_name in list_of_file:
            self.msgs_queue.put(("01", file_name))

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
                            self.list_of_new_files.append(filename)

                        elif action == 2:
                            self.msgs_queue.put(("02", filename))

                        elif action == 3:
                            if filename in self.list_of_new_files:
                                self.list_of_new_files.remove(filename)
                                self.msgs_queue.put(("01", filename))
                            else:
                                self.msgs_queue.put(("03", filename))

                        elif action == 4:
                            self.msgs_queue.put(("03", filename))

                        elif action == 5:
                            self.msgs_queue.put(("05", filename))
                        else:
                            print(action)

        except Exception as e:
            win32file.FindCloseChangeNotification(change_handle)


if __name__ == '__main__':
    q = queue.Queue()
    c = monitoring(fr"T:\public\יב\imri\nexus\projectCode\\.nitur", q)
    while True:
        print(q.get())