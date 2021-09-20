Changelog
=========

2.2 - Enable filtering of metadata job lists
--------------------------------------------
- Filter lists of jobs based on three criteria: email, comment, job id.
- Use ensembl-prodinf-core version 1.3.1

2.1 - Use ensembl-prodinf-core version 1.2
------------------------------------------
- Update requirements.txt
- Remove unused files

2.0 - Fix datacheck-client submit
---------------------------------
- Fix `datacheck_client` `submit_job()` call
- Add `target_url` optional argument to datacheck-client command

1.1 - Reuse VERSION in setup.py
---------------------------------
- Read VERSION file and use it in setup.py

1.0 - Initial package version
-----------------------------
- Created commands entry points
