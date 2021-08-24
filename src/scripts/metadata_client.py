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

from ensembl.production.core.clients.metadata import MetadataClient


def main():
    parser = argparse.ArgumentParser(description='Metadata load via a REST service')

    parser.add_argument('-u', '--uri', help='Metadata database REST service URI', required=True)
    parser.add_argument('-a', '--action', help='Action to take',
                        choices=['submit', 'retrieve', 'list', 'delete', 'email', 'kill_job'], required=True)
    parser.add_argument('-i', '--job_id', help='Job id to retrieve. In "list" mode, used as a cut-off')
    parser.add_argument('-v', '--verbose', help='Verbose output', action='store_true')
    parser.add_argument('-o', '--output_file', help='File to write output as JSON',
                        type=argparse.FileType('w'))
    parser.add_argument('-f', '--input_file', help='File containing list of metadata and database URIs',
                        type=argparse.FileType('r'))
    parser.add_argument('-d', '--database_uri', help='URI of database to load')
    parser.add_argument('-s', '--e_release', help='Ensembl release number')
    parser.add_argument('-r', '--release_date', help='Release date')
    parser.add_argument('-c', '--current_release', help='Is this the current release')
    parser.add_argument('-g', '--eg_release', help='EG release number')
    parser.add_argument('-e', '--email', help='Submitter. In "list" mode, used as a filter')
    parser.add_argument('-n', '--comment', help='Comment. In "list" mode, used as a regex pattern')
    parser.add_argument('-b', '--source', help='Source of the database, eg: Handover, Release load')

    args = parser.parse_args()

    if args.verbose is True:
        logging.basicConfig(level=logging.DEBUG, format='%(message)s')
    else:
        logging.basicConfig(level=logging.INFO, format='%(message)s')

    if args.uri.endswith('/') is False:
        args.uri = args.uri + '/'

    client = MetadataClient(args.uri)

    if args.action == 'submit':
        if args.input_file is None:
            logging.info("Submitting " + args.database_uri + " for metadata load")
            job_id = client.submit_job(args.database_uri, args.e_release, args.eg_release, args.release_date,
                                       args.current_release, args.email, args.comment, args.source)
            logging.info('Job submitted with ID ' + str(job_id))
        else:
            for line in args.input_file:
                uris = line.split()
                logging.info("Submitting " + uris[0] + " for metadata load")
                job_id = client.submit_job(uris[0], args.e_release, args.eg_release, args.release_date,
                                           args.current_release, args.email, args.comment, args.source)
                logging.info('Job submitted with ID ' + str(job_id))

    elif args.action == 'retrieve':
        job = client.retrieve_job(args.job_id)
        client.print_job(job, print_results=True, print_input=True)

    elif args.action == 'list':
        jobs = client.list_jobs(args.email, args.job_id, args.comment)
        if args.output_file is None:
            for job in jobs:
                client.print_job(job)
        else:
            args.output_file.write(json.dumps(jobs, indent=2))

    elif args.action == 'delete':
        client.delete_job(args.job_id)

    elif args.action == 'email':
        client.results_email(args.job_id, args.email)


if __name__ == '__main__':
    main()
