import os
import sqlite3
import uuid

import xbmc

from resources.lib.compatibility import encode_utf, translatePath
from resources.lib.const import DB_TABLE, DOWNLOAD_STATUS, ROUTE
from resources.lib.kodilogging import service_logger, logger
from resources.lib.utils.kodiutils import data_dir, try_decode, get_info


def escape(text):
    return text.replace("'", "''")


CURRENT_USER_VERSION = 5

pre_updates = {
    5: [
        '''DROP TABLE IF EXISTS ''' + DB_TABLE.FILTERS + ''';'''
    ]
}

updates = {
    1: [
        '''ALTER TABLE ''' + DB_TABLE.TRAKT_LIST_ITEMS + ''' ADD COLUMN play_count INT DEFAULT NULL;'''
    ],
    2: [
        '''ALTER TABLE ''' + DB_TABLE.TRAKT_LIST_ITEMS + ''' ADD COLUMN show_id INT DEFAULT NULL;''',
        '''ALTER TABLE ''' + DB_TABLE.TRAKT_LIST_ITEMS + ''' ADD COLUMN season INT DEFAULT NULL;''',
        '''ALTER TABLE ''' + DB_TABLE.TRAKT_LIST_ITEMS + ''' ADD COLUMN episode INT DEFAULT NULL;''',
        '''ALTER TABLE ''' + DB_TABLE.TRAKT_LIST_ITEMS + ''' ADD COLUMN last_updated_at TEXT DEFAULT NULL;''',
        '''DELETE FROM ''' + DB_TABLE.TRAKT_LIST_ITEMS,
    ],
    3: [
        '''ALTER TABLE ''' + DB_TABLE.WATCH_HISTORY + ''' ADD COLUMN media_type TEXT DEFAULT NULL;'''
    ],
    4: [
        '''ALTER TABLE ''' + DB_TABLE.DOWNLOAD + ''' ADD COLUMN subs_included INT DEFAULT 0;'''
    ],
}


