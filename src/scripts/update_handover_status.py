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

import sys
import click
import datetime
import re
from elasticsearch import Elasticsearch, TransportError, NotFoundError, RequestError

@click.command()
@click.option('-h', '--host',  help="Elastic search Host Name", default="localhost", show_default=True)
@click.option('-p', '--port',  type=int, help="Elastic search Host Port", default=9200, show_default=True)
@click.option('-i', '--index', help="Elastic search Index ", required=True)
@click.option('-t', '--handover_token', help="Handover token to update the status", required=True)
def main(host, port, index, handover_token):
  """
    Update's given handover token status to success 

    Example : python update_handover_status.py -h es.production.ensembl.org -p 80 -i reports_vert -t 04c06668-8ef6-11ea-bc10-005056ab00f0
  """
  try:
      es = Elasticsearch([{'host': host, 'port': port}])
      res_error = es.search(
                             index=index, 
                              body={
                                "query": {
                                  "bool": {
                                    "must": [ 
                                              {"term": {"params.handover_token.keyword": str(handover_token)}},
                                              {"term": {"report_type.keyword": "INFO"}},
                                              {"query_string": {"fields": ["message"],"query":"Metadata AND failed"}}
                                            ],
                                    "must_not": [], 
                                    "should": []
                                  }
                                },
                                "from": 0, "size": 1,
                                "sort": [{"report_time": {"order": "desc"}}], "aggs": {}}
                           )

      if len(res_error['hits']['hits']) == 0:
        raise Exception(f"No Hits Found for Handover Token {handover_token}" )

      #set handover message to success
      result = res_error['hits']['hits'][0]['_source']
      h_id = res_error['hits']['hits'][0]['_id']
      result['report_time'] = str(datetime.datetime.now().isoformat())[:-3]
      result['message'] = 'Metadata load complete, Handover successful'
      result['report_type'] = 'INFO'
      res = es.update(index=index, id=h_id, doc_type='report' , body={ "doc": result })
  except Exception as e  :
      print(str(e))
      sys.exit(1)

if __name__ == "__main__":
  main()