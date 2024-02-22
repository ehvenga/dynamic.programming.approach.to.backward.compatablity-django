from django.db import models

class Parameterhierarchy(models.Model):
    parentparameterid = models.CharField(db_column='parentParameterID', primary_key=True, max_length=10)
    childparameterid = models.CharField(db_column='childParameterID', max_length=10)
    noofdepth = models.IntegerField(db_column='noOfDepth')
    noofchildren = models.IntegerField(db_column='noOfChildren')

    class Meta:
        db_table = 'parameterhierarchy'
        unique_together = (('parentparameterid', 'childparameterid', 'noofdepth', 'noofchildren'),)
