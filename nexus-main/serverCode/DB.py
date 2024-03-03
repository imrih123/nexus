import sqlite3


class DBClass:
    def __init__(self):
        """
        set the curr and the conns and the names
        """
        self.dbName = "NexusDB.sql"
        self.tblName = "torrnetTBL"
        self.conn = None
        self.curr = None
        self._buildDB()

    def _buildDB(self):
        """
        create DB if DB dose not exists yet
        :return: None
        """
        self.conn = sqlite3.connect(self.dbName)
        self.curr = self.conn.cursor()
        sql = f"CREATE TABLE IF NOT EXISTS {self.tblName}(names VARCHAR(10) PRIMARY KEY)"
        self.curr.execute(sql)
        self.conn.commit()

    def have_torrent(self, torrent_name):
        """
        check if user name in the table
        :param torrent_name:
        :return: none or data
        """
        sql = f"SELECT * FROM {self.tblName} WHERE names = ?"
        self.curr.execute(sql, (torrent_name,))
        return self.curr.fetchone() is not None

    def add_torrent(self, torrent_name):
        """

        :param torrent_name:
        :return:
        """
        if not self.have_torrent(torrent_name):
            sql = f"INSERT INTO {self.tblName} VALUES (?)"
            self.curr.execute(sql, (torrent_name,))
            self.conn.commit()

    def deleteDb(self):
        """
        delete the db
        :return:
        """
        sql = f"DROP TABLE {self.tblName}"
        self.curr.execute(sql)
        self.conn.commit()

    def closeDb(self):
        """
        close the db
        :return:
        """
        self.curr.close()
        self.conn.close()

