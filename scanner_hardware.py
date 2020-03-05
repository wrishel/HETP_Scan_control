
"""Scan ballot images for TEVS, setting parameters for the Fujitsu 5900-c scanner.

   We do not assume that the prior batch ended properly. That is to say, when
   we start up there may be images from a prior run still in self.incomingdir.

   These will get copied to the output dirtree on the first timer interrupt.

   Based strongly on TEVS routine written by Mitch Trachtenberg.
"""

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
MARKER_SUFFIX = 'marker'
# SIMULATED_BATCH_SIZE = 1000

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
class Batch_status:
    """A block of data showing the progress while scanning a batch."""

    class stop_code(IntFlag):
        RUNNING =       0b1             # not stopped
        NORMAL =        0b10            # stopped after a normal end of batch
        MISFEED =       0b100
        DOUBLE_FEED =   0b1000
        OTHER_ERROR =   0b10000
        ERROR = MISFEED | DOUBLE_FEED | OTHER_ERROR

    def __init__(self):
        self.GLB_name = 'batch_status'

        self.back_path = None               # if 2-sided, path to the back image
        self.batch_start_time = None        # usually a datetime object
        self.dbg_throw_error_after = None   # force an error during scanning after this many sides
        self.elections_batch_num = None     # (string) elections batch number being scanned
        self.first_seq_num_in_batch = None
        self.front_path = None              # path to the front image of the sheet
        self.images_scanned = 0             # may be one or two images/sheet depending on sided
        self.next_seq_num_in_batch = None   # the ballot that will be scanned next
        self.operator_id = None             # Initials of the operator for this batch
        self.operator_id_time = None        # The time the current operator started a batch
        self.seq_num_limit = None           # the seq num of the last ballot scanned; not valid during scanning
        self.sided = 2 if bool(GLB.config['ballot']['doublesided']) else 1
        self.cur_stop_code = self.stop_code.NORMAL  # the reason the scanner stopped, using stop_code enum
        print(f'initing batch_status: {self.first_seq_num_in_batch}')

    def __repr__(self):
        l = list()
        l.append(f"back_path={self.back_path}")
        l.append(f"batch_start_time={self.batch_start_time}")
        l.append(f"dbg_throw_error_after={self.dbg_throw_error_after}")
        l.append(f"first_seq_num_in_batch={self.first_seq_num_in_batch}")
        l.append(f"front_path={self.front_path}")
        l.append(f"images scanned={self.images_scanned}")
        l.append(f"next_seq_num_in_batch={self.next_seq_num_in_batch}")
        l.append(f"operator_id={self.operator_id}")
        l.append(f"operator_id_time={self.operator_id_time}")
        l.append(f"seq_num_limit={self.seq_num_limit}")
        l.append(f"sided={self.sided}")
        l.append(f"cur_stop_code={self.cur_stop_code}")
        s = '<Batch_status: ' + '; '.join(l) + '>'
        return s

    def is_stopped_on_error(self):
        return self.cur_stop_code & Batch_status.stop_code.ERROR != 0

    def get_next_image_number(self):
        """Return the image number that should be applied to the next image scanned.

           If scanning is using the hardware, this is the output of get_next_to_scan_new_batch()

           In the event of a crash during scanning, there is the possibility that
           there will be one more image in the dir than in the database. This can
           be recovered retrospectively. See Scan_HW_control.timeoutfunc.

           If scanning is simulated, this is one more than the highest number
           in the database."""

        # todo: checking on odd number when 2-sided
        simulating = GLB.config['Scanning']['simulating']
        if simulating:
            return GLB.batch_status.get_next_image_number() + 1
        else:
            return GLB.scanner.find_high_water + 1

    def dbg_conditional_trace(self, tracing_flag, title):
        if not tracing_flag: return
        print(f'\n{title}')
        print(f'start =   {self.first_seq_num_in_batch}\n' +
              f'next =    {self.next_seq_num_in_batch}\n' +
              f'limit =   {self.seq_num_limit}\n' +
              f'images scanned =   {self.images_scanned}\n' +
              f'front =   {self.front_path}\n' +
              f'back =    {self.back_path}\n')
        ...  # possible breakpoint after printing

    def get_next_to_scan_new_batch(self) -> int:
        """Return an integer that represents the next ballot number to assign
           when starting to scan a new batch. This the highest *.mrk file in
           the output directories."""

        path_head = GLB.config['Election']['pathtoimages']
        markers = sorted(glob.glob(path_head + f'/*/*.{MARKER_SUFFIX}'))
        return 0 if len(markers) == 0 else int(markers[0][-10:-4])



    def OK_to_backup(self):
        return self.next_seq_num_in_batch - self.sided <= self.first_seq_num_in_batch

    def back_up_one_sheet(self):
        """Back up the batch by one sheet.

           Return True if successful and false if we are already at the start of the batch."""

        if self.OK_to_backup():
            return False

        self.next_seq_num_in_batch -= self.sided
        self.images_scanned -= self.sided
        self.front_path = fullpath_to_image(self.next_seq_num_in_batch - self.sided)
        if self.sided > 1:
            self.back_path = fullpath_to_image(self.next_seq_num_in_batch - self.sided + 1)
        return True

    def forward_one_sheet(self):
        """Move forward in the batch by one sheet.

           Always return True but there is no guarantee that the files really exist."""

        self.next_seq_num_in_batch += self.sided
        self.images_scanned += self.sided
        self.front_path = fullpath_to_image(self.next_seq_num_in_batch - self.sided)
        if self.sided > 1:
            self.back_path = fullpath_to_image(self.next_seq_num_in_batch - self.sided + 1)
        return True

    def set_up_batch(self, next_seq_num_in_batch, simulating):
        """Set up parameters in BSB to initially start a batch"""

        assert next_seq_num_in_batch is not None
        bsb = GLB.batch_status
        # operator_id has been set up by control screens before scanning starts
        self.operator_id_date_time = datetime.now().replace(microsecond=0, second=0)
        self.batch_start_time = datetime.now().replace(microsecond=0, second=0)
        self.first_seq_num_in_batch = self.next_seq_num_in_batch = next_seq_num_in_batch
        self.seq_num_limit = GLB.config.get_int_or('Debugging', 'simulated_batch_size', 10) \
                             + self.first_seq_num_in_batch
        self.images_scanned = 0
        self.cur_stop_code = None
        assert self.next_seq_num_in_batch is not None

        # initially front_path and backup_path are None until an image is received or simulated
        self.front_path = self.back_path = None

        if simulating:
            # get the simulated error count if it exists.
            t = GLB.config.get_or_else('Debugging', 'simulate_error_after_images', None)
            if t in (None, ''):
                bsb.dbg_throw_error_after = None
            else:
                bsb.dbg_throw_error_after = int(t) + bsb.sided

        else:
            bsb.dbg_throw_error_after = None

    def restart_batch_params(self, simulating):
        """Reset parameters to the start of this batch"""

        self.next_seq_num_in_batch = self.first_seq_num_in_batch - self.sided
        self.front_path = self.back_path = None
        self.images_scanned = 0
        if simulating:
            self.seq_num_limit = GLB.config.get_int_or(10) + self.first_seq_num_in_batch
        else:
            self.seq_num_limit = None

