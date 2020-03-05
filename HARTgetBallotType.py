""" Obtain the ballot type ID from a HART ballot by bar-code or, optical recognition.

    This code was written for the Humboldt Election Transparency Project and is licensed
    but under the MIT License and the Beer License.
"""

# import tesseract
from PIL import Image
from PIL import ImageFile  # fix for IOError('image file is truncated ...
ImageFile.LOAD_TRUNCATED_IMAGES = True
from pyzbar.pyzbar import decode, ZBarSymbol
import codecs
import os
import re
import sys
import time
from election_paramaters.pctids_2018_11 import pctids_2018_11
# import logging        # logging commented out, should be used by caller if wanted

def pct_id(s):
    """Extract the precinct ID from the bar code string"""

    return s[1:7]

def page_num(s):
    """Extract the page number digits from the bar code string"""

    return s[8]

def b2str(binbytes):
    """Convert binary octets to Python3 string.

       Currently required for pyzbar output. If arg is None, return None"""

    if binbytes is None: return None
    return ''.join(chr(x) for x in binbytes)



# Performance measured on PowerBook (2015) MacOS Jan 17, 2020
#
# time in pyzbar starts at .0059 and grows slowly       todo: why?
# total elapsed time starts at .245 seconds. Most of the difference is opening and
# subsetting the image in PIL

