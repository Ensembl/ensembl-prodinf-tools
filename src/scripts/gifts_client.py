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

from ensembl.production.core.clients.gifts import GIFTsClient


def main():
    parser = argparse.ArgumentParser(description='Ensembl Production: Interact with the GIFTs services')

    parser.add_argument('-u', '--uri', help='GIFTs Production service REST URI', required=True)
    parser.add_argument('-a', '--action', help='Action to take', choices=['submit', 'retrieve', 'list'], required=True)
    parser.add_argument('-i', '--job_id', help='GIFTs job identifier to retrieve')
    parser.add_argument('-v', '--verbose', help='Verbose output', action='store_true')
    parser.add_argument('-o', '--output_file', help='File to write output as JSON', type=argparse.FileType('w'))
    parser.add_argument('-r', '--ensembl_release', help='Ensembl release number', required=True)
    parser.add_argument('-n', '--environment', help='Execution environment (dev or staging)', required=True)
    parser.add_argument('-e', '--email', help='Email address for pipeline reports', required=True)
    parser.add_argument('-t', '--tag', help='Tag for annotating/retrieving a submission')

    args = parser.parse_args()

    if args.verbose == True:
        logging.basicConfig(level=logging.DEBUG, format='%(message)s')
    else:
        logging.basicConfig(level=logging.INFO, format='%(message)s')

    if args.uri.endswith('/') == False:
        args.uri = args.uri + '/'

    client = GIFTsClient(args.uri)

    if args.action == 'submit':
        job_id = client.submit_job(args.ensembl_release, args.environment, args.email, args.tag)
        logging.info('Job submitted with ID ' + str(job_id))

    elif args.action == 'retrieve':
        job = client.retrieve_job(args.job_id)
        client.print_job(job, print_results=True, print_input=True)

    elif args.action == 'list':
        jobs = client.list_jobs(args.output_file, args.tag)


if __name__ == '__main__':
    main()
