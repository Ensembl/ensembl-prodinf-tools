#!/usr/bin/env python3
# See the NOTICE file distributed with this work for additional information
#   regarding copyright ownership.
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#       http://www.apache.org/licenses/LICENSE-2.0
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
# !/usr/bin/env python3
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
import os
import warnings
from collections import namedtuple

import requests
import sqlalchemy as sa
from sqlalchemy.engine.url import make_url

from ensembl.production.core.clients.dbcopy import DbCopyRestClient
from ensembl.utils import RemoteFileLoader

CopyJob = namedtuple('CopyJob',
                     'src_host, src_incl_db tgt_host email user')

Database = namedtuple('Database', 'name division')

GITHUB_BASE = 'https://raw.githubusercontent.com/Ensembl/ensembl-compara/release/{}/conf/{}/allowed_species.json'
DIVISION_HOST = {
    'vertebrates': 'st1',
    'plants': 'st3',
    'metazoa': 'st3'
}

DIVISION_ENS_MAP = {
    'vertebrates': 'EnsemblVertebrates',
    'protists': 'EnsemblProtists',
    'fungi': 'EnsemblFungi',
    'metazoa': 'EnsemblMetazoa',
    'plants': 'EnsemblPlants',
    'bacteria': 'EnsemblBacteria'
}

DIVISIONS = DIVISION_HOST.keys()


def parse_arguments():
    parser = argparse.ArgumentParser(description='Submit Copy Jobs form Report Updates')
    parser.add_argument('-s', '--source-server', required=False,
                        help='Source (e.g. sta-a, sta-b) or server name (e.g. mysql://user[:password]@server:port)')
    parser.add_argument('-t', '--target-server', required=False, default='mysql-ens-vertannot-staging',
                        help='Target (e.g. sta-a, sta-b) or server name (e.g. mysql://user[:password]@server:port))')
    parser.add_argument('-u', '--user', required=False, default=os.getenv('USER'),
                        help='User submitting the job')
    parser.add_argument('-d', '--division', required=False, help='Process only one division')
    parser.add_argument('-v', '--ens-version', required=False, default=os.getenv('ENS_VERSION'),
                        help='Force ENSEMBL version')
    parser.add_argument('--metadata-url',
                        help='Metadata database MySQL URL')
    parser.add_argument('--dbcopy-url', default=os.getenv('DBCOPY_API_URI'),
                        help='Copy database REST service URL')
    parser.add_argument('-D', '--dry-run', action='store_true',
                        help='Prints copy jobs without submitting them.')
    parser.add_argument('-F', '--fake', action='store_true',
                        help='Fake for local testing without mysql shortcut commands available.')
    args = parser.parse_args()
    return args


def _exec_cmd(cmd):
    return os.popen(cmd).readline().strip('\n')


def src_host(division, args):
    host = DIVISION_HOST[division]
    if int(args.ens_version) % 2 == 1:
        # even release
        host += '-b'
    if args.fake:
        return f"mysql://{host}:3306"
    db_host = _exec_cmd(host + " details url")
    db_url = make_url(db_host)
    return ':'.join([db_url.host, str(db_url.port)])


def tgt_host(args):
    if args.fake:
        return "mysql://vertannot-staging:3306"
    db_host = _exec_cmd(args.target_server + " details url")
    db_url = make_url(db_host)
    return ':'.join([db_url.host, str(db_url.port)])


def meta_host(args):
    if args.metadata_url:
        return args.metadata_url
    if args.fake:
        return 'mysql://ensembl@localhost:3306/ensembl_metadata'
    return _exec_cmd("meta1 details url") + 'ensembl_metadata'


def get_databases(metadata_engine, species, division, args):
    species_sql = """
        SELECT gd.dbname, d.name
        FROM genome g
        JOIN organism o ON g.organism_id = o.organism_id
        JOIN data_release dr ON g.data_release_id = dr.data_release_id
        JOIN genome_database gd ON g.genome_id = gd.genome_id
        JOIN division d on g.division_id = d.division_id
        WHERE dr.ensembl_version = :ens_version
        AND d.name = :division
        AND gd.type = 'core'
        AND o.name IN :species
        ORDER by gd.dbname
    """
    with metadata_engine.connect() as conn:
        species_dbs = conn.execute(sa.text(species_sql),
                                   ens_version=args.ens_version,
                                   division=DIVISION_ENS_MAP[division],
                                   species=tuple(species)).fetchall()
    result = species_dbs
    return list(map(lambda x: x[0], result))


def make_jobs(databases, division, args):
    jobs = []
    # parse list and chunk for less than 1024 chars
    chunks = [[]]
    parts = 0
    # Chunk databases list in required string length
    for database in databases:
        length = sum(len(s) for s in chunks[parts])
        if length + len(database) > 2000:
            parts += 1
            chunks.append([])
        chunks[parts].append(database)

    for chunk in chunks:
        src_serv = src_host(division, args)
        tgt_serv = tgt_host(args)
        if chunk:
            job = CopyJob(
                src_host=src_serv,
                src_incl_db=','.join(chunk),
                tgt_host=tgt_serv,
                user=args.user,
                email=f'{args.user}@ebi.ac.uk'
            )
            jobs.append(job)
    return jobs


def submit_jobs(client, jobs, args):
    for job in jobs:
        if args.dry_run:
            print(job)
        else:
            client.submit_job(*job)


def parse_species(ens_version):
    loader = RemoteFileLoader('json')
    compara_species = {}
    try:
        for division in DIVISIONS:
            uri = GITHUB_BASE.format(ens_version, division)
            compara_species[division] = loader.r_open(uri)
    except requests.HTTPError:
        warnings.warn(f"Unable to load compara from {uri}")
    return compara_species


def main():
    args = parse_arguments()
    compara_species = parse_species(args.ens_version)
    dbcopy_url = args.dbcopy_url
    metadata_url = args.metadata_url or meta_host(args)
    metadata_engine = sa.create_engine(metadata_url)
    copy_client = DbCopyRestClient(dbcopy_url)
    if not args.division:
        for division in DIVISIONS:
            species_names = compara_species[division]
            databases = get_databases(metadata_engine, species_names, division, args)
            if not databases:
                warnings.warn(f'No database retrieved for {division}')
            else:
                jobs = make_jobs(databases, division, args)
                submit_jobs(copy_client, jobs, args)
    else:
        species_names = compara_species[args.division]
        databases = get_databases(metadata_engine, species_names, args.division, args)
        if not databases:
            warnings.warn(f'No database retrieved for {args.division}')
        else:
            jobs = make_jobs(databases, args.division, args)
            submit_jobs(copy_client, jobs, args)


if __name__ == '__main__':
    main()
