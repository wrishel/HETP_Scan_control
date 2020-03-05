"""Process scanned files to identify the precinct and page number.

   This a main program can be run in multiple parallel process.

   Review the database for rows in Images that have not yet had this info filled in.
   Decode the barcodes and translate the numbers into precinct IDs
   Write the information back to the database."""

import dbase
from election_paramaters.pctids_2018_11 import pctids_2018_11
from ETP_util import fullpath_to_image, subpath_to_image
import GLB_globals
from HARTgetBallotType import HARTgetBallotType, pct_id, page_num, b2str
import signal
import time

SIGINT = 2
TESTING = True
BATCH_SIZE = 5

global stopflag
stopflag= False

def intHandler():
    global stopflag
    stopflag = True

def process_barcodes(db):
    signal.signal(SIGINT, intHandler)



if __name__ == '__main__':
    GLB = GLB_globals.get()
    GLB.set_object_instances()
    config = GLB.config
    PATH_TO_IMAGES = config['Election']['pathtoimages']

    if TESTING:
        db = dbase.ETPdb(dbase.test_dbconfig)

        # create test data
        # db.recreate_images()
        # with open('test_data/test1_for_process_barcodes.py.sql') as inf:
        #     s = inf.read()
        #     db.exe_script(s)

    else:
        db = dbase.ETPdb(dbase.dbconfig)



    while True:
        with HARTgetBallotType() as hgbt:
            if stopflag:
                exit(0)

            # get a list of rows to fix
            #
            rows_to_fix = db.get_images_for_barcode(10)      # batch of 10
            fixes = [] # tuples of (precinct, page_number, image_number)
            for row in rows_to_fix:
                image_num = row.image_number
                pth = fullpath_to_image(image_num) + '.jpg'    # todo: fails if scanner returns .JPEG
                barcode = '000001' # b2str(hgbt.getBallotType(pth))
                if barcode is not None:
                    try:
                        precinct = pctids_2018_11[pct_id(barcode)]
                        pagenum = page_num(barcode)

                    except KeyError:
                        precinct = 'UNKNOWN'
                        pagenum = 'UNK'

                    fixes.append((precinct, pagenum, image_num))

                else:
                    precinct = 'UNKNOWN'
                    pagenum = 'UNK'

            print(len(fixes))
            db.update_unscanned_images(fixes)

            time.sleep(.1) # give parallel processes a chance
