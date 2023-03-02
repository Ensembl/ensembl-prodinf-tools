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
import re

from ensembl.production.metadata.updater import CoreMetaUpdater
from sqlalchemy.engine.url import make_url


def main():
    parser = argparse.ArgumentParser(
        description='Method for loading data from a specific database to a metadata registry')

    parser.add_argument('-m', '--uri', help='Metadata database URI', required=True)
    parser.add_argument('-d', '--database_uri', help='URI of database to load', required=True)
    parser.add_argument('-r', '--release', help='Release')

    args = parser.parse_args()

    db_url = make_url(args.database_uri)

    if '_compara_' in db_url.database:
        raise Exception("compara not implemented yet")
    elif '_variation_' in db_url.database:
        raise Exception("variation not implemented yet")
    elif '_funcgen_' in db_url.database:
        raise Exception("funcgen not implemented yet")
    elif '_core_' in db_url.database:
        core = CoreMetaUpdater(args.uri, args.database_uri, args.release)
        core.process_core()
    elif '_otherfeatures_' in db_url.database:
        raise Exception("otherfeatures not implemented yet")
    elif '_rnaseq_' in db_url.database:
        raise Exception("rnaseq not implemented yet")
    elif '_cdna_' in db_url.database:
        raise Exception("cdna not implemented yet")
    # Dealing with other versionned databases like mart, ontology,...
    elif re.match('^\w+_?\d*_\d+$', db_url.database):
        raise Exception("other not implemented yet")
    elif re.match(
            '^ensembl_accounts|ensembl_archive|ensembl_autocomplete|ensembl_metadata|ensembl_production|ensembl_stable_ids|ncbi_taxonomy|ontology|website',
            db_url.database):
        raise Exception("other not implemented yet")
    elif '_collection_' in db_url.database:
        raise Exception("Collection not implemented yet")
    else:
        raise "Can't find data_type for database " + db_url.database


if __name__ == '__main__':
    main()