GLB.register(Batch_status())

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
    nnnnnnjpg = re.compile(r'\d\d\d\d\d\d\.jpe*g$', re.IGNORECASE)
    nnnnnnjpgmarker = re.compile(fr'\d\d\d\d\d\d\.(jpe*g|{MARKER_SUFFIX})$', re.IGNORECASE)
    # nnnnnnmarker = re.compile(fr'\d\d\d\d\d\d\.{MARKER_SUFFIX}$', re.IGNORECASE)

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
        if self.simulating:
            try:
                hin = GLB.db.get_highest_image_num(
                                GLB.config['Election']['maximagenum'])
            except Exception as e:
                if e.msg.lower() == 'table \'hetptesting.images\' doesn\'t exist':
                    GLB.db.recreate_images()
                    hin = GLB.db.get_highest_image_num(GLB.config['Election']['maximagenum'])
                else:
                    assert False, "unexpected error"
            self.bsb.first_seq_num_in_batch = hin if hin else -self.bsb.sided
            self.bsb.next_seq_num_in_batch = hin
            self.remove_all_marks()

        else: assert False

    def scan_a_batch(self, tracing=False):
        """Call out to scanimage, monitor progress through self.timeoutfunc().
        
        tracing:    enables frequent prints to the console"""

        self.tracing = tracing
        assert self.bsb.cur_stop_code != Batch_status.stop_code.RUNNING
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
        newimages = [f for f in files if Scan_HW_Control.nnnnnnjpgmarker.match(f)]
        if len(newimages) > 0:
            return int(os.path.basename(max(newimages))[:6])

        # nothing interesting in incoming directory, so check output directory tree
        #
        ignore_above, _ = subpath_to_image(GLB.config['Election']['maximagenum'])
        dirlist = sorted([d for d in os.listdir(self.outdirtree)
                          if Scan_HW_Control.dirnnn.match(d)])
        ...

        for dir in reversed(dirlist): # allow for an empty directory in the tree (shouldn't be, but...)

            lookin = os.path.join(self.outdirtree, dir)

            if dir <  ignore_above:
                files = sorted([f for f in os.listdir(lookin) if Scan_HW_Control.nnnnnnjpg.match(f)])
                if len(files) == 0: continue
                return int(files[-1][:6])

        return -1  # no image files in incoming or the directory tree

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
        newimages = [int(f[:6]) for f in files if Scan_HW_Control.nnnnnnjpg.match(f)]

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

        # create marker file for highwater in output dirtree
        highname = os.path.join(self.incomingdir,
                                f"%06d.{MARKER_SUFFIX}" % self.incomingdir_highwater)
        open(highname, 'w').close()
        # self.running = False
    # end watch scanner thread -----------------------------------------------

    # start simulation thread ------------------------------------------------
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

    def remove_all_marks(self):
        """Remove all marker files from all directories. Primarily used for unit testing."""

        path_head = GLB.config['Election']['pathtoimages']
        markers = sorted(glob.glob(path_head + f'/*/*.{MARKER_SUFFIX}'))
        for f in markers:
            os.remove(f)


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



