
"""Manage the scanner hardware and the flow of images between the scanner, main storage, and
   backup storage.

   The output images are arranged in a directory structure. Image file number 4012 would be in
   004/004012.jpg.

   These same directories will also contain zero-length files with the suffix .mrk. These are
   "marker" files. The highest .mrk file number in the structure has the name that will be
   assigned to the next image that is scanned.

   CURRENTLY THIS IS A DUMMY TO SUPPORT OTHER MODULES"""

from datetime  import datetime
from enum import Enum, auto
import GLB_globals
import glob
import os.path
from PyQt5.QtCore import QTimer
import scanner_hardware
import re
import sys

GLB = None # GLB will magically upated to the actual etp_globals object

# def subpath_to_image(num):
#     """Break up num into a directory/file name combo, without the file type suffix.
#
#        Num should be an integer in numeric or string form, <= 999999."""
#
#     fname = ('00000' + str(num))[-6:]
#     dir = fname[:3]
#     return dir, fname
#
# def fullpath_to_image(num):
#     base = GLB.config['Election']['pathtoimages']
#     dir, fname = subpath_to_image(num)
#     return  f"{base}/{dir}/{fname}"


class Scanner(object):
    def __init__(self):
        # self.status = 'not running'
        # self.simulating = True
        # if self.simulating:
        #     self.simulated_scanner_speed = 500  # msecs / image
        #     self.sim_images_path = GLB.config['Debugging']['imagesource']
        #     self.sim_last_image = None
        # self.batch_status = None
        # self.normal_stop_callback = None
        # self.Scan_HW_Control = scanner_hardware.Scan_HW_Control()

        if self.simulating:
            self.remove_all_mrks()

        # asynchronous processes can add two the following dirs when not simulating
        #
        self.dir_of_dirs = None                         # directory of the subdirs that have images
        self.image_dir = None                           # one of the subdirs

    # def scan_test_ballot(self, normal_stop_callback, error_stop_callback):
    #     """Scan a single page and display the image(s). Do not move them to storage and
    #        don't change the next image number."""
    #
    #     print('Scan test ballot', file=sys.stderr)
    #     if self.simulating:
    #         return
    #     else:
    #         self.scanHWcontrol.scan_test_ballot()
    #
    #     # todo: not this time - need to return the top-side image here

    # def get_next_to_scan_new_batch(self) -> int:
    #     """Return an integer that represents the next ballot number to assign
    #        when starting to scan a new batch. This the highest *.mrk file in
    #        the output directories.
    #
    #        Not valid if we currently processing a batch. (For a job with lots of images
    #        this is far too slow to run every image.)"""
    #
    #     assert self.status == 'not running', 'Error trying to find next marker while batch in progress,'
    #     path_head = GLB.config['Election']['pathtoimages']
    #     markers = sorted(glob.glob(path_head + '/*/*.mrk'))
    #     return 0 if len(markers) == 0 else int(markers[0][-10:-4])  # todo -- would be wrong if we had 4-char suffixes

    def setup_new_batch(self, first):
        """Set up GLB.batch_status for a new run.

           First is the lowest file number in that batch.

           In simulation, if the input direcotry of images has gaps of
           more than 1K images this could falsely end with with the last
           image before the first gap."""

        assert self.simulating, "need more code for non-simulating"
        assert isinstance(first, int)
        GLB.batch_status.first_seq_num_in_batch = int(first)
        # maxnum = int(first) + 1000

        # create a list of all the files that will be scanned in this batch
        #
        path_head = GLB.config['Election']['pathtoimages']
        filter = re.compile(r'^\d\d\d$')
        dir_of_dirs = [x for x in sorted(os.listdir(path_head)) if filter.match(x)]

        curr_dir = subpath_to_image(first)[0]
        last_dir = subpath_to_image(first+100)[0]

        for i in range(len(dir_of_dirs)):       # search forward to first valid subdir
            if dir_of_dirs[i] >= curr_dir:
                break

        if i>0: del dir_of_dirs[0: i-1]         # delete invalid subdirs
                                                # todo: optimize take out subdirs that are too high
        full_paths = list()

        # add valid filenames to full_paths, excluding non jpgs and whose names
        # can't be in a batch of approximately 1000 starting at first
        #
        for subdir in dir_of_dirs:
            possibles = [x for x in sorted(glob.glob(path_head +
                            f'/{subdir}/[0-9][0-9][0-9][0-9][0-9][0-9].*'))
                          if self._filter(x, first, first + 1000)]

            for f in possibles:
                full_paths.append(f)
                if len(full_paths) >= 1000: break
            if len(full_paths) >= 1000: break      # break out of outer loop
        GLB.batch_status.files_in_batch = full_paths
        return

    # def set_up_batch(self, operator_id, normal_stop_callback, update_callback, error_stop_callback):
    #     """Scan ballots and move them to output directory.
    #
    #        Returns immediately to keep the UI alive. Callbacks come asyncrhonously when the scanner
    #        stops or passes an item.
    #
    #        CURRENTLY A DUMMY THAT PULLS IMAGES OUT OF AN EXISTING DIRECTORY."""
    #
    #     # assert self.status == 'not running'
    #     # bsb = GLB.batch_status                 # batch status block
    #     # bsb.operator_id = operator_id
    #     # bsb.operator_id_date_time = datetime.now().replace(microsecond=0,second=0)
    #     # bsb.next_num_in_batch = bsb.first_seq_num_in_batch
    #     # bsb.batch_start_time = datetime.now().replace(microsecond=0,second=0)
    #     # bsb.sides_scanned = 0
    #     # assert isinstance(bsb.first_seq_num_in_batch, int)
    #     if self.simulating:
    #         bsb.seq_num_limit = 14 + int(bsb.first_seq_num_in_batch)
    #     else: assert False, "Code not written yet."
    #
    #     # self.status = 'running'
    #     self.normal_stop_callback = normal_stop_callback
    #     self.update_callback = update_callback
    #     self.error_stop_callback = error_stop_callback
    #     QTimer.singleShot(1, self.simulated_item)
    #     return True
    #
    def simulated_item(self):
        """Simulate one sheet passing through the scanner.

           Returns 1 or 2 image paths depending on whether the ballot is 2-sided.

           Calls itself repeatedly to simulate scanning."""

        bsb = GLB.batch_status
        print(bsb)
        bsb.front_path = bsb.files_in_batch[bsb.images_scanned]
        bsb.images_scanned += 1
        bsb.next_num_in_batch += 1
        if bsb.sided == 2:
            bsb.back_path = bsb.files_in_batch[bsb.images_scanned]
            bsb.images_scanned += 1
            bsb.next_num_in_batch += 1

        else:
            back_image_path = None

        if bsb.next_num_in_batch <= bsb.seq_num_limit:
            self.update_callback(bsb)
            QTimer.singleShot(self.simulated_scanner_speed, self.simulated_item)  # check back in sanner speed msecs

        else:
            # we say "might be" below because the actual next seq num
            # will be determined by looking for the highest .mrk file
            #
            print(f'simulating end of successful run; next sequence number might be '
                  f'{int(bsb.next_num_in_batch - bsb.sided)}', file=sys.stderr)
            # self.status = 'not running'
            p = fullpath_to_image(f'{bsb.next_num_in_batch}')
            open(p + '.mrk', 'w').close()
            self.normal_stop_callback()

        # ToDo: need to simulate error callbacks returning last two images

    # def remove_all_mrks(self):
    #     """Remove all marker files from all directories. Primarily used for unit testing."""
    #
    #     path_head = GLB.config['Election']['pathtoimages']
    #     markers = sorted(glob.glob(path_head + '/*/*.mrk'))
    #     for f in markers:
    #         os.remove(f)

    def _filter(self, path, minnum, maxnum):
        """Quicky filter for us in list comprehension below."""

        mo = re.search(r'/(\d\d\d\d\d\d).(jpg|jpeg|JPG|JPEG)$', path)
        if mo is None: return False
        return maxnum >= int(mo[1]) >= minnum


