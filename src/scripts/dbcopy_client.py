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
import sys

from ensembl.production.core.clients.dbcopy import DbCopyRestClient


def handle_runtime_error(error):
    logging.error("Error: %s", error)
    sys.exit(1)


def handle_key_error(error, job):
    msg = f"Invalid response. Missing argument: '{err}'. Response: {job}"
    logging.error(msg)


def main():
    parser = argparse.ArgumentParser(description='Copy Databases via a REST service')

    parser.add_argument('-u', '--uri', required=True,
                        help='Copy database REST service URI')
    parser.add_argument('-a', '--action', choices=['submit', 'retrieve', 'list', 'delete', 'email', 'kill_job'],
                        required=True, help='Action to take')
    parser.add_argument('-j', '--job_id', help='Copy job identifier to retrieve')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')
    parser.add_argument('-s', '--src_host', required=True,
                        help='Source host for the copy in the form host:port')
    parser.add_argument('-t', '--tgt_host', required=True,
                        help='List of hosts to copy to in the form host:port,host:port')
    parser.add_argument('-i', '--src_incl_db',
                        help='List of databases to include in the copy. If not defined all the databases from the server will be copied')
    parser.add_argument('-k', '--src_skip_db', help='List of database to exclude from the copy')
    parser.add_argument('-p', '--src_incl_tables', help='List of tables to include in the copy')
    parser.add_argument('-d', '--src_skip_tables', help='List of tables to exclude from the copy')
    parser.add_argument('-n', '--tgt_db_name', help='Database name on target server. Used for renaming databases')
    parser.add_argument('-o', '--skip_optimize', default=0,
                        help='Skip database optimization step after the copy. Useful for very large databases')
    parser.add_argument('-w', '--wipe_target', default=0,
                        help='Delete target database before copy')
    parser.add_argument('-c', '--convert_innodb', default=0,
                        help='Convert InnoDB tables to MyISAM after copy')
    parser.add_argument('-e', '--email_list', required=True,
                        help='Email where to send the report')
    parser.add_argument('-r', '--user', required=True, help='User name')
    parser.add_argument('--skip-check', action='store_true', default=False,
                        help='Skip host:port server validation')

    args = parser.parse_args()

    if args.verbose == True:
        logging.basicConfig(level=logging.DEBUG, format='%(message)s')
    else:
        logging.basicConfig(level=logging.INFO, format='%(message)s')

    client = DbCopyRestClient(args.uri)

    if args.action == 'submit':
        logging.info('Submitting %s -> %s', args.src_host, args.tgt_host)
        try:
            if not args.skip_check:
                logging.info('Checking source and target hostname validity...')
                source_errs = client.check_hosts('source', (args.src_host,))
                target_errs = client.check_hosts('target', args.tgt_host.split(','))
                for err in source_errs:
                    logging.error('Source hostname error: %s', err)
                for err in target_errs:
                    logging.error('Target hostname error: %s', err)
                if source_errs or target_errs:
                    sys.exit(1)
            job_id = client.submit_job(args.src_host, args.src_incl_db, args.src_skip_db, args.src_incl_tables,
                                       args.src_skip_tables, args.tgt_host, args.tgt_db_name, args.skip_optimize,
                                       args.wipe_target, args.convert_innodb, args.email_list, args.user)
        except RuntimeError as err:
            handle_runtime_error(err)
        logging.info('Job submitted with ID %s', job_id)

    elif args.action == 'retrieve':
        try:
            job = client.retrieve_job(args.job_id)
            client.print_job(job, args.user, print_results=True)
        except RuntimeError as err:
            handle_runtime_error(err)
        except KeyError as err:
            handle_key_error(err, job)
    elif args.action == 'list':
        try:
            jobs = client.list_jobs()
        except RuntimeError as err:
            handle_error(err)
        for job in jobs:
            try:
                client.print_job(job, args.user)
            except KeyError as err:
                handle_key_error(err, job)


if __name__ == '__main__':
    main()
