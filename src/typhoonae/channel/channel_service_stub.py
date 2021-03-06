# -*- coding: utf-8 -*-
#
# Copyright 2007 Google Inc.
# Copyright 2010 Tobias Rodäbel
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
"""TyphoonAE's stub version of the Channel API."""

from google.appengine.api import apiproxy_stub
from google.appengine.api.channel import channel_service_pb
from google.appengine.runtime import apiproxy_errors

import httplib
import logging
import random
import time

WEEKDAY_ABBR = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
MONTHNAME    = [None, 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']


def rfc1123_date(ts=None):
  """Return an RFC 1123 format date string.

  Required for use in HTTP Date headers per the HTTP 1.1 spec. 'Fri, 10 Nov
  2000 16:21:09 GMT'.
  """
  if ts is None: ts=time.time()
  year, month, day, hh, mm, ss, wd, y, z = time.gmtime(ts)
  return "%s, %02d %3s %4d %02d:%02d:%02d GMT" % (WEEKDAY_ABBR[wd],
                                                  day, MONTHNAME[month],
                                                  year,
                                                  hh, mm, ss)


class ChannelServiceStub(apiproxy_stub.APIProxyStub):
  """Channel service stub.

  Using a publish/subscribe service.
  """

  def __init__(self, address, log=logging.info, service_name='channel'):
    """Initializes the Channel API proxy stub.

    Args:
      address: The address of our Channel service.
      log: A logger, used for dependency injection.
      service_name: Service name expected for all calls.
    """
    apiproxy_stub.APIProxyStub.__init__(self, service_name)
    self._address = address
    self._log = log

  def _Dynamic_CreateChannel(self, request, response):
    """Implementation of channel.get_channel.

    Args:
      request: A ChannelServiceRequest.
      response: A ChannelServiceResponse
    """
    application_key = request.application_key()
    if not application_key:
      raise apiproxy_errors.ApplicationError(
          channel_service_pb.ChannelServiceError.INVALID_CHANNEL_KEY)

    response.set_client_id(application_key)

  def _Dynamic_SendChannelMessage(self, request, response):
    """Implementation of channel.send_message.

    Queues a message to be retrieved by the client when it polls.

    Args:
      request: A SendMessageRequest.
      response: A VoidProto.
    """
    application_key = request.application_key()

    if not request.message():
      raise apiproxy_errors.ApplicationError(
          channel_service_pb.ChannelServiceError.BAD_MESSAGE)

    conn = httplib.HTTPConnection(self._address)
    headers = {'Content-Type': 'text/plain',
               'Last-Modified': rfc1123_date()}
    conn.request("POST", "/_ah/publish?id=%s" %
                 application_key, request.message(), headers)
    conn.close()
