# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2010 United States Government as represented by the
# Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

"""Metadata request handler."""

import webob.dec
import webob.exc

from nova.api.ec2 import cloud


class MetadataRequestHandler(object):

    """Serve metadata from the EC2 API."""

    def print_data(self, data):
        if isinstance(data, dict):
            output = ''
            for key in data:
                if key == '_name':
                    continue
                output += key
                if isinstance(data[key], dict):
                    if '_name' in data[key]:
                        output += '=' + str(data[key]['_name'])
                    else:
                        output += '/'
                output += '\n'
            return output[:-1] # cut off last \n
        elif isinstance(data, list):
            return '\n'.join(data)
        else:
            return str(data)

    def lookup(self, path, data):
        items = path.split('/')
        for item in items:
            if item:
                if not isinstance(data, dict):
                    return data
                if not item in data:
                    return None
                data = data[item]
        return data

    @webob.dec.wsgify
    def __call__(self, req):
        cc = cloud.CloudController()
        meta_data = cc.get_metadata(req.remote_addr)
        if meta_data is None:
            _log.error('Failed to get metadata for ip: %s' % req.remote_addr)
            raise webob.exc.HTTPNotFound()
        data = self.lookup(path, meta_data)
        if data is None:
            raise webob.exc.HTTPNotFound()
        return self.print_data(data)
