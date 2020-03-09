#!/usr/bin/env python3

"""Process scanned files to identify the precinct and page number.

   This a main program can be run in multiple parallel process.

   Review the database for rows in Images that have not yet had this info filled in.
   Decode the barcodes and translate the numbers into precinct IDs
   Write the information back to the database."""

# todo: potentially huge time saving in https://stackoverflow.com/questions/48281086/extracting-a-region-of-interest-from-an-image-file-without-reading-the-entire-im/48376269#48376269

import dbase
import datetime
from election_paramaters.pctids_2018_11 import pctids_2018_11
from ETP_util import fullpath_to_image, subpath_to_image
import GLB_globals
import etpconfig
from HARTgetBallotType import HARTgetBallotType, pct_id, page_num, b2str
import os
import signal
import sys
import time

TESTING = True
pid = os.getpid()

global stopflag
stopflag= False

def intHandler(x, y):
    print(pid, 'interruption', x, y)
    global stopflag
    stopflag = True

signal.signal(signal.SIGINT, intHandler)

if __name__ == '__main__':
    GLB = GLB_globals.get()
    config = GLB.config
    PATH_TO_IMAGES = config['Election']['pathtoimages']
    tot_processed = 0
    start_time = datetime.datetime.now()

    if TESTING:
        db = dbase.ETPdb()
        db.connect('testing')

    else:
        db = dbase.ETPdb()
        db.connect('production')

    with HARTgetBallotType() as hgbt:
        tries = 0
        while True:
            # get a list of rows to fix
            #
            tries += 1
            # print(f'{pid} trying {tries}', file=sys.stderr)
            # print(f'{pid} trying {tries}', )
            rows_to_fix = db.get_images_for_barcode(pid, 10)      # batch of 10
            if tries != 1: raise Exception
            tries -=1
            # print(f'{pid} getting {tries}')
            # print(f'{pid} getting {tries}', file=sys.stderr)
            fixes = [] # tuples of (precinct, page_number, image_number)
            for row in rows_to_fix:
                image_num = row.image_number
                # print(f'yyy{image_num}')
                pth = fullpath_to_image(image_num)
                # print(f'zzz{pth}')
                barcode = b2str(hgbt.getBallotType(pth))
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

            time.sleep(.05)     # avoid starving the UI
            tot_processed += len(fixes)
            if len(fixes) != 0:
                print(pid, 'processed', tot_processed, datetime.datetime.now() - start_time)
            db.update_unscanned_images(fixes)
            if stopflag:
                t = datetime.datetime.now() - start_time
                print(f'===> pid {pid} exiting after interrupt, total processed={tot_processed}, time={t}')
                exit(0)

            # t = .20 starves the UI in fast simulation. Probably not in operation
            t = .25 if len(fixes) != 0 else 1.0
            print(f'{pid} dozing')
            time.sleep(t) # give other processes a chance

