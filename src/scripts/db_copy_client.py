#!/usr/bin/env python3
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

from ensembl.production.core.clients.dbcopy import DbCopyClient

# DEPRECATED
if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Copy Databases via a REST service')

    parser.add_argument('-u', '--uri', help='Copy database REST service URI', required=True)
    parser.add_argument('-a', '--action', help='Action to take',
                        choices=['submit', 'retrieve', 'list', 'delete', 'email', 'kill_job'], required=True)
    parser.add_argument('-i', '--job_id', help='HC job identifier to retrieve')
    parser.add_argument('-v', '--verbose', help='Verbose output', action='store_true')
    parser.add_argument('-o', '--output_file', help='File to write output as JSON', type=argparse.FileType('w'))
    parser.add_argument('-f', '--input_file', help='File containing list of source and target URIs',
                        type=argparse.FileType('r'))
    parser.add_argument('-s', '--source_db_uri', help='URI of database to copy from')
    parser.add_argument('-t', '--target_db_uri', help='URI of database to copy to')
    parser.add_argument('-y', '--only_tables', help='List of tables to copy')
    parser.add_argument('-n', '--skip_tables', help='List of tables to skip')
    parser.add_argument('-p', '--update', help='Incremental database update using rsync checksum')
    parser.add_argument('-d', '--drop', help='Drop database on Target server before copy')
    parser.add_argument('-c', '--convert_innodb', help='Convert InnoDB tables to MyISAM after copy')
    parser.add_argument('-k', '--skip_optimize',
                        help='Skip the database optimization step after the copy. Useful for very large databases')
    parser.add_argument('-e', '--email', help='Email where to send the report')

    args = parser.parse_args()

    if args.verbose == True:
        logging.basicConfig(level=logging.DEBUG, format='%(message)s')
    else:
        logging.basicConfig(level=logging.INFO, format='%(message)s')

    if args.uri.endswith('/') == False:
        args.uri = args.uri + '/'

    client = DbCopyClient(args.uri)

    if args.action == 'submit':

        if args.input_file == None:
            logging.info("Submitting " + args.source_db_uri + "->" + args.target_db_uri)
            job_id = client.submit_job(args.source_db_uri, args.target_db_uri, args.only_tables, args.skip_tables,
                                       args.update, args.drop, args.convert_innodb, args.skip_optimize, args.email)
            logging.info('Job submitted with ID ' + str(job_id))
        else:
            for line in args.input_file:
                uris = line.split()
                logging.info("Submitting " + uris[0] + "->" + uris[1])
                job_id = client.submit_job(uris[0], uris[1], args.only_tables, args.skip_tables, args.update, args.drop,
                                           args.convert_innodb, args.skip_optimize, args.email)
                logging.info('Job submitted with ID ' + str(job_id))

    elif args.action == 'retrieve':

        job = client.retrieve_job(args.job_id)
        client.print_job(job, print_results=True, print_input=True)

    elif args.action == 'list':

        jobs = client.list_jobs()
        for job in jobs:
            client.print_job(job)

    elif args.action == 'delete':
        client.delete_job(args.job_id)
        logging.info("Job " + str(args.job_id) + " was successfully deleted")

    elif args.action == 'email':
        client.job_email(args.job_id, args.email)

    elif args.action == 'kill_job':
        client.kill_job(args.job_id)
