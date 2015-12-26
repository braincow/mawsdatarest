from mongoengine import *

class MAWSData(Document):
    # define document fields to store into database
    timestamp = DateTimeField(required=True, unique=True)
    # actual data points are defined here
    TA60sAvg = FloatField(required=True) # data1 C
    DP60sAvg = FloatField(required=True) # data2 C
    RH60sAvg = FloatField(required=True) # data3 %
    PA60sAvg = FloatField(required=True) # data4 hPa
    QFF60sAvg = FloatField(required=True) # data5 hPa
    SR60sSum = FloatField(required=True) # data6 W/m2
    PR60sSum = FloatField(required=True) # data7 mm
    WD2minAvg = FloatField(required=True) # data8 (degrees)
    WS2minAvg = FloatField(required=True) # data9 m/s
    # define document metadata
    meta = {
        'indexes': [
            'timestamp'
        ]
    }

#eof
