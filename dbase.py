"""Interface to MySQL database.

"""
from collections.abc import Iterable
import sys
import mysql.connector as dbase
from mysql.connector.constants import ClientFlag
import GLB_globals
GLB = GLB_globals.get()

# passwords are buried here rather than being in the .ini file -- somewhat pointless, I know

dbconfig = {
    "user": "etp",
    "password": "Hetp2020",
    "database": "HETP"
}
test_dbconfig = {
    "user": "ETP",
    "password": "Hetp2020",
    "database": "HETPtesting"
}

# todo: polishing: should be an enum for testing or production rather then sloppy strings

class ETPdb():
    """Interface to MySQL database.

       As a general rule, rows are returned as namedtuples."""

    def __init__(self):
        self.GLB_name = 'db'

    def connect(self, db_choice):
        """Create connection.
        
           db_choice says whether to use the test or production database"""
        self.tracing_sql = GLB.config.get_or_else('Debugging','get_bool_or', False)
        if db_choice == 'testing':
            db_credentials = test_dbconfig
        elif db_choice == 'production':
            db_credentials = dbconfig
        else:
            assert False, f'unknown database choice: "{db_choice}"'

        self.cnx = dbase.connect(**db_credentials)
        # if db_choice == 'testing' and \
        #             GLB.config.get_bool_or('Debugging', 'clear_db_on_start', False):
        #         self.recreate_images()


    # -------------------------------  Server interactions  -------------------------------

    def exe(self, sql, indata=None, multi=False, commit=False):
        """Execute sql with no return values. Cursor is defined in an arg to enable
           optional return of rows as dicts."""

        if self.tracing_sql:
            print(sql)
            if indata:
                print(indata)
        cursor = self.cnx.cursor(named_tuple=True)
        if indata:
            ret = cursor.execute(sql, indata, multi)
        else:
            ret = cursor.execute(sql)
        cursor.close()
        if commit:
            self.cnx.commit()
        return ret

    def exe_many(self, sql, indata):
        """Execute sql indata and commit."""

        if self.tracing_sql:
            print(sql)
            print(indata)
        cursor = self.cnx.cursor(named_tuple=True)
        ret = cursor.executemany(sql, indata)
        cursor.close()
        self.cnx.commit()
        return ret

    def exe_script(self, sqliter):
        """Execute a sequence of lines from sqliter. Always commits at the end."""

        if self.tracing_sql:
            print(sql)
        cursor = self.cnx.cursor()
        for s in sqliter.split('\n'):
            ret = cursor.execute(s)

        cursor.close()
        self.cnx.commit()

    def retrieve(self, sql):
        """Execute sql and return list of dicts."""

        if self.tracing_sql:
            print(sql)
        cursor = self.cnx.cursor()
        try:
            cursor.execute(sql)
        except Exception as e:
            print(f'exception in retireve{e}, sql={sql}')
            raise e
        res = cursor.fetchall()
        cursor.close()
        return res

    def retrieve_tuples(self, sql):
        """Execute sql and return list."""

        if self.tracing_sql:
            print(sql)
        cursor = self.cnx.cursor(named_tuple=True)
        cursor.execute(sql)
        res = cursor.fetchall()
        cursor.close()
        return res

    # -----------------------------  Application services  ----------------------------

    def add_image_nums(self, elections_batch_num, image_nums):
        """Add a new row to Images with only the image_number and elections_batch_num.

           elections_batch_num: str
           image_nums:  int, str or iterable of ints and strs"""

        if not isinstance(image_nums, Iterable):
            image_nums = (image_nums,)
        data = list()
        for item in image_nums: data.append((int(item), elections_batch_num))
        sql =  """INSERT INTO Images (image_number, elections_batch_num) VALUES (%s, %s)"""
        r = None
        try:
            r = self.exe_many(sql, data)
        except Exception as e:
            print('error exception:', e)
        return r

    def add_images(self, data):
        """Insert images into table.

        Call with data as a list of tuples
            (image number, precinct, page_number, elections_batch_num, ETP_batch_num"""

        sql =  """INSERT INTO Images 
               (image_number, precinct, page_number, elections_batch_num, ETP_batch_num) 
               VALUES (%s, %s, %s, %s, %s)"""
        return self.exe_many(sql, data)

    def delete_images(self, data):
        """Delete a list of images from the table.

        data: an interable of image_number"""

        if not isinstance(data, Iterable):
            data = (data,)
        d = tuple(data)
        num_list = ','.join((str(x) for x in d))
        sql =  f"""DELETE from Images WHERE image_number in ({num_list})"""
        r = None
        try:
            r = self.exe(sql, commit=True)
        except Exception as e:
            r = e
            print('error exception in dbase:', e, file=sys.stderr)
        return r



    def fix_orphaned_rows(self):
        """Abnormal shutdown scenarios can leave rows checked out for get_images_for_barcode(). Run
           this once when nothing else is accessing the database to reset those rows."""

        sql = f'''UPDATE Images SET assigned_to_pid = NULL 
                        WHERE assigned_to_pid IS NOT NULL AND precinct IS NULL'''

        return self.exe(sql, commit=True)

    def get_images(self, iterable):
        """Return a list of image IDs"""

        t = tuple(iterable)
        sql = f"SELECT * FROM Images WHERE image_number IN {str(iterable)}"
        return self.retrieve(sql)

    def get_images_for_barcode(self, pid, num):
        """Get rows from Images that need the precinct ID.

           To enable parallel processing this finds candidate rows and locks them
           by putting the process ID in assigned_to_pid. Once this is done, parallel
           calls to this routine should skip rows."""

        # self.retrieve_tuples(s)         # clear the cursor
        cursor = self.cnx.cursor(named_tuple=True)
        sql = f'''UPDATE Images SET assigned_to_pid = {pid} 
                        WHERE assigned_to_pid IS NULL AND precinct IS NULL
                        LIMIT {num}'''

        self.exe(sql,commit=True)
        sql = f'SELECT * FROM Images WHERE assigned_to_pid = {pid}'
        return self.retrieve_tuples(sql)

    def get__get_lock_images_no_pagenum(self, max=None, pid='???'):
        """Return a list of image IDs where the row in the table has no page number.

           Those rows are 'locked' by putting pid in the assigned_to_pid. This
           locking is an application concept, not related to the database's locking.
        """

        if max is None:
            sql = '''SELECT * FROM Images WHERE page_number IS NULL '''
        else:
            sql = f'''SELECT * FROM Images WHERE page_number IS NULL LIMIT {max}'''
        return self.retrieve_tuples(sql)

    def get_highest_image_num(self) -> int:

        sql = f"""select max(image_number) from Images"""
        try:
            x = self.retrieve(sql)
        except Exception as e:
            raise e
        rv =  x[0][0]
        if rv is None: rv = -1
        return rv

    def get_page_report(self):
        """Get the data for the pages report."""

        sql = """drop table if exists temp_counts"""
        self.exe(sql, commit=True)
        sql = """
        CREATE TABLE temp_counts AS
            select precinct,
                COUNT(if(page_number = '1', 1, NULL)) as page_1,
                COUNT(if(page_number = '2', 1, NULL)) as page_2,
                COUNT(if(page_number = '3', 1, NULL)) as page_3,
                COUNT(if(page_number = '4', 1, NULL)) as page_4,
                COUNT(if(page_number = 'UNK', 1, NULL)) unknown,
                group_concat(distinct elections_batch_num) as elections_nums
            from Images
            group by precinct"""
        self.exe(sql, commit=True)

        sql = """
        select precinct, page_1, page_2, page_3, page_4, unknown,
               page_1 + page_2 + page_3 + page_4 + unknown as total_pages,
               elections_nums
            from temp_counts
            order by precinct;"""
        return self.retrieve_tuples(sql)

    def recreate_images(self):
        """Drop and redefine the images table."""

        self.exe("""DROP TABLE IF EXISTS Images""")
        self.exe("""CREATE TABLE IF NOT EXISTS Images (
                        image_number MEDIUMINT NOT NULL,
                        precinct VARCHAR(7),            # UNKNOWN means scanning failed
                        page_number VARCHAR(3) NULL,    # UNK means scanning failed
                        elections_batch_num VARCHAR(6),
                        ETP_batch_num VARCHAR(6),
                        assigned_to_pid MEDIUMINT NULL, # pid handling during parallel scanning
                        PRIMARY KEY (image_number))""")
        self.cnx.commit()

    def update_unscanned_images(self, update_data):
        """Update the images that were previousy unscanned.

           Call with tuples of (precinct, page_number, image_number)"""

        sql = "UPDATE  Images SET precinct = %s, page_number=%s, assigned_to_pid = NULL " \
              "WHERE image_number = %s"
        self.exe_many(sql, update_data)

