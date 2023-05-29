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

import unittest
from collections import namedtuple

SpeciesArgs = namedtuple('SpeciesArgs',
                         'include_divisions exclude_divisions statuses')
JobArgs = namedtuple('JobArgs',
                     'source_server target_server convert_innodb skip_optimize email')


class TestServicesClient(unittest.TestCase):

    def test_copy_client(self):
        # TODO setup services accordinly
        self.assertTrue(True)

    def test_handover_client(self):
        # TODO setup services accordinly
        self.assertTrue(True)

    def test_metadata_client(self):
        # TODO setup services accordinly
        self.assertTrue(True)

    def test_datacheck_client(self):
        # TODO setup services accordinly
        self.assertTrue(True)

    def test_event_client(self):
        # TODO setup services accordinly
        self.assertTrue(True)

    def test_gifts_client(self):
        # TODO setup services accordinly
        self.assertTrue(True)

