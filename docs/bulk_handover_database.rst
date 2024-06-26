**********************
Bulk database handover
**********************

Overview
########

The Production infrastructure interface contains a handover service `handover endpoint`
This document describes how to use the `HandoverClient` class to interact with the endpoint and bulk database handover.

List of databases to handover
#############################

Create file with list of databases to handover, e.g: handover_databases.txt

.. code-block::

  cavia_porcellus_funcgen_91_4
  homo_sapiens_funcgen_91_38
  mus_musculus_funcgen_91_38
  pan_troglodytes_funcgen_91_3

Or for all the database of a given division:

Non Vertebrates:
================

* Bacteria - EB
* Protists - EPr
* Fungi	- EF
* Metazoa - EM
* Plants - EPl
* Pan - EP

To get the list of databases for Fungi:

.. code-block::

  RELEASE=41
  perl ensembl-metadata/misc_scripts/get_list_databases_for_division.pl $(mysql-ens-meta-prod-1 details script) -division fungi -release $RELEASE > fungi_handover.txt


Vertebrates:
============

.. code-block::

  RELEASE=94
  perl ensembl-metadata/misc_scripts/get_list_databases_for_division.pl $(mysql-ens-meta-prod-1 details script) -division vertebrates -release $RELEASE > vertebrates_handover.txt

Submit the jobs using Python REST db copy endpoint:
###################################################

To Submit the job via the REST endpoint

.. code-block::

    pyenv activate production-tools

For Vertebrates:

.. code-block::

  DATABASE_SERVER=$(mysql-ens-general-prod-1 details url)
  ENDPOINT=http://PROD_SERVICE_URI/api/vertebrates/handovers/
  EMAIL=john.doe@ebi.ac.uk
  RELEASE=105
  DESCRIPTION="Handover $RELEASE new databases"

  for db in $(cat vertebrates_handover.txt); do
    handover-client --action submit --uri ${ENDPOINT} --src_uri "${DATABASE_SERVER}${db}" --email "${EMAIL}" --description "${DESCRIPTION}";
  done

For Fungi/Protists/Bacteria:

.. code-block:: bash

  DATABASE_SERVER=$(mysql-ens-general-prod-1 details url)
  ENDPOINT=http://PROD_SERVICE_URI/api/microbes/handovers/
  EMAIL=john.doe@ebi.ac.uk
  DESCRIPTION="Handover 105 Fungi databases"

  for db in $(cat fungi_handover.txt); do
    handover-client --action submit --uri ${ENDPOINT} --src_uri "${DATABASE_SERVER}${db}" --email "${EMAIL}" --description "${DESCRIPTION}";
  done


Script usage:
#############

The script accept the following arguments:

::

  usage: handover-client [-h] -u URI -a
                            {submit,retrieve,list,delete,events,processes} [-v]
                            -s SRC_URI -e EMAIL -t
                            {new_genome,new_genebuild,new_assembly,other} -c
                            DESCRIPTION [-n EMAIL_NOTIFICATION]

  Handover via a REST service

  optional arguments:
    -h, --help            show this help message and exit
    -u URI, --uri URI     HC REST service URI
    -a {submit,retrieve,list,delete,events,processes}, --action {submit,retrieve,list,delete,events,processes}
                          Action to take
    -v, --verbose         Verbose output
    -s SRC_URI, --src_uri SRC_URI
                          URI of database to hand over
    -e EMAIL, --email EMAIL
                          Email address
    -c DESCRIPTION, --description DESCRIPTION
                          Description
    -n EMAIL_NOTIFICATION, --email_notification EMAIL_NOTIFICATION
                          Get email notification of handover progress

Check job status
################

You can check job status either on the production interface: `<http://PROD_SERVICE_URI/>`_ or `<http://PROD_SERVICE_URI/api/microbes/handovers/jobs>`_ for microbes

or using the Python client:

.. code-block:: bash

  pyenv activate production-tools

  handover-client --action list --uri http://PROD_SERVICE_URI/api/vertebrates/handovers/
  handover-client --action list --uri http://PROD_SERVICE_URI/api/microbes/handovers/

If you have handed over many databases, you can get a summary of your handover:

.. code-block:: bash

  pyenv activate production-tools

  handover-client --action summary --uri http://PROD_SERVICE_URI/api/vertebrates/handovers/ -e john.doe@ebi.ac.uk
  handover-client --action summary --uri http://PROD_SERVICE_URI/api/microbes/handovers/ -e john.doe@ebi.ac.uk

If a database was handed over multiple times, you will only see the latest one.
