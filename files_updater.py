# -*- coding: utf-8 -*-
from database_connector import *
import labeling

def crawling_batch():

    folder_data, exifs_data = glob.get_file_list(config_t.path_full_master)

    # print 'before call', folder_data
    print 'List of files collected'
    # insert files and hash into db
    insert_files_db(folder_data)

    # insert exifs
    insert_exif(exifs_data)

    if config_t.DEBUG:
        print 'remove duplicates'

    # remove identical hash records
    remove_duplicates_db()


def adult_stuff_batch():
    if config_t.DEBUG:
        print 'start adult check, get all unlabelled hash'
    #labeling

    folder_data = get_all_unlabelled_adult()

    if config_t.DEBUG:
        print 'start adult labeling loop for '+ str(len(folder_data))

    for index, files in enumerate(folder_data):
        print 'detection for ', files[0]

        print round(100.0 * index / len(folder_data))

        insert_meta(labeling.detect_safe_search_uri(files[1], files[2]))



def adult_stuff_batch_multi():
    from threading import Thread

    if config_t.DEBUG:
        print 'start adult check, get all unlabelled hash'
    folder_data = get_all_unlabelled_adult()

    print len(folder_data)
    def try_one_operation( file):

        print 'detection for ', file[0]
        insert_meta(labeling.detect_safe_search_uri(file[1], file[2]))

    index = 0

    while  index < len (folder_data):
        print  str( round (index*100.0 / len(folder_data), 1)) + '%'

        t1 = Thread(target=try_one_operation, args=[folder_data[index]])
        t1.start()

        try:
            t2 = Thread(target=try_one_operation, args=[folder_data[index + 1]])
            t2.start()

        except:
            print 'issue with ', index+1
            break

        try:
            t3 = Thread(target=try_one_operation, args=[folder_data[index + 2]])
            t3.start()

        except:
            print 'issue with ', index+2
            break

        try:
            t4 = Thread(target=try_one_operation, args=[folder_data[index + 3]])
            t4.start()

        except:
            print 'issue with ', index+3
            break

        try:
            t5 = Thread(target=try_one_operation, args=[folder_data[index + 4]])
            t5.start()

        except:
            print 'issue with ', index+4
            break

        t1.join()
        t2.join()
        t3.join()
        t4.join()
        t5.join()

        index += 5


def labeling_batch_multi():
    from threading import Thread

    if config_t.DEBUG:
        print 'start labeling, get all unlabelled hash'
    folder_data = get_all_unlabelled()

    print len(folder_data)
    def try_one_operation( file):

        print 'detection for ', file[0]
        insert_label(labeling.detect_label(file[1], file[2]))

        # TODO insert_meta_gps_from_tag
        insert_meta(glob.get_tags_from_txt(file[1][:-len(file[0]) - 1], file[2]))


    index = 0

    while  index < len (folder_data):
        print  str( round(index*100.0 / len(folder_data), 1) ) + '%'

        t1 = Thread(target=try_one_operation, args=[folder_data[index]])
        t1.start()

        try:
            t2 = Thread(target=try_one_operation, args=[folder_data[index + 1]])
            t2.start()

        except:
            print 'issue with ', index+1
            break

        try:
            t3 = Thread(target=try_one_operation, args=[folder_data[index + 2]])
            t3.start()

        except:
            print 'issue with ', index+2
            break

        try:
            t4 = Thread(target=try_one_operation, args=[folder_data[index + 3]])
            t4.start()

        except:
            print 'issue with ', index+3
            break

        try:
            t5 = Thread(target=try_one_operation, args=[folder_data[index + 4]])
            t5.start()

        except:
            print 'issue with ', index+4
            break

        t1.join()
        t2.join()
        t3.join()
        t4.join()
        t5.join()

        index += 5




def labeling_batch():
    if config_t.DEBUG:
        print 'start labeling, get all unlabelled hash'
    #labeling
    folder_data = get_all_unlabelled()

    if config_t.DEBUG:
        print 'start labeling loop'


    for index, files in enumerate(folder_data):
        print '\ndetection for ', files[0]

        print round(100.0 * index / len(folder_data))

        insert_label(labeling.detect_label(files[1], files[2]))

        # TODO insert_meta_gps_from_tag
        insert_meta(glob.get_tags_from_txt(files[1][:-len(files[0]) - 1], files[2]))
        # TODO insert_adult

if __name__ == '__main__':
    import requests

    requests.get('https://google.com/')

    init_db()
    crawling_batch()

    labeling_batch_multi()

    adult_stuff_batch_multi()