## Connecting to the database

## importing 'mysql.connector' as mysql for convenient
import mysql.connector as mysql



def create_table():
    query = u"""CREATE TABLE IF NOT EXISTS fiddlin.employees (
    id INT NOT NULL AUTO_INCREMENT,
    fname VARCHAR(30),
    lname VARCHAR(30),
    hired DATE NOT NULL DEFAULT '1970-01-01',
    separated DATE NULL,
    job_code CHAR(3) NOT NULL,
    store_id INT NOT NULL,
    PRIMARY KEY (id))"""

    cursor = cnx.cursor()
    cursor.execute(query)
    cursor.close()
    # cnx.commit()
    print("Created table")

def get_one():
    mycursor = cnx.cursor()
    mycursor.execute("SELECT * FROM fiddlin.employees")
    myresult = mycursor.fetchall()
    print(len(myresult), 'rows')
    for x in myresult:
        print(x)

def add_one(fname, lname):
    sqlstr = u"""INSERT INTO fiddlin.employees (fname, lname, job_code, store_id) 
                 VALUES (%s, %s, %s, %s)"""
    val = (fname, lname, "JBC", 7)
    cursor = cnx.cursor()
    cursor.execute(sqlstr, val)
    # cnx.commit()


def delete_all_rows():
    query = u"""delete from employees"""

    # cnx = mysql
    cursor = cnx.cursor()
    cursor.execute(query)
    cursor.close()
    # cnx.close()
    # cnx.commit()
    print( "Deleted all rows")



## connecting to the database using 'connect()' method
## it takes 3 required parameters 'host', 'user', 'passwd'
cnx = mysql.connect(
    host = "localhost",
    user = "root",
    passwd = "Hetp2020",
    database = 'fiddlin'
)
print(cnx) # it will print a connection object if everything is fine
create_table()
get_one()
add_one('Family', 'Cutekidsname')
get_one()
cnx.commit()
delete_all_rows()
cnx.commit()

