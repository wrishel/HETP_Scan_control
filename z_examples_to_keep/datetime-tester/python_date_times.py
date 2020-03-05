
"""Demonstrate python datetime module code needed to measure a time gap"""

import datetime

today = datetime.datetime.now().replace(microsecond=0,second=0)
mins90 = datetime.timedelta(minutes=90)

print('isoformat     ', today.isoformat())
print('default format', today)
another = datetime.datetime.fromisoformat('2019-12-15 16:01')
print('prior date    ', another)
gap = (today - another)
print('gap           ', gap)
print('gap > mins90  ', gap > mins90)

