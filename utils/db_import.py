import argparse
import sqlite3

########################### EDIT THIS SCRIPT FOR YOUR OWN PURPOSE ######################################
# Script made to import records from other databases into chaos database
# Make sure to know which index in rows corresponds to desired fields 
# "source" and "destination" are database names/paths
# "source_table_name" is a table where we want po pick records from
parser = argparse.ArgumentParser()
parser.add_argument('-s', '--source', help='')
parser.add_argument('-d', '--destination',  help='')
parser.add_argument('-t', '--source_table_name',  help='')
args = parser.parse_args()


def stats_table_import():
    temp_list = read_db()
    
    with sqlite3.connect(args.destination) as dest_db:
        c = dest_db.cursor()
        for row in temp_list:
            # EDIT ROWS INDEXES
            # `author`	TEXT NOT NULL,
            # `month_num`	INTEGER NOT NULL,
            # `day_num`	INTEGER NOT NULL,
            # `day_week`	INTEGER NOT NULL,
            # `year`	INTEGER NOT NULL,
            # `hour`	INTEGER NOT NULL
            c.execute('INSERT INTO "stats" ("author" , "month_num" , "day_num" , "day_week" , "year" , "hour") '
                      'VALUES (?, ?, ?, ?, ?, ?)', (row[0], row[1], row[2], row[3], row[4], row[5]))
        dest_db.commit()
        c.close()


def quote_table_import():
    temp_list = read_db()
    with sqlite3.connect(args.destination) as dest_db:
        c = dest_db.cursor()
        for row in temp_list:
            # EDIT ROWS INDEXES
            #            `id`	INTEGER PRIMARY KEY AUTOINCREMENT,
            #        	 `quote`	TEXT NOT NULL,
            #        	 `time`	TEXT NOT NULL,
            #            `author`    TEXT NOT NULL,
            #            `author_id`    INTEGER NOT NULL
            c.execute('INSERT INTO quotes ("quote","time","author","author_id") VALUES (?, ?, ?, ?)',
                      (row[0], row[1], row[2], row[3]))
        dest_db.commit()
        c.close()


def read_db():
    temp_list = list()
    i = 0
    with sqlite3.connect(args.source) as source_db:
        c = source_db.cursor()
        for row in c.execute(f'SELECT * FROM {args.source_table_name}'):
            temp_list.append(row)
            # Change this to have a look on source database records
            if i % 1000 == 0:
                print(row)
            i += 1
        source_db.commit()
        c.close()
    return temp_list

#stats_table_import()
#quote_table_import()