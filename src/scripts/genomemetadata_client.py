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
import json
from ensembl.production.core.clients.genomemetadata import GenomeMetadataRestClient


def handle_runtime_error(error):
    logging.error("Error: %s", error)
    sys.exit(1)


def handle_key_error(error, job):
    msg = f"Invalid response. Missing argument: '{error}'. Response: {job}"
    logging.error(msg)


def main():
    parser = argparse.ArgumentParser(description='Interact with ensembl genome REST client')
    parser.add_argument('-u', '--uri', required=True, help='Base URI, api. ex:https://services.test.ensembl-production.ebi.ac.uk/')
    parser.add_argument('-a', '--action', choices=['submit', 'retrieve', 'list', 'update'], required=True, help='Action to take. Options: submit (only for dataset), retrieve, list')
    parser.add_argument('-t', '--table', choices=['datasets', 'genomes'], required=True, help='Table. Options: datasets, genomes')
    parser.add_argument('-g', '--guuid', help='UUID of genome to retrieve or submit. Required for dataset submission')
    parser.add_argument('-i', '--duuid', help='UUID of dataset to retrieve or update')
    parser.add_argument('--user', help='User registered with this service. Required for dataset submission')
    parser.add_argument('-n', '--name', help='Dataset name. Required for dataset submission')
    parser.add_argument('-d', '--description', help='Description of dataset. Required for dataset submission')
    parser.add_argument('-l', '--label', help='Dataset label. Required for dataset submission')
    parser.add_argument('-y', '--type', help='Dataset type name. Required for dataset submission')
    parser.add_argument('-s', '--source_name', help='Dataset source name. Required for dataset submission')
    parser.add_argument('-z', '--source_type', help='Dataset source type. Required for dataset submission')
    parser.add_argument('-r', '--dataset_attribute', nargs=2, action='append', help='List of dataset attributes in the form "-da name value" ')
    parser.add_argument('-p', '--payload', help='Alternate method with direct submission of a json. Only for create')
    parser.add_argument('--pass', '--password', help='Password')

    args = parser.parse_args()

    client = GenomeMetadataRestClient(args.uri)
    try:
        if args.action == 'submit':
            if args.payload is not None:
                client.create_dataset(args.payload)
            else:
                required_args = ['guuid', 'user', 'name', 'description', 'label', 'type', 'source_name', 'source_type']
                if [arg for arg in required_args if getattr(args, arg) is None]:
                    raise ValueError("Argument missing. Required arguments are " + ", ".join(required_args))
                dataset_attribute = []
                for pair in args.dataset_attribute:
                    name, value = pair
                    dataset_attribute.append({"name": name, "value": value})

                payload = {
                    "user": args.user,
                    "name": args.name,
                    "description": args.description,
                    "label": args.label,
                    "dataset_type": args.type,
                    "dataset_source": {
                        "name": args.source_name,
                        "type": args.source_type
                    },
                    "genome_uuid": args.guuid,
                    "dataset_attribute": dataset_attribute,
                }
                json_payload = json.dumps(payload)
                client.create_dataset(json_payload)

        elif args.action == 'list':
            if args.table == 'datasets':
                print (client.get_all_datasets())
            elif  args.table == 'genomes':
                print (client.get_all_genomes())

        elif args.action == 'retrieve':
            if args.table == 'datasets':
                if args.duuid is None:
                    raise ValueError("Argument missing. Required arguments for dataset get is duuid")
                print (client.get_dataset_by_uuid(args.duuid))

            elif args.table == 'genomes':
                if args.guuid is None:
                    raise ValueError("Argument missing. Required arguments for genome  is guuid")
                print (client.get_genome_by_uuid(args.guuid))

        elif args.action == 'update':
            required_args = ['dataset_uuid', 'user']
            if [arg for arg in required_args if getattr(args, arg) is None]:
                raise ValueError("Argument missing. Required arguments for PUT are " + ", ".join(required_args))

            dataset_attribute = []
            if args.dataset_attribute:
                for name, value in args.dataset_attribute:
                    dataset_attribute.append({"name": name, "value": value})

            payload = {
                "user": args.user,
                "dataset_uuid": args.dataset_uuid,
                "dataset_attribute": dataset_attribute
            }
            json_payload = json.dumps(payload)
            client.update_dataset(json_payload)

    except RuntimeError as err:
        handle_runtime_error(err)


if __name__ == '__main__':
    main()
