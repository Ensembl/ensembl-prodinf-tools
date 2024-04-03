EnsEMBL - Production Tools
==========================

Collection of Python command line scripts for interacting with EnsEMBL
Production Web Services & libraries.


System Requirements
-------------------

- Python 3.7+


Installation
------------

This repository can be installed as a Python package.
We recommend to install the latest release tag instead of the default branch.

For example, using _pip_:
```
pip install git+https://github.com/Ensembl/ensembl-prodinf-tools.git@<Release Tag>
```


Usage
-----

Command line tools provided by this package:


#### `datacheck-client`

Tool for submitting/retrieving DataChecks to/from EnsEMBL Production DC Service


#### `dbcopy-client`

Tool for managing DBCopy Request Jobs


#### `gifts-client`

Tool for submitting/retrieving Gifts Jobs to/from EnsEMBL Production Gifts Service


#### `handover-client`

Tool for submitting/retrieving Handover Jobs to/from EnsEMBL Production Handover Service



Please refer to [Docs](./docs) folder for each tool detailed usage.