class SQLiteStorage:
    def __init__(self, db_dir=data_dir(), db_name="data.db"):
        db_path = translatePath(db_dir)
        db_path = try_decode(db_path)
        db_name = try_decode(db_name)
        self.db_path = os.path.join(db_path, db_name)

    def connect(self):
        return sqlite3.connect(self.db_path)

    def execute(self, query, *args):
        service_logger.debug('DB: Executed ' + encode_utf(query))
        with self.connect() as conn:
            c = conn.cursor()
            c.execute(query, args)
            conn.commit()

    def get_schema(self, table_name):
        cur = self.select("SELECT sql FROM sqlite_master WHERE type='table' AND name='%s'" % table_name)
        return cur.fetchone()[0]

    def get_version(self):
        return self.select('PRAGMA user_version').fetchone()[0]

    def set_version(self, version):
        return self.execute('PRAGMA user_version = %s' % version)

    def update(self, updates_list):
        version = self.get_version()
        if version != CURRENT_USER_VERSION:
            service_logger.debug('DB: Updating from version %s to %s' % (version, CURRENT_USER_VERSION))
            for i in range(version + 1, CURRENT_USER_VERSION + 1):
                if i in updates_list:
                    self.multiexecute(updates_list[i])

    def select(self, query, *args):
        with self.connect() as conn:
            c = conn.cursor()
            c.execute(query, args)
            return c

    def get_last_row_id(self, table, id_column="id"):
        with self.connect() as conn:
            c = conn.cursor()
            cursor = c.execute('SELECT max(' + id_column + ') FROM ' + table)
            return cursor.fetchone()[0]

    def clear(self, table_name):
        self.execute('DELETE FROM %s' % table_name)

    def multiexecute(self, queries):
        with self.connect() as conn:
            c = conn.cursor()
            for query in queries:
                if isinstance(query, tuple):
                    service_logger.debug("DB: Multiexecute %s (%r)" % (query[0], query[1]))
                    c.execute(query[0], query[1:])
                elif isinstance(query, str):
                    service_logger.debug("DB: Multiexecute %s" % query)
                    c.execute(query)
                else:
                    raise ValueError('Unrecognized type in queries.')
            conn.commit()

    @staticmethod
    def insert_or_replace(table, **kwargs):
        values = kwargs.values()
        cols = kwargs.keys()
        params = ','.join(['?' for i in range(len(values))])
        return ('INSERT or REPLACE INTO %s(%s) VALUES (%s)' % (table, ','.join(cols), params),) + tuple(values)

    def update_many(self, table, items):
        self.multiexecute([self.insert_or_replace(table, **item) for item in items])

    class Pinned:
        TABLE_NAME = DB_TABLE.PINNED

        def __init__(self):
            self.db = SQLiteStorage()
            self.db.execute(
                '''CREATE TABLE IF NOT EXISTS ''' + self.TABLE_NAME +
                ''' (route text NOT NULL, key text NOT NULL, PRIMARY KEY (key, route))''')

        def add(self, route, key):
            self.db.execute(
                "INSERT OR REPLACE INTO " + self.TABLE_NAME + " VALUES ('" + route + "','" + escape(key) + "')")

        def delete(self, route, key):
            self.db.execute(
                "DELETE FROM " + self.TABLE_NAME + " WHERE route='" + route + "' AND key='" + escape(key) + "'")

        def get(self, route):
            cur = self.db.select("SELECT key FROM " + self.TABLE_NAME + " WHERE route = '" + route + "'")
            return cur.fetchall()

        def exists(self, route, key):
            cur = self.db.select(
                "SELECT * FROM " + self.TABLE_NAME +
                " WHERE route='" + route + "' AND key='" + escape(key) + "'")
            return cur.fetchone() is not None

    class Hidden(Pinned):
        TABLE_NAME = DB_TABLE.HIDDEN

    class Download:
        TABLE_NAME = DB_TABLE.DOWNLOAD

        def __init__(self):
            self.db = SQLiteStorage()
            self.db.execute(
                '''CREATE TABLE IF NOT EXISTS ''' + self.TABLE_NAME +
                ''' (id integer PRIMARY KEY autoincrement, ''' +
                '''path text, url text, title text, status text, percentage int, speed text, size int, ''' +
                '''subtitles_url text, media_id text, added text, completed text)''')

        def add(self, url, path, title, media_id, subs_included, subtitles_url=""):
            self.db.execute(
                "INSERT INTO '%s' (url, path, title, status, percentage, speed, subtitles_url, media_id, subs_included, added) VALUES ('%s', '%s', '%s', '%s', 0, '0', '%s', '%s', '%d', datetime('now', 'localtime'))" % (
                    self.TABLE_NAME, url, path, title, DOWNLOAD_STATUS.QUEUED, subtitles_url, media_id, subs_included))

        def delete(self, dl_id):
            self.db.execute("DELETE FROM " + self.TABLE_NAME + " WHERE id='" + dl_id + "'")

        def dl_update(self, download_id, percentage, speed, size):
            # no need to check for SQLi, because this is just local DB and we handle all the inputs
            # noinspection SqlInjection
            cmd = "UPDATE '%s' SET percentage='%s', speed='%s', size='%s', status='%s' WHERE id='%s'" \
                  % (self.TABLE_NAME, percentage, speed, size, DOWNLOAD_STATUS.DOWNLOADING, download_id)
            self.db.execute(cmd)

        def done(self, download_id):
            # noinspection SqlInjection
            cmd = "UPDATE '%s' SET percentage='100', status='%s', completed=datetime('now', 'localtime') WHERE " \
                  "id='%s'" % (self.TABLE_NAME, DOWNLOAD_STATUS.COMPLETED, download_id)
            self.db.execute(cmd)

        def get(self, dl_id):
            # noinspection SqlInjection
            cmd = "SELECT * FROM '{db}' WHERE id='{dl_id}'".format(db=self.TABLE_NAME, dl_id=dl_id)
            c = self.db.select(cmd)
            return c.fetchone()

        def get_by_media_id(self, media_id):
            # noinspection SqlInjection
            cmd = "SELECT * FROM '{db}' WHERE media_id='{media_id}'".format(db=self.TABLE_NAME, media_id=media_id)
            c = self.db.select(cmd)
            return c.fetchone()

        def exists(self, dl_id):
            return self.get(dl_id) is not None

        def get_all(self):
            # noinspection SqlInjection
            cmd = "SELECT * FROM '%s' ORDER BY id DESC" % self.TABLE_NAME
            c = self.db.select(cmd)
            return c.fetchall()

        def get_queued(self, limit=''):
            # noinspection SqlInjection
            if limit != '': limit = 'LIMIT {0}'.format(limit)
            cmd = "SELECT * FROM '{db}' WHERE status='{status}' ORDER BY id ASC {limit}".format(db=self.TABLE_NAME,
                                                                                                status=DOWNLOAD_STATUS.QUEUED,
                                                                                                limit=limit)
            c = self.db.select(cmd)
            return c.fetchall()

        def get_downloading(self):
            # noinspection SqlInjection
            cmd = "SELECT * FROM '{db}' WHERE status='{status}' ORDER BY id DESC".format(db=self.TABLE_NAME,
                                                                                         status=DOWNLOAD_STATUS.DOWNLOADING)
            c = self.db.select(cmd)
            return c.fetchall()

        def get_completed(self):
            # noinspection SqlInjection
            cmd = "SELECT * FROM '{db}' WHERE status='{status}' ORDER BY id DESC".format(db=self.TABLE_NAME,
                                                                                         status=DOWNLOAD_STATUS.COMPLETED)
            c = self.db.select(cmd)
            return c.fetchall()

        def get_paused(self):
            # noinspection SqlInjection
            cmd = "SELECT * FROM '{db}' WHERE status='{status}' ORDER BY id DESC".format(db=self.TABLE_NAME,
                                                                                         status=DOWNLOAD_STATUS.PAUSED)
            c = self.db.select(cmd)
            return c.fetchall()

        def get_by_filename(self, dest, name):
            cmd = "SELECT * FROM '{db}' WHERE path='{path}' AND title='{name}'".format(db=self.TABLE_NAME, path=dest,
                                                                                       name=name)
            c = self.db.select(cmd)
            return c.fetchone()

        def get_by_filename_status(self, dest, name, status):
            cmd = "SELECT * FROM '{db}' WHERE path='{path}' AND title='{name}' AND status='{status}'".format(
                db=self.TABLE_NAME, path=dest, name=name, status=status)
            c = self.db.select(cmd)
            return c.fetchone()

        def file_exists(self, dest, name):
            return self.get_by_filename(dest, name) is not None

        def is_completed(self, dl_id):
            cmd = "SELECT * FROM '{db}' WHERE id='{dl_id}' AND status='{status}'".format(db=self.TABLE_NAME,
                                                                                         dl_id=dl_id,
                                                                                         status=DOWNLOAD_STATUS.COMPLETED)
            c = self.db.select(cmd)
            return c.fetchone() is not None

        def status(self, dl_id, status):
            cmd = "SELECT * FROM '{db}' WHERE id='{dl_id}' AND status='{status}'".format(db=self.TABLE_NAME,
                                                                                         dl_id=dl_id, status=status)
            c = self.db.select(cmd)
            return c.fetchone() is not None

        def get_status(self, dl_id):
            cmd = "SELECT status FROM '{db}' WHERE id='{dl_id}'".format(db=self.TABLE_NAME, dl_id=dl_id)
            c = self.db.select(cmd)
            return c.fetchone()[0]

        def cancel_download(self, dl_id, status):
            cmd = "UPDATE '%s' SET percentage='%s', speed='%s', size='%s', status='%s' WHERE id='%s'" % (
                self.TABLE_NAME, 0, 0, 0, status, dl_id)
            self.db.execute(cmd)

        def set_status(self, dl_id, status):
            cmd = "UPDATE '%s' SET status='%s' WHERE id='%s'" % (self.TABLE_NAME, status, dl_id)
            self.db.execute(cmd)

        def change_status(self, from_status, to_status):
            cmd = "UPDATE '{db}' SET status='{status1}' WHERE status='{status2}'".format(db=self.TABLE_NAME,
                                                                                         status1=to_status,
                                                                                         status2=from_status)
            self.db.execute(cmd)

        def get_inactive(self):
            cmd = "SELECT * FROM '{db}' WHERE status!='{status}'".format(db=self.TABLE_NAME,
                                                                         status=DOWNLOAD_STATUS.DOWNLOADING)
            c = self.db.select(cmd)
            return c.fetchall()

        def delete_cancelled(self):
            cmd = "DELETE FROM '{db}' WHERE status='{status}'".format(db=self.TABLE_NAME,
                                                                      status=DOWNLOAD_STATUS.CANCELLED)
            self.db.execute(cmd)

    class WatchHistory:
        TABLE_NAME = DB_TABLE.WATCH_HISTORY

        def __init__(self):
            self.db = SQLiteStorage()
            self.db.execute(
                '''CREATE TABLE IF NOT EXISTS ''' + self.TABLE_NAME +
                ''' (media_id text PRIMARY KEY, watched text)''')

        def add(self, media_id, media_type):
            self.db.execute(
                "INSERT or REPLACE INTO " + self.TABLE_NAME + " VALUES ('" + media_id + "',datetime('now', 'localtime'),'" + media_type + "')")

        def delete(self, media_id=None):
            condition = ""
            if media_id:
                condition = " WHERE media_id = '" + media_id + "'"
            self.db.execute("DELETE FROM " + self.TABLE_NAME + condition)

        def delete_type(self, media_type=None):
            condition = ""
            if media_type:
                condition = " WHERE media_type = '" + media_type + "'"
            self.db.execute("DELETE FROM " + self.TABLE_NAME + condition)

        def get_all(self, media_type=None):
            where = " WHERE media_type = '" + media_type + "'" if media_type else ''
            cur = self.db.select("SELECT * FROM " + self.TABLE_NAME + where + " ORDER BY datetime(watched) DESC")
            return cur.fetchall()

        def update_many(self, items):
            self.db.update_many(self.TABLE_NAME, items)

        def get_media_types(self):
            cur = self.db.select(
                "SELECT media_type, MAX(watched) FROM " + self.TABLE_NAME + " GROUP BY media_type ORDER BY MAX(watched) DESC")
            return cur.fetchall()

        def count(self):
            c = self.db.select("select count(*) from " + self.TABLE_NAME)
            return c.fetchone()[0]

    class TraktListItems:
        TABLE_NAME = DB_TABLE.TRAKT_LIST_ITEMS

        def __init__(self):
            self.db = SQLiteStorage()
            self.db.execute(
                '''CREATE TABLE IF NOT EXISTS ''' + self.TABLE_NAME +
                '''(list_id TEXT,  item_type TEXT, trakt_id TEXT, PRIMARY KEY(list_id, item_type, trakt_id))''')
            self.db.execute('''''')

        def add(self, **kwargs):
            self.db.execute(
                *self.db.insert_or_replace(self.TABLE_NAME, **kwargs)
            )

        def get(self, item_type, trakt_id):
            cur = self.db.select('SELECT list_id FROM %s WHERE item_type = ? AND trakt_id = ?' % self.TABLE_NAME,
                                 item_type, trakt_id)
            vals = [i[0] for i in cur.fetchall()]

            return vals

        def get_item(self, item_type, trakt_id):
            cur = self.db.select('SELECT * FROM %s WHERE item_type = ? AND trakt_id = ?' % self.TABLE_NAME,
                                 item_type, trakt_id)
            return cur.fetchone()

        def get_list(self, list_id):
            cur = self.db.select('SELECT * FROM %s WHERE list_id = ? ' % self.TABLE_NAME,
                                 list_id)
            return cur.fetchall()

        def get_list_by_type(self, list_id, item_type):
            cur = self.db.select('SELECT * FROM %s WHERE list_id = ? AND item_type = ?' % self.TABLE_NAME,
                                 list_id, item_type)
            return cur.fetchall()

        def get_from_list(self, list_id, item_type, trakt_id):
            cur = self.db.select(
                'SELECT * FROM %s WHERE list_id = ? AND item_type = ? AND trakt_id = ?' % self.TABLE_NAME,
                list_id, item_type, trakt_id)
            return cur.fetchone()

        def get_show(self, show_id, item_type):
            cur = self.db.select('SELECT * FROM %s WHERE show_id = ? AND item_type = ?' % self.TABLE_NAME, show_id,
                                 item_type)
            return cur.fetchall()

        def remove_query(self, list_id, item_type, trakt_id, *args, **kwargs):
            return (
                'DELETE FROM %s WHERE list_id = ? AND item_type = ? AND trakt_id = ?' % self.TABLE_NAME,
                list_id, item_type, trakt_id)

        def remove(self, list_id, item_type, trakt_id):
            self.db.execute(*self.remove_query(list_id, item_type, trakt_id))

        def remove_list(self, list_id):
            self.db.execute('DELETE FROM %s WHERE list_id = ? ' % self.TABLE_NAME, list_id)

        def remove_many(self, items):
            service_logger.debug('Removing many items')
            self.db.multiexecute([self.remove_query(**item) for item in items])

        def remove_shows(self, show_ids):
            self.db.multiexecute(
                [('DELETE FROM %s WHERE show_id = ?' % self.TABLE_NAME, show_id) for show_id in show_ids])

        def update(self, items):
            self.db.update_many(self.TABLE_NAME, items)

    class TVShowsSubscriptions:
        TABLE_NAME = DB_TABLE.TV_SHOWS_SUBSCRIPTIONS

        def __init__(self):
            self.db = SQLiteStorage()
            self.db.execute(
                '''CREATE TABLE IF NOT EXISTS ''' + self.TABLE_NAME +
                '''(media_id text PRIMARY KEY,  library_path TEXT)''')

        def add(self, media_id, library_path):
            # if path exists, update media_id to actual one - in case DB data would changes after user add id's to data.db
            exists = self.db.select(
                "SELECT media_id FROM %s WHERE library_path = '%s'" % (self.TABLE_NAME, library_path)).fetchone()
            if exists:
                self.db.execute("UPDATE '%s' SET media_id = '%s' WHERE library_path = '%s'" % (
                    self.TABLE_NAME, media_id, library_path))
            else:
                self.db.execute(
                    "INSERT or REPLACE INTO " + self.TABLE_NAME + " VALUES ('" + media_id + "', '" + library_path + "')")

        def get_all(self):
            cur = self.db.select("SELECT * FROM " + self.TABLE_NAME)
            return cur.fetchall()

        def delete(self, media_id):
            self.db.execute("DELETE FROM " + self.TABLE_NAME + " WHERE media_id = '" + media_id + "'")

    class Files:
        TABLE_NAME = DB_TABLE.FILES

        def __init__(self):
            db_path = 'special://database'
            translated_path = translatePath(db_path)
            service_logger.debug('Database is located in: %s' % translated_path)
            translated_path = try_decode(translated_path)
            files = sorted(os.listdir(translated_path))
            service_logger.debug('Found DB files: %s' % ', '.join(files))
            videos_db_names = [file for file in files if file.startswith('MyVideos') and file.endswith(".db")]
            videos_db_name = videos_db_names[-1] if len(videos_db_names) > 0 else None

            if not videos_db_name:
                self.active = False
                return
            self.active = True
            self.db = SQLiteStorage(db_path, videos_db_name)

        @staticmethod
        def where_plugin():
            return "strFilename LIKE '%" + get_info('id') + "%'"

        def select(self, query, suffix=""):
            return self.db.select(
                query + (' WHERE ' if 'WHERE' not in query else ' AND ') + self.where_plugin() + suffix)

        def get_all(self):
            query = "SELECT * FROM %s" % self.TABLE_NAME + " WHERE strFilename LIKE '" + ROUTE.RESOLVE_MEDIA_ITEM + "%'"
            cur = self.select(query)
            return cur.fetchall()

        def get_unfinished(self):
            query = "SELECT * FROM %s" % self.TABLE_NAME + " LEFT JOIN bookmark on bookmark.idFile = files.idFile WHERE strFilename LIKE '" + ROUTE.RESOLVE_MEDIA_ITEM + "%'"
            query = query + " AND lastPlayed is not NULL"
            cur = self.select(query, " ORDER BY datetime(lastPlayed) DESC")
            return cur.fetchall()

        def get_finished(self):
            query = "SELECT * FROM %s" % self.TABLE_NAME + " WHERE (strFilename LIKE '" + ROUTE.RESOLVE_MEDIA_ITEM + "%'"
            query = query + " OR strFilename LIKE '" + ROUTE.RESOLVE_MEDIA_ITEM_CONFIG + "%')"
            query = query + " AND (playCount > 0)"
            cur = self.select(query, " ORDER BY datetime(lastPlayed) DESC")
            return cur.fetchall()

        def count(self):
            c = self.select("select count(*) from " + self.TABLE_NAME + " WHERE playCount IS NOT NULL")
            return c.fetchone()[0]

        def delete(self, media_id):
            self.db.execute("DELETE FROM " + self.TABLE_NAME + " WHERE strFilename LIKE '" + ROUTE.RESOLVE_MEDIA_ITEM + "%' AND strFilename LIKE '%media_id=" + media_id + "%'")

    class SearchHistory:
        TABLE_NAME = DB_TABLE.SEARCH_HISTORY

        def __init__(self):
            self.db = SQLiteStorage()
            self.db.execute(
                '''CREATE TABLE IF NOT EXISTS ''' + self.TABLE_NAME +
                ''' (value text PRIMARY KEY, last_search text NOT NULL, count INT DEFAULT 0)''')

        def add(self, value):
            value = escape(value)
            self.db.execute(
                "INSERT OR REPLACE INTO " + self.TABLE_NAME + " VALUES ('" + value + "', datetime('now', 'localtime'), ifnull((select count from " + self.TABLE_NAME + " where value = '" + value + "'), 0) + 1)")

        def get_all(self):
            cur = self.db.select(
                "SELECT * FROM " + self.TABLE_NAME + " ORDER BY datetime(last_search) DESC")
            return cur.fetchall()

        def delete_type(self, media_type=None):
            condition = ""
            if media_type:
                condition = " WHERE media_type = '" + media_type + "'"
            self.db.execute("DELETE FROM " + self.TABLE_NAME + condition)

        def delete(self, value):
            self.db.execute("DELETE FROM " + self.TABLE_NAME + " WHERE value = '" + value + "'")

    class Filters:
        TABLE_NAME = DB_TABLE.FILTERS

        def __init__(self):
            self.db = SQLiteStorage()
            self.db.execute(
                '''CREATE TABLE IF NOT EXISTS ''' + self.TABLE_NAME +
                ''' (id text PRIMARY KEY, config text NOT NULL)''')

        def add(self, config, id=None):
            self.db.execute(
                "INSERT OR REPLACE INTO " + self.TABLE_NAME + " VALUES ('" + (id or str(
                    uuid.uuid4())) + "', '" + config + "')")

        def get(self, id):
            cur = self.db.select(
                "SELECT * FROM " + self.TABLE_NAME + " WHERE id = '" + id + "'")
            return cur.fetchone()

        def get_all(self):
            cur = self.db.select(
                "SELECT * FROM " + self.TABLE_NAME)
            return cur.fetchall()

        def delete(self, id):
            self.db.execute("DELETE FROM " + self.TABLE_NAME + " WHERE id = '" + id + "'")

    class WatchHistoryAdvanced:
        TABLE_NAME = DB_TABLE.WATCH_HISTORY_ADVANCED

        def __init__(self):
            self.db = SQLiteStorage()
            self.db.execute(
                '''CREATE TABLE IF NOT EXISTS ''' + self.TABLE_NAME +
                ''' (media_id text PRIMARY KEY,
                    media_path text,
                    parent_id text,
                    root_parent_id text,
                    season INTEGER,
                    episode INTEGER,
                    last_played text,
                    finished INTEGER)''')

        def add_query(self, media_id, media_path, parent_id=None, root_parent_id=None, season=None, episode=None, last_played=None, finished=None):
            return "INSERT OR REPLACE INTO " + self.TABLE_NAME + " VALUES (?,?,?,?,?,?,?,?)", media_id, media_path, parent_id, root_parent_id, season, episode, last_played, finished,

        def add(self, *args):
            self.db.execute(self.add_query(*args))

        def add_many(self, items):
            self.db.multiexecute([self.add_query(*i) for i in items])

        def get_by_root(self, root_id):
            cur = self.db.select(
                "SELECT * FROM " + self.TABLE_NAME + " WHERE root_parent_id = '" + root_id + "'")
            return cur.fetchall()

        def get_all(self):
            cur = self.db.select(
                "SELECT * FROM " + self.TABLE_NAME + " ORDER BY datetime(last_played) DESC")
            return cur.fetchall()

        def get_all_unfinished(self):
            cur = self.db.select(
                "SELECT * FROM " + self.TABLE_NAME + " WHERE finished is NULL ORDER BY datetime(last_played) DESC")
            return cur.fetchall()

        def get_last(self, root_parent_id, finished=True):
            finished = 'not' if finished else ''
            cur = self.db.select(
                "SELECT * FROM " + self.TABLE_NAME + " WHERE root_parent_id = '" + root_parent_id + "' AND finished is " + finished + " NULL ORDER BY season DESC, episode DESC")
            return cur.fetchone()

        def get_first(self, root_parent_id, finished=True):
            finished = 'not' if finished else ''
            cur = self.db.select(
                "SELECT * FROM " + self.TABLE_NAME + " WHERE root_parent_id = '" + root_parent_id + "' AND finished is " + finished + " NULL ORDER BY season ASC, episode ASC")
            return cur.fetchone()

        def delete(self, *media_ids):
            self.db.execute("DELETE FROM " + self.TABLE_NAME + " WHERE media_id IN (\"" + "\",\"".join(*media_ids) + "\")")

        def delete_root(self, *media_ids):
            self.db.execute("DELETE FROM " + self.TABLE_NAME + " WHERE root_parent_id IN (\"" + "\",\"".join(*media_ids) + "\")")

        def delete_by_path(self, *media_paths):
            self.db.execute("DELETE FROM " + self.TABLE_NAME + " WHERE media_path IN (" + ",".join(*media_paths) + ")")

        def update_state_query(self, media_path, last_played, finished):
            return "UPDATE '" + self.TABLE_NAME + "' SET last_played=?, finished=? WHERE media_path=?", last_played, finished, media_path

        def update_state(self, *args):
            self.db.execute(self.update_state_query(*args))

        def update_state_many(self, items):
            self.db.multiexecute([self.update_state_query(*i) for i in items])

    class History:
        TABLE_NAME = DB_TABLE.HISTORY

        def __init__(self):
            self.db = SQLiteStorage()
            self.db.execute(
                '''CREATE TABLE IF NOT EXISTS ''' + self.TABLE_NAME +
                ''' (ident text PRIMARY KEY, valid INTEGER)''')

        def add(self, ident, exists):
            self.db.execute("INSERT or REPLACE INTO " + self.TABLE_NAME + " VALUES ('" + ident + "', " + ('1' if exists else '0') + ")")

        def get(self, ident):
            cur = self.db.select("SELECT * FROM " + self.TABLE_NAME + " WHERE ident = '" + ident + "'")
            return cur.fetchone()

        def get_all(self):
            cur = self.db.select("SELECT * FROM " + self.TABLE_NAME)
            return cur.fetchall()

        def delete(self, *idents):
            self.db.execute("DELETE FROM " + self.TABLE_NAME + " WHERE ident IN (\"" + "\",\"".join(*idents) + "\")")


sql = SQLiteStorage()

try:
    sql.update(pre_updates)
except sqlite3.OperationalError as err:
    service_logger.error('DB update failed: %s' % err)


class DB:
    WATCH_HISTORY = SQLiteStorage.WatchHistory()
    PINNED = SQLiteStorage.Pinned()
    DOWNLOAD = SQLiteStorage.Download()
    TRAKT_LIST_ITEMS = SQLiteStorage.TraktListItems()
    TV_SHOWS_SUBSCRIPTIONS = SQLiteStorage.TVShowsSubscriptions()
    HIDDEN = SQLiteStorage.Hidden()
    FILES = SQLiteStorage.Files()
    SEARCH_HISTORY = SQLiteStorage.SearchHistory()
    FILTERS = SQLiteStorage.Filters()
    WATCH_HISTORY_ADVANCED = SQLiteStorage.WatchHistoryAdvanced()
    HISTORY = SQLiteStorage.History()


try:
    sql.update(updates)
except sqlite3.OperationalError as err:
    service_logger.error('DB update failed: %s' % err)
sql.set_version(CURRENT_USER_VERSION)
del sql
