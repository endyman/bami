import copy
import logging

from tastypie import fields
from tastypie.resources import ModelResource, ALL
from tastypie.api import Api
from django.conf.urls.defaults import url

logger = logging.getLogger('apps')

#internal imports
from extensions.tastypie.authorization import CustomDjangoAuthorization
from extensions.tastypie.authentication import CustomApiKeyAuthentication

from bmiconsole.models import Location, System, Cabinet, OSProfile

def get_api():
    # create the naespaces for the applications and api versions
    apis = {}
    apis['v1'] = Api(api_name='v1')
    apis['v1'].register(LocationResource())
    apis['v1'].register(SystemResource())
    apis['v1'].register(CabinetResource())
    apis['v1'].register(OSProfileResource())
    return apis


class CabinetResource(ModelResource):
    systems = fields.ToManyField('bmiconsole.api.SystemResource', 'systems', full=True)
    class Meta:
        queryset = Cabinet.objects.all()
        include_resource_uri = False
        resource_name = 'cabinets'
        authentication = CustomApiKeyAuthentication()
        authorization = CustomDjangoAuthorization()

    def alter_list_data_to_serialize(self, request, data_dict):
        # remove meta key from response
        if isinstance(data_dict, dict):
            if 'meta' in data_dict:
                # Get rid of the "meta".
                del(data_dict['meta'])
                # Rename the objects.
                data_dict['cabinets'] = copy.copy(data_dict['objects'])
                del(data_dict['objects'])
        return data_dict

class LocationResource(ModelResource):
    cabinets = fields.ToManyField('bmiconsole.api.CabinetResource', 'cabinets', full=False)
    class Meta:
        queryset = Location.objects.all()
        include_resource_uri = False
        resource_name = 'locations'
        authentication = CustomApiKeyAuthentication()
        authorization = CustomDjangoAuthorization()

    def alter_list_data_to_serialize(self, request, data_dict):
        # remove meta key from response
        if isinstance(data_dict, dict):
            if 'meta' in data_dict:
                # Get rid of the "meta".
                del(data_dict['meta'])
                # Rename the objects.
                data_dict['locations'] = copy.copy(data_dict['objects'])
                del(data_dict['objects'])
        return data_dict

class SystemResource(ModelResource):
    cabinet = fields.ForeignKey('bmiconsole.api.CabinetResource', 'cabinet', full=False)
    osprofile = fields.ForeignKey('bmiconsole.api.OSProfileResource', 'osprofile', full=False)
    class Meta:
        queryset = System.objects.all()
        filtering = {
        'mac_address': ('exact'),
        'uuid': ('exact'),
        }
        include_resource_uri = True
        resource_name = 'systems'
        authentication = CustomApiKeyAuthentication()
        authorization = CustomDjangoAuthorization()

    def override_urls(self):
        # mapping additional fields (apart from PK) into resource path
        # TODO: better regex for uuid / mac parsing        
        return [
            url(r"^(?P<resource_name>%s)/(?P<mac_address>[\dABCDEF:-]{17})/$" % self._meta.resource_name, self.wrap_view('dispatch_detail'), name="api_dispatch_detail"),
            url(r"^(?P<resource_name>%s)/(?P<uuid>[\d\w-]{36})/$" % self._meta.resource_name, self.wrap_view('dispatch_detail'), name="api_dispatch_detail"),    
            ]

    def alter_list_data_to_serialize(self, request, data_dict):
        # remove meta key from response
        if isinstance(data_dict, dict):
            if 'meta' in data_dict:
                # Get rid of the "meta".
                del(data_dict['meta'])
                # Rename the objects.
                data_dict['systems'] = copy.copy(data_dict['objects'])
                del(data_dict['objects'])
        return data_dict


class OSProfileResource(ModelResource):
    systems = fields.ToManyField('bmiconsole.api.SystemResource', 'systems', full=False)
    class Meta:
        queryset = OSProfile.objects.all()
        include_resource_uri = False
        resource_name = 'osprofiles'
        authentication = CustomApiKeyAuthentication()
        authorization = CustomDjangoAuthorization()

    def alter_list_data_to_serialize(self, request, data_dict):
        # remove meta key from response
        if isinstance(data_dict, dict):
            if 'meta' in data_dict:
                # Get rid of the "meta".
                del(data_dict['meta'])
                # Rename the objects.
                data_dict['osprofiles'] = copy.copy(data_dict['objects'])
                del(data_dict['objects'])
        return data_dict