from mongoengine import *

class MAWSData(Document):
    # define document fields to store into database
    site = StringField(required=True)
    timestamp = DateTimeField(required=True, unique=True)
    # actual data points are defined here
    TA60sAvg = FloatField() # data1 C
    DP60sAvg = FloatField() # data2 C
    RH60sAvg = FloatField() # data3 %
    PA60sAvg = FloatField() # data4 hPa
    QFF60sAvg = FloatField() # data5 hPa
    SR60sSum = FloatField() # data6 W/m2
    PR60sSum = FloatField() # data7 mm
    WD2minAvg = FloatField() # data8 (degrees)
    WS2minAvg = FloatField() # data9 m/s
    # define document metadata
    meta = {
        'indexes': [
            'site',
            'timestamp'
        ]
    }

#eof
