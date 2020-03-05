
useit = False
importable = None
if useit:
    importable = __import__('importable')

hs = importable.hide_and_seek()
print (hs.a)

# import importlib
#
# useit = False
# importable = None
# if useit:
#     importable = importlib.__import__('importable')
#
# # import importable
# hs = importable.hide_and_seek()
# print (hs.a)
