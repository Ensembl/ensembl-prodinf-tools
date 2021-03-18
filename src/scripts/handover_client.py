#!/usr/bin/env python
# .. See the NOTICE file distributed with this work for additional information
#    regarding copyright ownership.
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#        http://www.apache.org/licenses/LICENSE-2.0
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

import argparse
import logging
import re
from datetime import datetime

import requests
from sqlalchemy.engine.url import make_url

from ensembl.production.core.server_utils import assert_http_uri, assert_mysql_db_uri, assert_email





if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Handover a database via a REST service')
    parser.add_argument('-u', '--uri', help='HC REST service URI', required=True)
    parser.add_argument('-a', '--action', help='Action to take',
                        choices=['submit', 'retrieve', 'list', 'delete', 'summary'], required=True)
    parser.add_argument('-v', '--verbose', help='Verbose output', action='store_true')
    parser.add_argument('-s', '--src_uri', help='URI of database to hand over')
    parser.add_argument('-e', '--email', help='Email address')
    parser.add_argument('-c', '--description', help='Description')
    parser.add_argument('-t', '--handover_token', help='Handover token')

    args = parser.parse_args()

    if args.verbose == True:
        logging.basicConfig(level=logging.DEBUG, format='%(message)s')
    else:
        logging.basicConfig(level=logging.INFO, format='%(message)s')

    if args.uri.endswith('/') == False:
        args.uri = args.uri + '/'

    client = HandoverClient(args.uri)

    if args.action == 'submit':

        spec = {
            "src_uri": args.src_uri,
            "contact": args.email,
            "comment": args.description
        }
        logging.debug(spec)
        handover_id = client.submit_handover(spec)
        logging.info('Job submitted with transaction ID ' + str(handover_id))
    elif args.action == 'list':
        handovers = client.list_handovers()
        for handover in handovers:
            client.print_handover_detail(handover)
    elif args.action == 'retrieve':
        handover = client.retrieve_handover(args.handover_token)
        client.print_handover_detail(handover[0])
    elif args.action == 'summary':
        handovers = client.list_handovers()
        client.handover_summary_email(handovers, args.email)
    else:
        logging.error("Action " + args.action + " not supported")
