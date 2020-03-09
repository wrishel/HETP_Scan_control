
"""Scan ballot images for TEVS, setting parameters for the Fujitsu 5900-c scanner.

   We do not assume that the prior batch ended properly. That is to say, when
   we start up there may be images from a prior run still in self.incomingdir.

   These will get copied to the output dirtree on the first timer interrupt.

   Based strongly on TEVS routine written by Mitch Trachtenberg.
"""

from batch import Batch_status
import copy
from datetime import datetime
import etpconfig    # accessed through GLB_globals; imported for IDE support
from enum import IntFlag, auto
from ETP_util import fullpath_to_image , subpath_to_image
import glob
import logging      # to do. Is this working? Change to my logging?
import os
import os.path
import q_util       # will be accessed through GLB
import re
import shutil
import subprocess
import sys
import threading    # thread for timing
import time

import GLB_globals
GLB = GLB_globals.get()

DEFER_COPY_SECS = 10.0 # During scanning, defer copying files to output for this long

def makedirsok(path):
    try:
        os.makedirs(path)
    except OSError as e:
        if e.errno != 17: raise e

def del_dir_contents(dir):
    """Delete all the contents of dir, but leave dir in place."""

    for filename in os.listdir(dir):
        file_path = os.path.join(dir, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e), file=sys.stderr)

# todo: polishing: move Batch_status to a separate source file

