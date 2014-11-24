import itertools
import json

try:
    from urllib.request import Request, urlopen, URLError
except ImportError:
    from urllib2 import Request, urlopen, URLError


class OpenStackConnector(object):
    def __init__(self, username, password, tenant_id, auth_url):
        self.username = username
        self.password = password
        self.tenant_id = tenant_id
        self.auth_url = auth_url
        self.token = self.get_token()
        self.access = self.token.get('access')
        if not self.access:
            raise ValueError("Unauthorized or invalid token")
        self.tenant_id = self.access.get('token',
                                         {}).get('tenant', {}).get('id')
        self.token_id = self.token.get('access', {}).get('token', {}).get('id')
        self.service_catalog = self.access.get('serviceCatalog')

        self._compute_urls = self._urls_from_catalog(self.service_catalog,
                                                     'compute')
        self._metering_urls = self._urls_from_catalog(self.service_catalog,
                                                      'metering')

        if not self._compute_urls:
            raise Exception("No public URLs available for compute service")

        self.compute_url = self._compute_urls[0]

    def get_token(self):
        headers = {'Content-Type': 'application/json',
                   'Accept': 'application/json'}
        data = {'auth':
                {'passwordCredentials':
                 {'username': self.username, 'password': self.password},
                 'tenantId': self.tenant_id}}
        req = Request('%s/%s' % (self.auth_url, 'tokens'),
                      json.dumps(data), headers)
        resp = urlopen(req)
        content = resp.read().decode('utf-8')
        return json.loads(content)

    def get_tenant_usages(self, start, end):
        try:
            ts_start = start.isoformat()
            ts_end = end.isoformat()
            req = Request(self.compute_url +
                          "/os-simple-tenant-usage?start=" +
                          "%s&end=%s&detailed=1" % (ts_start, ts_end))
            self._upgrade_to_authenticated_request(req)
            resp = urlopen(req)
            content = resp.read().decode('utf-8')
            encoded = json.loads(content)
            resp.close()
        except URLError as e:
            raise Exception("Unable to connect compute service API: %s" % e)
        except Exception as e:
            raise Exception("Unable to process compute reponse: %s" % e)

        return encoded['tenant_usages']

    def get_tenant_quotas(self, tenant):
        try:
            req = Request(self.compute_url +
                          "/os-quota-sets/" + tenant)
            self._upgrade_to_authenticated_request(req)
            resp = urlopen(req)
            content = resp.read().decode('utf-8')
            encoded = json.loads(content)
            resp.close()
        except URLError as e:
            raise Exception("Unable to connect compute service API: %s" % e)
        except Exception as e:
            raise Exception("Unable to process compute reponse: %s" % e)

        return encoded['quota_set']

    def get_vm_info(self, tenant, instance_id):
        """Returns a detailed description of a running instance. In case the
        given instance_id does not exists or it is associated with an instance
        in terminated state the API query will return 404."""
        try:
            req = Request(self.compute_url +
                          "/servers/%s" % instance_id)
            self._upgrade_to_authenticated_request(req)
            resp = urlopen(req)
            content = resp.read().decode('utf-8')
            encoded = json.loads(content)
            resp.close()
        except URLError as e:
            return {}
        except Exception as e:
            raise Exception("Unable to process compute reponse: %s" % e)

        return encoded['server']

    def get_meter_vm_cpu(self, instance_id, start):
        try:
            req = Request(self.metering_url + "/meters/cpu?limit=1&q.field=" +
                          "resource_id&q.op=eq&q.value=" + instance_id +
                          "&limit=1")
            self._upgrade_to_authenticated_request(req)
            resp = urlopen(req)
            context = resp.read().decode('utf-8')
            meter_info = json.loads(context)
            resp.close()
        except URLError as e:
            raise Exception("Unable to connect metering service API: %s" % e)
        except Exception as e:
            raise ValueError("Unable to process metering response: %s" % e)

        if not meter_info:
            return {}
        else:
            return meter_info[0]

    def get_flavor_name(self, flavor_id):
        return self._get_name_from_OS_object('flavor', flavor_id)

    def get_image_name(self, image_id):
        return self._get_name_from_OS_object('image', image_id)

    def _get_name_from_OS_object(self, object_type, object_id):
        document = {}
        try:
            req = Request(self.compute_url +
                          "/%ss/%s" % (object_type, object_id))
            self._upgrade_to_authenticated_request(req)
            resp = urlopen(req)
            context = resp.read().decode('utf-8')
            document = json.loads(context).get(object_type, {})
            resp.close()
        except URLError as e:
            pass
        except Exception as e:
            raise ValueError("Unable to process metering response: %s" % e)

        return document.get('name')

    def _upgrade_to_authenticated_request(self, req):
        req.add_header("X-Auth-Project-Id", self.tenant_id)
        req.add_header("Accept", "application/json")
        req.add_header("X-Auth-Token", self.token_id)

    @staticmethod
    def _urls_from_catalog(catalog, service_type):
        urls = []
        endpoints = [x.get('endpoints') for x in catalog
                     if (x.get('type') == service_type)]
        it = itertools.chain.from_iterable(endpoints)
        urls.extend(x.get('publicURL') for x in it
                    if x.get('publicURL'))
        return urls
