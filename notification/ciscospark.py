#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# (c) 2016, Arun prasath <arun@wanclouds.net>
#
# This file is part of Ansible
#
# Ansible is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.

DOCUMENTATION = '''
---
module: ciscospark
version_added: "2.2"
short_description: Send a message to Cisco Spark room
description:
   - Send a message to Cisco Spark room
options:
  token:
    description:
      - API token.
    required: true
  room:
    description:
      - ID or name of the room.
  person_id:
    description:
      - The ID of the recipient when sending a private 1:1 message.
  personemail:
    description:
     - The email address of the recipient when sending a private 1:1 message.
  msg:
    description:
      - The message body.
    required: true

requirements: [ ]
author: "Arun prasath (@bingoarunprasath)"
'''

EXAMPLES = '''
# Example playbook 
- ciscospark:  token=apitoken room=roomId msg="Ansible task finished"

# Example playbook sending message to a spark room
- ciscospark:
    token: eUfFpFWeOjOlOdScWATeeUfFpFWeOjOlOdScWATeeUfFpFWeOjOlOdScWATe
    room: eUfFpFWeOjOlOdScWATeeUfFpFWeOjOlOdScWATeeUfFpFWeOjOlOdScWATe
    msg: "Hello team !!"

# Example playbook sending message to a single user 1:1
- ciscospark:
    token: eUfFpFWeOjOlOdScWATeeUfFpFWeOjOlOdScWATeeUfFpFWeOjOlOdScWATe
    personEmail: example@cisco.com
    msg: "Hi there !!"
'''

RETURN = '''
result:
  description: Returns the json output of the post message call.
  returned: changed
  type: dict
'''

# ===========================================
# Cisco spark module specific support methods.
#

import urllib
try:
    import json
except ImportError:
    import simplejson as json


DEFAULT_URI_V1 = "https://api.ciscospark.com"
MSG_URI_V1 = "/v1/messages"


def checkArgs(*args):
    '''Function to check if only one of the variables are set'''
    args_list = [bool(i) for i in args]
    return args_list.count(True) == 1

def send_msg_v1(module, token, room, msg, personId, personEmail):
    '''sending message to Cisco Spark API'''

    headers = {'Authorization': 'Bearer %s' % token, 'Content-Type': 'application/json'}
    
    # Only one of room, personEmail, personID parameter should be set
    if not checkArgs(room, personId, personEmail):
       module.fail_json(msg="Only one of the following parameter should be provided (room, personEmail, personId)")

    body = dict()
    body['text'] = msg
    if room:
        body['roomId'] = room
    if personId:
        body['toPersonId'] = personId
    if personEmail:
        body['toPersonEmail'] = personEmail

    url = DEFAULT_URI_V1 + MSG_URI_V1
    data = json.dumps(body)

    if module.check_mode:
        # In check mode, exit before actually sending the message
        module.exit_json(changed=False)
    response, info = fetch_url(module, url, data=data, headers=headers, method='POST')
    if info['status'] in [200]:
        return response.read()
    else:
        module.fail_json(msg="failed to send message, return status=%s" % str(info['status']))


# ===========================================
# Module execution.
#

def main():

    module = AnsibleModule(
        argument_spec=dict(
            token=dict(required=True, no_log=True),
            room=dict(required=False),
            msg=dict(required=True),
            personId=dict(required=False),
            personEmail=dict(required=False),
        ),
        supports_check_mode=True
    )

    token = module.params["token"]
    room = module.params["room"]
    msg = module.params["msg"]
    personId = module.params["personId"]
    personEmail = module.params["personEmail"]
    result = send_msg_v1(module, token, room, msg, personId, personEmail)
    changed = True
    module.exit_json(changed=changed, result=result)

# import module snippets
from ansible.module_utils.basic import *
from ansible.module_utils.urls import *
if __name__ == '__main__':
    main()
