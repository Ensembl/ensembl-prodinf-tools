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

from ensembl.production.core.rest import RestClient


def main():
    parser = argparse.ArgumentParser(description='Run Production jobs via a REST service')

    parser.add_argument('-u', '--uri', help='HC REST service URI', required=True)
    parser.add_argument('-a', '--action', help='Action to take',
                        choices=['submit', 'retrieve', 'list', 'delete', 'collate'], required=True)
    parser.add_argument('-i', '--job_id', help='HC job identifier to retrieve')
    parser.add_argument('-v', '--verbose', help='Verbose output', action='store_true')
    parser.add_argument('-o', '--output_file', help='File to write output as JSON', type=argparse.FileType('w'))
    parser.add_argument('-f', '--failure_only', help='Show failures only', action='store_true')
    parser.add_argument('-e', '--email', help='User email')

    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG, format='%(message)s')
    else:
        logging.basicConfig(level=logging.INFO, format='%(message)s')

    if not args.uri.endswith('/'):
        args.uri = args.uri + '/'

    client = RestClient(args.uri)

    if args.action == 'retrieve':
        job = client.retrieve_job(args.job_id)
        client.print_job(job, print_results=True, print_input=True)
    elif args.action == 'list':
        jobs = client.list_jobs()
    elif args.action == 'delete':
        client.delete_job(args.job_id)
    else:
        logging.error("Unknown action %s", args.action)


if __name__ == '__main__':
    main()
