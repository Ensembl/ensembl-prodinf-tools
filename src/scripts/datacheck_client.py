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

from ensembl.production.core.clients.datachecks import DatacheckClient

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Run datachecks via a REST service')

    parser.add_argument('-u', '--uri', help='Datacheck REST service URI', required=True)
    parser.add_argument('-a', '--action', help='Action to take',
                        choices=['submit', 'retrieve', 'list'], required=True)
    parser.add_argument('-i', '--job_id', help='Datacheck job identifier to retrieve')
    parser.add_argument('-v', '--verbose', help='Verbose output', action='store_true')
    parser.add_argument('-o', '--output_file', help='File to write output as JSON', type=argparse.FileType('w'))
    parser.add_argument('-s', '--server_url', help='URL of database server', required=True)
    parser.add_argument('-db', '--dbname', help='Database name')
    parser.add_argument('-sp', '--species', help='Species production name')
    parser.add_argument('-div', '--division', help='Division')
    parser.add_argument('-dbt', '--db_type', help='Database type')
    parser.add_argument('-n', '--datacheck_names', help='Datacheck names, multiple names comma-separated')
    parser.add_argument('-g', '--datacheck_groups', help='Datacheck groups, multiple names comma-separated')
    parser.add_argument('-dct', '--datacheck_types', help='Datacheck type (advisory or critical)')
    parser.add_argument('-e', '--email', help='Email address for pipeline reports')
    parser.add_argument('-t', '--tag', help='Tag to collate results and facilitate filtering')
    parser.add_argument('-f', '--failure_only', help='Show failures only', action='store_true')

    args = parser.parse_args()

    if args.verbose is True:
        logging.basicConfig(level=logging.DEBUG, format='%(message)s')
    else:
        logging.basicConfig(level=logging.INFO, format='%(message)s')

    client = DatacheckClient(args.uri)

    if args.action == 'submit':
        job_id = client.submit_job(args.server_url, args.dbname, args.species, args.division, args.db_type,
                                   args.datacheck_names, args.datacheck_groups, args.datacheck_types,
                                   args.email, args.tag)
        logging.info('Job submitted with ID ' + str(job_id))

    elif args.action == 'retrieve':
        job = client.retrieve_job(args.job_id)
        client.print_job(job, print_results=True, print_input=True)

    elif args.action == 'list':
        jobs = client.list_jobs(args.output_file, args.tag, args.failure_only)