class HARTgetBallotType:
    """Get a HART ballot precinct ID (six digits) and page number from the barcode.

       There is code commented out here that would use tesseract to OCR the information
       if pyzbar fails. But pyzbar is working well and tesseract is yet another library
       to load and maintain versions. The code was tested and worked,"""

    def __init__(self):

        self.DPI = 300  # scanning resolutions lower than use impact recognition
        inchToPx = lambda x: int(float(x) * self.DPI + .5)

        # HART Ballot Locations
        #
        # Printed number runs vertically in left margin. These crops
        # allow for misalignment but aren't too generous because the OCR
        # algorithm is sensitive to dirt on the page.
        #
        self.OCR_TOP_LEFT_X_PX = inchToPx(0.075)
        self.OCR_TOP_LEFT_Y_PX = inchToPx(3.1)
        self.OCR_BOT_RIGHT_X_PX = inchToPx(0.53)
        self.OCR_BOT_RIGHT_Y_PX = inchToPx(5.0)
        self.OCR_DELTA_X_PX = inchToPx(0.1)
        self.OCR_DELTA_Y_PX = inchToPx(0.1)

        # Barcode also runs vertically in the left margin. the crops are generously
        # wide, which works OK with pyzbar.
        #
        self.BARCODE_TOP_LEFT_X_PX = inchToPx(0.09)
        self.BARCODE_TOP_LEFT_Y_PX = inchToPx(0.45)
        self.BARCODE_BOT_RIGHT_X_PX = inchToPx(0.87)
        self.BARCODE_BOT_RIGHT_Y_PX = inchToPx(3.3)  # wjr 9/25/18

        self.goodnum = re.compile(r'^\d{14}$')  # The only acceptable format.
        self.successfulMode = None

    def getBallotType(self, file):
        """
        :param fd: file:
        :return string: Ballot type string of digits or None
        """
        global bc_count, bc_proctime, ocr_count, ocr_proctime
        self.upsideDownImage = None
        self.successfulMode = None
        # logging.info(file)
        # print(f'file={file}')
        image = Image.open(file)
        image.load()                # for time testing

        start = time.time()
        barcode = self._scanBarcode(image)
        # logging.info(barcode)
        if barcode:
            bc_count += 1
            bc_proctime += time.time() - start
            return barcode



        # # Barcode didn't work; try OCR-ing the ballot.
        # return self._ocrBallotID(image)
        return None

    # # In order to assure that tesseract gets closed, this class is
    # # instantiated through __enter__ for use with the With statement.
    # #
    def __enter__(self):
        # self.tessAPI = PyTessBaseAPI()  # Tesseract API
        # self.tessAPI.SetVariable('tessedit_char_whitelist', digits)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # self.tessAPI.End()
        return False        # if terminated by exception raise it now

    # def _ocrBallotID(self, image, deltaX=0, deltaY=0, upsideDown=False):
    #     """OCR the number that indicates the ballot format
    #        and contains the key to the precinct.
    #
    #     :param Image image:  a Pillow image of the full scanned ballot side.
    #     :param int deltaX: a cushion around the target number when scanning upside down.
    #     :param int deltaY: a cushion around the target number when scanning upside down.
    #     :return string: the OCR'pct_tots digits or None
    #
    #     """
    #
    #     # The error rate could probably be improved here by thresholding all
    #     # pixels of the cropped image with substantial color (i.e., not white or
    #     # black) to white. Performance penalty would be small
    #     # because most pages are handled with bar codes.
    #     #
    #     if upsideDown:
    #         if not self.upsideDownImage:
    #             self.upsideDownImage = image.transpose(Image.ROTATE_180)
    #         cropped = self.upsideDownImage.crop(
    #             (self.OCR_TOP_LEFT_X_PX - self.OCR_DELTA_X_PX,
    #              self.OCR_TOP_LEFT_Y_PX,
    #              self.OCR_BOT_RIGHT_X_PX,
    #              self.OCR_BOT_RIGHT_Y_PX + self.OCR_DELTA_Y_PX)).transpose(Image.ROTATE_270)
    #
    #     else:
    #         cropped = image.crop((self.OCR_TOP_LEFT_X_PX,
    #                               self.OCR_TOP_LEFT_Y_PX,
    #                               self.OCR_BOT_RIGHT_X_PX,
    #                               self.OCR_BOT_RIGHT_Y_PX)).transpose(Image.ROTATE_270)
    #
    #     self.tessAPI.SetImage(cropped)
    #     txt = tesserocr.image_to_text(image)
    #     # logging.info(txt)
    #
    #     # Ignore embedded spaces in OCR'pct_tots text. Even thought we specify only digits Tesseract
    #     # may embed spaces in the text.
    #     #
    #     txt = txt.replace(' ', '')
    #     # logging.info(txt)
    #     if self.goodnum.match(txt):
    #         self.successfulMode = 'o'
    #         # logging.info(txt)
    #         return txt
    #     if upsideDown:
    #         logging.info('try upside down')
    #         return None  # already tried upside down, so give up
    #     return self._ocrBallotID(image, deltaX, deltaY, True)  # try upside down

    def _scanBarcode(self, image, upsideDown=False):
        """Capture the ballot ID from the barcode.

        :param Image image:  a Pillow image of the full scanned ballot side.
        :param Boolean upsideDown:  a Pillow image of the full scanned ballot side.
        :return string: the bar code digits or None
        """
        img = image
        if upsideDown:
            if not self.upsideDownImage:
                self.upsideDownImage = image.transpose(Image.ROTATE_180)
                img = self.upsideDownImage

        bcimage = img.crop((self.BARCODE_TOP_LEFT_X_PX,
                            self.BARCODE_TOP_LEFT_Y_PX,
                            self.BARCODE_BOT_RIGHT_X_PX,
                            self.BARCODE_BOT_RIGHT_Y_PX))
        if False:
            bcimage.show()
        barcodes = decode(bcimage, symbols=[ZBarSymbol.I25])

        # Pyzbar can return some ghost barcodes. (This may be fixed now).
        #
        for i in reversed(range(len(barcodes))):
            bcd = barcodes[i]
            bcd_data = bcd.data.decode("utf-8")
            if bcd.rect.width == 0 or not self.goodnum.match(bcd_data):
                del barcodes[i]

        if len(barcodes) == 1:
            self.successfulMode = 'b'
            if upsideDown:
                print(f'upside down {image}')
            return barcodes[0].data
        if upsideDown:
            print(f'failed {image}')
            return None  # we already tried upside down so punt.
        return self._scanBarcode(image, True)

