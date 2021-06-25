******************
Bulk Database Copy
******************

Overview
########

The Production infrastructure interface allows the copy of database using the Production Services DBCopy endpoint in the background.
This document describes how to use `dbcopy-client` command line tool to interact with the endpoint and bulk copy databases.

List of databases to copy
#########################

Create file with list of databases to copy, e.g: ``db_to_copy.txt``

::

  cavia_porcellus_funcgen_91_4
  homo_sapiens_funcgen_91_38
  mus_musculus_funcgen_91_38
  pan_troglodytes_funcgen_91_3

Or for all the database of a given division:

1.Please find below the list of divisions short names:

* bacteria - EnsemblBacteria
* protists - EnsemblProtists
* fungi	- EnsemblFungi
* metazoa - EnsemblMetazoa
* plants - EnsemblPlants
* pan - EnsemblPan
* vertebrates - EnsemblVertebrates

To get the list of databases for Fungi:

.. code-block:: bash

  RELEASE=38
  perl ensembl-metadata/misc_scripts/get_list_databases_for_division.pl $(mysql-ens-meta-prod-1 details script) -division fungi -release $RELEASE > fungi_db_to_copy.txt

2. Vertebrates:

.. code-block:: bash

  RELEASE=91
  perl ensembl-metadata/misc_scripts/get_list_databases_for_division.pl $(mysql-ens-meta-prod-1 details script) -division vertebrates -release $RELEASE > vertebrates_db_to_copy.txt


Submit the jobs using Python REST db copy endpoint
##################################################

To Submit the job via the REST endpoint:

.. code-block::

    pyenv activate production-tools

N.B. Make sure `PYTHONPATH` is not set when activating a virtual environment

.. code-block:: bash

  SOURCE_SERVER=$(mysql-ens-vertannot-staging details url) #e.g: mysql://ensro@mysql-ens-vertannot-staging:4573/
  TARGET_SERVER=$(mysql-ens-general-prod-1-ensadmin details url)
  ENDPOINT=http://production-services.ensembl.org/api/dbcopy/requestjob/

  for db in $(cat db_to_copy.txt); do
    dbcopy-client --action submit --uri ${ENDPOINT} --source_db_uri "${SOURCE_SERVER}${db}" --target_db_uri "${TARGET_SERVER}${db}" --drop 1
  done

If activating a virtual environment is not feasible, `dbcopy-client` can be invoked directly:

.. code-block::

   $(pyenv root)/versions/production-tools/bin/dbcopy-client


Script usage
############

The script accept the following arguments:

.. code-block:: bash

    usage: dbcopy-client [-h] -u URI -a
                         {submit,retrieve,list,delete,email,kill_job} [-j JOB_ID]
                         [-v] -s SRC_HOST -t TGT_HOST [-i SRC_INCL_DB]
                         [-k SRC_SKIP_DB] [-p SRC_INCL_TABLES]
                         [-d SRC_SKIP_TABLES] [-n TGT_DB_NAME] [-o SKIP_OPTIMIZE]
                         [-w WIPE_TARGET] [-c CONVERT_INNODB] -e EMAIL_LIST -r
                         USER [--skip-check]

    Copy Databases via a REST service

    optional arguments:
      -h, --help            show this help message and exit
      -u URI, --uri URI     Copy database REST service URI
      -a {submit,retrieve,list,delete,email,kill_job}, --action {submit,retrieve,list,delete,email,kill_job}
                            Action to take
      -j JOB_ID, --job_id JOB_ID
                            Copy job identifier to retrieve
      -v, --verbose         Verbose output
      -s SRC_HOST, --src_host SRC_HOST
                            Source host for the copy in the form host:port
      -t TGT_HOST, --tgt_host TGT_HOST
                            List of hosts to copy to in the form
                            host:port,host:port
      -i SRC_INCL_DB, --src_incl_db SRC_INCL_DB
                            List of databases to include in the copy. If not
                            defined all the databases from the server will be
                            copied
      -k SRC_SKIP_DB, --src_skip_db SRC_SKIP_DB
                            List of database to exclude from the copy
      -p SRC_INCL_TABLES, --src_incl_tables SRC_INCL_TABLES
                            List of tables to include in the copy
      -d SRC_SKIP_TABLES, --src_skip_tables SRC_SKIP_TABLES
                            List of tables to exclude from the copy
      -n TGT_DB_NAME, --tgt_db_name TGT_DB_NAME
                            Database name on target server. Used for renaming
                            databases
      -o SKIP_OPTIMIZE, --skip_optimize SKIP_OPTIMIZE
                            Skip database optimization step after the copy. Useful
                            for very large databases
      -w WIPE_TARGET, --wipe_target WIPE_TARGET
                            Delete target database before copy
      -c CONVERT_INNODB, --convert_innodb CONVERT_INNODB
                            Convert InnoDB tables to MyISAM after copy
      -e EMAIL_LIST, --email_list EMAIL_LIST
                            Email where to send the report
      -r USER, --user USER  User name
      --skip-check          Skip host:port server validation


Check job status
################

You can check job status either on the production interface: `<http://production-services.ensembl.org/ensembl_dbcopy/requestjob/>`_ :

or using the Python client:

.. code-block:: bash

  dbcopy-client --action list --uri http://production-services.ensembl.org/api/dbcopy/requestjob/ -s <src_host> -t <tgt_host> -e <email> -r <user>
