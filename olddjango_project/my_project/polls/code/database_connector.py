# -*- coding: utf-8 -*-

import mysql.connector
import config_t
import MySQLdb


cnx = mysql.connector


def init_db():
    '''init db and update cnx'''
    global cnx
    cnx = mysql.connector.connect(user=config_t.user, password=config_t.password, host=config_t.host,
                                   database=config_t.database)   

def get_freq_labels():
    global cnx

    cursor = cnx.cursor()

    cursor.callproc('''get_frequent_labels''')
    cnx.commit()

    for result in cursor.stored_results():
        people=result.fetchall()
        
    return people
	
	
	
								   
if __name__ == '__main__':
    init_db()
    print get_freq_labels()

    cnx.close()