if __name__ == '__main__':
    from PyQt5.QtCore import QCoreApplication, QThread
    GLB = GLB_globals.get().set_object_instances()


    class dummy(QThread):
        """Driver to allow Scanner() to be running as a QThread while testing."""

        # callback functions used in testing
        def normal_stop(self):
            print('normal callback', file=sys.stderr)

        def update(self):
            print('update', file=sys.stderr)

        def error_stop(self):
            print('error stop', file=sys.stderr)

        def run(self):

            # begin testing
            #
            assert subpath_to_image(1) == ('000', '000001')
            assert subpath_to_image('999999') == ('999', '999999')
            fp = GLB.config['Election']['pathtoimages'] + '/012/012345'
            assert fullpath_to_image(12345) == fp

            # test the Scanner object with a batch of 1000 starting at 000018
            #
            GLB.scanner.remove_all_mrks()
            nextnum = GLB.scanner.get_next_to_scan_new_batch()
            assert nextnum == 0, f'possible error depending on input: {nextnum}'
            mrk = fullpath_to_image(nextnum + 18)       # create a marker file
            open(mrk + '.mrk', 'w').close()

            # now we should get a batch that crosses the subirectory boundary
            nextnum = GLB.scanner.get_next_to_scan_new_batch()
            assert nextnum == 18, f'Nextnum should be 18: {nextnum}'
            ###
            GLB.scanner.setup_new_batch(nextnum)
            r = GLB.scanner.start_batch('opid', self.normal_stop, self.update, self.error_stop)
            assert r, 'Start batch failed'

            # unable to test simulation here because simulated item fails
            #
            # bsb  = .batch_status
            # assert bsb.images_scanned == 0
            # assert bsb.back_path is None
            # assert bsb.front_path is None
            # v = '/Users/Wes/NotForTheCloud/2018_Nov/unproc/000/000018.jpg'
            # print(bsb.files_in_batch[0])
            # assert bsb.files_in_batch[0] == v, bsb.files_in_batch[0]

    app = QCoreApplication([])
    thread = dummy()
    thread.run()
