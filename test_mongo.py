from mongo import *

times = ['9.00-10.10', '10.10-11.20', '11.20-12.30', '12.30-14.00', '14.00-15.10', '15.10-16.20']

washers = free_washers()

for time in times:
    print(washers[0]['time'][time])