#
#  -----------------------------------------  Unit Test  -----------------------------------------
#
global bc_count, bc_proctime, ocr_count, ocr_proctime
bc_count, bc_proctime, ocr_count, ocr_proctime = 0, 0.0, 0, 0.0

if __name__== '__main__':
    import json
    import fnmatch

    # source of test images
    #
    # readwrite = 'r'  # r to read values expected during testing. 'w' to rewrite those values.

    images_path = '/Users/Wes/NotForTheCloud/2018_Nov/unproc'
    HIGHEST_IMAGE_FILE = '231499.jpg'

    onlyTheseForTesting = []

    tstart = time.time()
    test_results = {}
    cnt = 0
    bcd = 0
    ocr = 0
    lastdir = None
    quitAfter = None
    pths = []


    with HARTgetBallotType() as hgbt:
        for root, dirs, files in os.walk(images_path):
            for f in files:

                # Construct input for testing
                #
                if fnmatch.fnmatch(f, '*.jpg') and f <= HIGHEST_IMAGE_FILE:
                    if  len(onlyTheseForTesting) > 0:
                        if f not in onlyTheseForTesting:
                            continue

                    cnt += 1

                    if  True: # cnt % 23 == 0:  # sample a small percentage of files
                        pths.append(os.path.join(root, f))

        print(f"number of files={len(pths)}")
        pths = sorted(pths)
        print('sorting done')
        reported = list()   # 6-digit IDs returned from pyzbar that didn's map to precinct id
        for pth in pths:
            try:
                ballotID = b2str(hgbt.getBallotType(pth))
            except Exception as e:
                sys.stderr.write("Exception on file '{}'\n{}\n".format(f, repr(e)))
                continue

            pctid = pct_id(ballotID[1:7])
            if pctid not in pctids_2018_11:
                if pctid not in reported:
                    reported.append(pctid)
                    print(f"{pctid} not found from {pth}")

            if hgbt.successfulMode == 'b':
                x = '{} (bc)'.format(ballotID)
                bcd += 1
            elif hgbt.successfulMode == 'o':
                x = '{} (ocr)'.format(ballotID)
                ocr += 1
            else:
                x = '(no bc or ocr)'
                print( cnt, root, f)
            relpath = codecs.encode(os.path.relpath(pth, images_path))  # Unicode to ASCII
            if x in test_results:
                test_results[x].append(relpath)
            else:
                test_results[x] = [relpath]
            if (cnt % 100) == 0:
                telapse = time.time() - tstart
                print ('n={:>6,}; et={:>6.1f}; avg={:>6.6f}; bcd={}; ocr={}'\
                    .format(cnt, telapse, bc_proctime / bc_count, bcd, ocr))

            if root != lastdir:
                print (root)
                lastdir = root

            if cnt == quitAfter: break

    telapse = time.time() - tstart
    if cnt: print (telapse, telapse / cnt)
    if '(no bc or ocr)' in test_results:
        print(test_results['(no bc or ocr)'])
    # with open(dataoutf, 'w') as ouf:
    #     for k in sorted(test_results.keys()):
    #         l = len(test_results[k])
    #         s = str(test_results[k][:3])
    #         if l > 3: s += ' ...'
    #         ouf.write('{} {} {}\n'.format(k, l, s))
    #
    # testvals = []
    # for k in sorted(test_results.keys()):
    #     testvals.append([k, sorted(test_results[k])])   # values in UTF-8
    #
    # p = os.path.join(images_path, 'outfile.json')
    # if readwrite == 'r':
    #     with open(p, 'r') as inf:
    #         dtest = json.load(inf)  # values in Unicode
    #
    #
    #     assert testvals == dtest
    # else:
    #     with open(os.path.join(images_path, 'outfile.json'), 'w') as of:
    #         json.dump(testvals, of)
    #
