from pyzbar.pyzbar import decode
from PIL import Image


x = decode(Image.open('/Users/Wes/NotForTheCloud/2018_Nov/unproc/000/000000.jpg'))
# x = decode(Image.open('code128.png'))
print(x)
# [
#     Decoded(
#         data=b'Foramenifera', type='CODE128',
#         rect=Rect(left=37, top=550, width=324, height=76),
#         polygon=[
#             Point(x=37, y=551), Point(x=37, y=625), Point(x=361, y=626),
#             Point(x=361, y=550)
#         ]
#     )
#     Decoded(
#         data=b'Rana temporaria', type='CODE128',
#         rect=Rect(left=4, top=0, width=390, height=76),
#         polygon=[
#             Point(x=4, y=1), Point(x=4, y=75), Point(x=394, y=76),
#             Point(x=394, y=0)
#         ]
#     )
# ]