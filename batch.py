"""Batch -- the ballots processed together through a single scanner run."""


import copy
from datetime import datetime
import etpconfig    # accessed through GLB_globals; imported for IDE support
from enum import IntFlag, auto
from ETP_util import fullpath_to_image , subpath_to_image
import glob
import logging      # to do. Is this working? Change to my logging?
# import os
# import os.path
# import q_util       # will be accessed through GLB
# import re
# import shutil
# import subprocess
# import sys
# import threading    # thread for timing
# import time

import GLB_globals
GLB = GLB_globals.get()


class Batch_status:
    """A singleton object that shows the status of the current batch at a point in time.

       Sadly, this is denormalized so some of the contents represent a single sheet
       or a single image."""

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

    def curr_batch_num(self):
        return self.next_seq_num_in_batch - self.sided

    def is_stopped_on_error(self):
        return self.cur_stop_code & Batch_status.stop_code.ERROR != 0

    def dbg_conditional_trace(self, tracing_flag, title):
        if not tracing_flag: return
        print(f'\n{title}')
        print(f'start =   {self.first_seq_num_in_batch}\n' +
              f'next =    {self.next_seq_num_in_batch}\n' +
              f'limit =   {self.seq_num_limit}\n' +
              f'images scanned =   {self.images_scanned}\n' +
              f'front =   {self.front_path}\n' +
              f'back =    {self.back_path}\n')

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
                self.dbg_throw_error_after = None
            else:
                self.dbg_throw_error_after = int(t) + self.sided

        else:
            self.dbg_throw_error_after = None

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
