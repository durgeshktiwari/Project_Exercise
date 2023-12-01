from django.db import models

class KeyValueMapping(models.Model):
    key = models.CharField(max_length=255,blank=False,null=False)
    value = models.TextField()