class Scan_HW_Control:
    """Control the hardware scanner by starting the linux scanimage command as a subprocess.

       While scanimage running copy images from the temp dir where the scanner deposits
       images to the official directory.

       Determine if the scanner has stopped if no new images appear in the output directory
       for 5 seconds.

       If self.simulating is true, the scanner doesn't run and images are served
       up from what would otherwise be the output directory tree.

       NB: This object contains some thread code which calls methods not unique to the thread.
           We think this is save because the module never runs its main code and a thread
           at the same time, and never runs both threads at the same time.

           We also hope we are getting help from the GIL.
    """

    dirnnn = re.compile(r'\d\d\d$')

    def __init__(self):
        self.bsb = GLB.batch_status  # batch status block
        self.lenmm = str(int(25.4 * int(GLB.config["ballot"]["length"]) + 0.5))
        self.dpi = GLB.config["ballot"]["dpi"]
        self.outdirtree = GLB.config["Election"]["pathtoimages"]
        self.incomingdir = GLB.config["Election"]["scannertempdir"]  # todo: add to sys_admin
        self.timer_thread = None
        self.simulating = GLB.config['Scanning']['simulating']
        self.complete_sig = GLB.signals.scan_complete
        self.scan_error_sig = GLB.signals.scan_error
        self.scan_update = GLB.signals.scan_update
        self.sim_scanner_speed = 0.1  # when simulating, the delay between "scanned" sheets in seconds

    def init_more(self):
        """call to finish initialization after all global objects have been initialized"""

        high_img_num_db = GLB.db.get_highest_image_num()
        if high_img_num_db is None: hin = -1
        if self.simulating:
            self.bsb.next_seq_num_in_batch = high_img_num_db
            # self.bsb.first_seq_num_in_batch = hin
            # self.bsb.next_seq_num_in_batch = hin

        else:
            high_img_num_dirtree = self.find_high_water()

            # check for an edge condition: images were scanned but didn't get in database
            if high_img_num_dirtree > high_img_num_db:
                imgs = (n for n in range(high_img_num_db + 1, high_img_num_dirtree + 1))
                self.db.add_image_nums('unk', imgs)

            # the opposite shouldn't happen. Todo maybe: give a user-friendlier error
            assert high_img_num_db == high_img_num_db,\
                        f'highest image in db {high_img_num_db} > '\
                        f'hghest image in dirtree {high_img_num_dirtree}'

    def get_next_image_number(self):
        """Return the image number that should be applied to the next image scanned."""

        return GLB.db.get_highest_image_num() + 1

    def scan_a_batch(self, tracing=False):
        """Call out to scanimage, monitor progress through self.timeoutfunc().
        
        tracing:    enables frequent prints to the console"""

        self.tracing = tracing
        assert self.bsb.cur_stop_code != GLB.batch_status.stop_code.RUNNING
        # was scan_a_batch called to start a batch or to resume after an error?
        if not self.bsb.is_stopped_on_error():
            self.bsb.set_up_batch(self.bsb.next_seq_num_in_batch, True)  # Todo: important: simulating flag

        if self.simulating:
            self.timer_thread = threading.Timer(self.sim_scanner_speed, self.timeoutfunc_sim)
            self.timer_thread.start()
            return

        else:
            self.bsb.next_seq_num_in_batch = self.bsb.first_seq_num_in_batch
            popen_args = [
                "/usr/local/bin/scanimage",
                "--mode", "color",
                "--buffer-size",
                "--source", ('ADF Front', 'ADF Duplex')[self.sided - 1],
                "--compression", "JPEG",
                "--batch=%s/%%06d.jpg" % (self.incomingdir,),       # format of file name
                "-y",  self.lenmm,  # I wonder why scanimage doesn't default this to page length?
                "--page-height", self.lenmm,
                "--resolution", "%d" % (self.dpi,),
                "--batch-start", "%d" % (self.bsb.first_seq_num_in_batch,),  # starting num for file names
                "--endorser=yes",
                "--endorser-bits", "24",
                "--endorser-val", "%d" % (self.bsb.first_seq_num_in_batch,),
                "--endorser-step", str(self.sided),
                "--endorser-string", "%08ud",
                "--endorser-y", GLB.config['ballot']['imprint_y']
            ]
            my_env = os.environ.copy()
            my_env["LD_LIBRARY_PATH"] = "/usr/local/lib"
            self.p = subprocess.Popen(popen_args, env=my_env)
            self.timer_thread = threading.Timer(DEFER_COPY_SECS, self.timeoutfunc)
            self.timer_thread.start()

    def scan_test_ballot(self):
        """Pass a ballot with imprinting, but do not save the image."""

        if not self.simulating:
            next_to_scan = 999999
            folder = self.incomingdir + '/test_ballots'
            makedirsok(folder)
            del_dir_contents(folder)
            popen_args = [
                "/usr/local/bin/scanimage",
                "--mode", "color",
                "--buffer-size",
                "--source", ('ADF Front', 'ADF Duplex')[self.sided - 1],
                "--compression", "JPEG",
                "--batch=%s/%%06d.jpg" % (folder,),       # format of file name
                "-y",  self.lenmm,
                "--page-height", self.lenmm,
                "--resolution", "%d" % (self.dpi,),
                "--batch-start", "%d" % (next_to_scan,),
                "--endorser=yes",
                "--endorser-bits", "24",
                "--endorser-val", "%d" % (next_to_scan,),
                "--endorser-step", str(self.sided),
                "--endorser-string", "%08ud",
                "--endorser-y", "165",  # 6.5 inches down the page (beneath the barcode]
            ]

            # wait until scanimage is done before returning
            my_env = os.environ.copy()
            my_env["LD_LIBRARY_PATH"] = "/usr/local/lib"
            p = subprocess.Popen(popen_args, env=my_env)
            p.wait()

    def find_high_water(self):
        """Return the number of the highest file name in either the incoming directory
           or the directory tree.

           Returns -1 if there are no image files in either place."""

        files = os.listdir(self.incomingdir)
        newimages = [f for f in files if GLB.img_file_name_match.match(f)]
        if len(newimages) > 0:
            return int(os.path.basename(max(newimages))[:6])

        # nothing interesting in incoming directory, so check output directory tree
        #
        dirlist = sorted([d for d in os.listdir(self.outdirtree)
                          if Scan_HW_Control.dirnnn.match(d)])
        ...

        for dir in reversed(dirlist): # allow for an empty directory in the tree (shouldn't be, but...)
            lookin = os.path.join(self.outdirtree, dir)
            files = sorted([f for f in os.listdir(lookin) if GLB.img_file_name_match.match(f)])
            if len(files) == 0: continue
            return int(files[-1][:6])

        return -1  # no image files in the directory tree

    def _files_to_dirtree(self, nums):
        for num in [int(n) for n in nums]:
            subdir, fname = GLB.subpath_to_image(num)
            # subdir =  "%03d" % (int(num / 1000),)
            # fname  = '{:06d}.jpg'.format(num)
            frompath = os.path.join(self.incomingdir, fname)
            topath = os.path.join(self.outdirtree, subdir, fname)
            makedirsok(os.path.join(self.outdirtree, subdir))
            try:
                os.rename(frompath, topath)
                logging.info(topath)
            except Exception as e:
                logging.exception('Error moving {} to {}'.format(frompath, topath))
                print(e)

    # start watch scanner thread ------------------------------------------------
    def timeoutfunc(self):
        """Monitor scanimage and copy images to output dirtreeevery DEFER_COPY_SECS."""

        process_return_code = self.p.poll()

        # todo: IMPORTANT detect error stop and send signal to caller on normal or error stop

        files = os.listdir(self.incomingdir)
        newimages = [int(f[:6]) for f in files if GLB.img_file_name_match.match(f)]

        # copy new images from temp directory to the dirtree and add to database
        if len(newimages) > 0:
            self.incomingdir_highwater = max(newimages)
            self.bsb.next_num_in_batch = self.incomingdir_highwater + 1
            self._files_to_dirtree(newimages[:-1]) # last image may be incomplete if scanner still running
            GLB.db.add_image_nums(self.bsb.elections_batch_num, newimages[:-1])
            GLB.db.add_image_nums((newimages[:-1]))   # todo: could two images entries be incomplete?
            self.update()

        if process_return_code == None:
            t = threading.Timer(DEFER_COPY_SECS, self.timeoutfunc)
            t.start()       # scanimage is still running, so check back in DEFER_COPY_SECS

        else: # scanimage has exited

            # todo: important detect if this was an error stop see issues below:
            #   if it is an error stop the last image to be copied is questionable
            #   the users will have to determine if it is correct or not.
            #   signal an error stop rather than a regular update signal

            # not an error stop:
            self.complete()
    # end watch scanner thread -----------------------------------------------

    # start simulating scanner thread ------------------------------------------------
    def timeoutfunc_sim(self):
        """Simulate getting an image or a pair every sim_scanner_speed msecs."""

        self.bsb.front_path = fullpath_to_image(self.bsb.next_seq_num_in_batch)
        if self.bsb.sided == 1:
            self.bsb.back_path = None
        else:
            self.bsb.back_path = fullpath_to_image(self.bsb.next_seq_num_in_batch + 1)

        this_seq_num = self.bsb.next_seq_num_in_batch
        GLB.db.add_image_nums(self.bsb.elections_batch_num, (this_seq_num, this_seq_num + 1))

        # advance the "next image" pointer and image count
        self.bsb.next_seq_num_in_batch += self.bsb.sided
        self.bsb.images_scanned += self.bsb.sided

        # if we are simulating errors, is this the one?
        if self.bsb.dbg_throw_error_after:
            self.bsb.dbg_throw_error_after -= self.bsb.sided
            if self.bsb.dbg_throw_error_after <= 0:
                # yes, simulate an error now
                self.bsb.cur_stop_code = Batch_status.stop_code.OTHER_ERROR
                self.bsb.dbg_conditional_trace(self.tracing, 'about to emit an error signal')

                # at this point the "erroneous" file has been entered in the database and is
                # reflected in the bsb as having been processed
                self.scan_error_sig.emit()
                return

        # self.bsb.dbg_conditional_trace(True, 'after a non-error sheet is simulated')
        self.bsb.dbg_conditional_trace(self.tracing, 'after a non-error sheet is simulated')
        self.scan_update.emit()

        # time to end the batch?
        if self.bsb.seq_num_limit > self.bsb.next_seq_num_in_batch:
            # no, continue batch
            t = threading.Timer(self.sim_scanner_speed, self.timeoutfunc_sim)   # not done with batch
            t.start()

        else:
            # end batch now
            self.bsb.cur_stop_code = Batch_status.stop_code.NORMAL
            self.bsb.seq_num_limit = self.bsb.next_seq_num_in_batch
            self.bsb.dbg_conditional_trace(self.tracing, 'batch is complete')
            self.complete_sig.emit()

    # end simulation thread -------------------------------------------------

GLB.register(Scan_HW_Control(), 'scanner')


if __name__ == '__main__':
    bsb = GLB.batch_status

  #### CURRENTLY BROKEN BECAUSE OF SWITCH TO SIGNALS

    def printbsb(bsb):
        s = (bsb.__repr__())
        segs = s.split(';')
        for seg in segs:
            print("     ", seg)

    def update():
        print("update")
        printbsb(bsb)

    schdwr = Scan_HW_Control()
    schdwr.scan_a_batch(update)
    time.sleep(5)      # avoid prints from different threads commingling
    printbsb(bsb)
    print('scan another batch')
    schdwr.scan_a_batch(update)
    time.sleep(5)
    print('final BSB')
    printbsb(bsb)



