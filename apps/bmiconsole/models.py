from django.db import models
from django.conf import settings
from djangotoolbox.fields import ListField
from djangotoolbox.fields import EmbeddedModelField
from macaddress.fields import MACAddressField
from uuidfield import UUIDField
from django_mongodb_engine.fields import GridFSField
from django_mongodb_engine.storage import GridFSStorage
from utils.helper import current_site_url

gridfs = GridFSStorage(database='damncms_media', collection='media', base_url='%s/media/' % getattr(settings, 'SITE_URL', 'http://localhost:8080'))

import logging

logger = logging.getLogger('apps')
                
class Location(models.Model):
    name = models.CharField(max_length=100)
    street = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)    
    order = models.IntegerField(unique=True, default=0)
    def save(self, *args, **kwargs):
        # autogenerate order id if none is provided
        if self.order == 0:
            query_result = Location.objects.all()
            if query_result:
                self.order = query_result.aggregate(max_value=models.Max('order'))['max_value'] + 1
            else:
                self.order = 1
        super(Location, self).save(*args, **kwargs)
            
    def __unicode__(self):
        return u'%d-%s' % (self.order, self.name)
        
    class Meta:
        # order ascending by order
        ordering = ['order']
        # add view permission (GET)
        permissions = (
            ("view_location", "Can view avaliable locations"),
            )

class Cabinet(models.Model):
    name = models.CharField(max_length=100)
    location = models.ForeignKey('Location', related_name='cabinets')
    description = models.CharField(max_length=4096, blank=True)            
    def __unicode__(self):
        return u'%s-%s' % (self.location, self.name)
        
    class Meta:
        # order ascending by order
        ordering = ['name']
        # add view permission (GET)
        permissions = (
            ("view_cabinet", "Can view avaliable cabinets"),
            )


class System(models.Model):
    SYSTEM_STATUS = (
        (0, 'discovered'),
        (1, 'analysed'),
        (3, 'commisioning'),
        (4, 'installed'),
        (5, 'deactivated'),
        (6, 'unknown'),
    )
    BOOT_STATUS = (
        (0, 'ignore'),
        (1, 'analyse'),
        (2, 'commision'),
        (3, 'rescue'),
    )
    def get_default_cabinet():
        return Cabinet.objects.get(name='unknown')
    
    def get_default_osprofile():
            return OSProfile.objects.get(name='unknown')
                    
    cabinet = models.ForeignKey('Cabinet', related_name='systems', default=get_default_cabinet)
    #cabinet = models.ForeignKey('Cabinet', related_name='systems', null=True, blank=True)
    osprofile = models.ForeignKey('OSProfile', related_name='systems', default=get_default_osprofile)
    #osprofile = models.ForeignKey('OSProfile', related_name='systems', null=True, blank=True)
    name = models.CharField(max_length=100, default='unknown', null=True)
    description = models.CharField(max_length=4096, blank=True, null=True)
    mac_address = MACAddressField(unique=True)
    uuid = UUIDField(blank=True, null=True)
    system_status = models.IntegerField(choices=SYSTEM_STATUS, default=6, null=True)
    boot_status = models.IntegerField(choices=BOOT_STATUS, default=0, null=True)
    created = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return u'Servername: %s Rack: %s Boot Status: %s System Status: %s' % (
            self.name, self.cabinet, self.BOOT_STATUS[self.boot_status][1], self.SYSTEM_STATUS[self.boot_status][1] )

    class Meta:
        # order by product_type and cabinet (desc)
        ordering = ['name', 'cabinet']
        # add view permission (GET)
        permissions = (
            ("view_system", "Can view avaliable systems"),
            )

class OSProfile(models.Model):
    name = models.CharField(max_length=100)
    pxe_file = models.CharField(max_length=100)
    pxe_cfg = models.CharField(max_length=100)
    description = models.CharField(max_length=4096, blank=True)            
    def __unicode__(self):
        return u'%s' % (self.name)
        
    class Meta:
        ordering = ['name']
        # add view permission (GET)
        permissions = (
            ("view_osprofile", "Can view avaliable osprofiles"),
            )