GLB.register(ETPdb())

if __name__ == '__main__':
    from random import randint, seed
    import collections

    # Named tuple for a result of selection from Images
    #
    Exp_img_row = collections.namedtuple('Exp_img_row',
                                         'image_number precinct page_number '
                                         'electionos_batch_num ETP_batch_num '
                                         'assigned_to_pid')

    seed(2)         # initiallze random for repeatable test results
    db = ETPdb()
    db.connect('testing')
    db.tracing_sql = False      # omit this to see all SQL statements executed

    # test add_image_nums
    db.recreate_images()        # create a blank Images table
    db.add_image_nums(12345, (1,'2'))
    db.add_image_nums(12346, 3)
    db.add_image_nums(12346, '4')

    sql = '''SELECT * FROM IMAGES'''
    ret = db.retrieve(sql)
    assert len(ret) == 4
    indxs = range(4)
    for i in indxs:
        assert ret[i][0] == i + 1

    db.delete_images((2,))
    sql = '''SELECT * FROM IMAGES'''
    ret = db.retrieve(sql)
    assert len(ret) == 3
    assert ret[0][0] == 1
    assert ret[1][0] == 3
    assert ret[2][0] == 4

    db.delete_images(('1',4))
    sql = '''SELECT * FROM IMAGES'''
    ret = db.retrieve(sql)
    assert len(ret) == 1
    assert ret[0][0] == 3

    # test add_images
    db.recreate_images()        # create a blank Images table
    db.recreate_images()        # create a blank Images table
    data = []
    for x in range(15):
        data.append((
            x,
            ('2-CS', '1-CS4', 'ABCD-1','2-CS', '1-CS4', 'ABC', 'UNKNOWN')[randint(0,6)],
            (1, 2, 3, 4, 1, 2, 3, 4, None, 'UNK', None)[randint(0,10)],
            '31',
            '5'))

    db.add_images(data)
    no_page_num = db.get__get_lock_images_no_pagenum()
    assert len(no_page_num) == 5

    # expected result for random data with seed == 2
    #
    expected_value = Exp_img_row(12, '2-CS', None, '31', '5', None)
    assert no_page_num[4] == expected_value
    update_list = []
    for x in no_page_num:
        update_list.append(
            (('2-CS', '1-CS4', 'ABCD-1','2-CS', '1-CS4', 'ABC', 'UNKNOWN')[randint(0,6)],
             (1, 2, 3, 4, 1, 2, 3, 4, 'UNK')[randint(0, 8)],
             x.image_number)
        )
    db.update_unscanned_images(update_list)
    x = db.get_images((0,14))
    ev0 = Exp_img_row(0, 'UNKNOWN', '1', '31', '5', None)
    ev1 = Exp_img_row( 14, 'UNKNOWN', '1', '31', '5', None)
    expected_value = [ev0, ev1]
    assert x == expected_value

    x = db.get_page_report()
    expected_value = [('1-CS4', 0, 0, 0, 1, 2, 3, '31'),
                      ('2-CS', 0, 1, 0, 0, 2, 3, '31'),
                      ('ABC', 0, 0, 1, 0, 0, 1, '31'),
                      ('ABCD-1', 1, 0, 2, 1, 1, 5, '31'),
                      ('UNKNOWN', 3, 0, 0, 0, 0, 3, '31')]

    assert x == expected_value
    db.recreate_images()    # leave database empty after testing
