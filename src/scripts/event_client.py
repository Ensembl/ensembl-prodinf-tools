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
import json
import logging

from ensembl.production.core.clients.event import EventClient


def main():
    parser = argparse.ArgumentParser(description='Run HCs via a REST service')

    parser.add_argument('-u', '--uri', help='HC REST service URI', required=True)
    parser.add_argument('-a', '--action', help='Action to take',
                        choices=['submit', 'retrieve', 'list', 'delete', 'events', 'processes'], required=True)
    parser.add_argument('-i', '--job_id', help='HC job identifier to retrieve')
    parser.add_argument('-v', '--verbose', help='Verbose output', action='store_true')
    parser.add_argument('-e', '--event', help='Event as JSON')
    parser.add_argument('-p', '--process', help='Process name')

    args = parser.parse_args()

    if args.verbose == True:
        logging.basicConfig(level=logging.DEBUG, format='%(message)s')
    else:
        logging.basicConfig(level=logging.INFO, format='%(message)s')

    if args.uri.endswith('/') == False:
        args.uri = args.uri + '/'

    client = EventClient(args.uri)

    if args.action == 'submit':
        job_id = client.submit_job(json.loads(args.event))
        logging.info('Job submitted with ID ' + str(job_id))

    elif args.action == 'retrieve':
        job = client.retrieve_job(args.process, args.job_id)
        client.print_job(job, print_results=True, print_input=True)

    elif args.action == 'list':
        for job in client.list_jobs(args.process):
            client.print_job(job)

    elif args.action == 'delete':
        client.delete_job(args.job_id)

    elif args.action == 'events':
        logging.info(client.events())

    elif args.action == 'processes':
        logging.info(client.processes())


if __name__ == '__main__':
    main()
