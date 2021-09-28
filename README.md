# Brain Data Standards Queries
A repository for the Brain Data Standards Ontology queries and dumps. These queries are utilized to build dumps of the BDS ontology in json format. Related dumps can be found in the [dumps](dumps) folder.

## Solr

Latest version of the dump is also indexed to the [Solr](http://ec2-3-143-113-50.us-east-2.compute.amazonaws.com:8993/solr/#/bdsdump/query).

Solr is used as a document database to directly access entity metadata by IRI. This approach can also be used to traverse through related entities (parents, markers, references etc.): 

    http://ec2-3-143-113-50.us-east-2.compute.amazonaws.com:8993/solr/bdsdump/query?q=id:%22http://www.semanticweb.org/brain_data_standards/AllenDendClass_CS202002013_189%22

Version of the indexed ontology can be queried by:

    http://ec2-3-143-113-50.us-east-2.compute.amazonaws.com:8993/solr/bdsdump/query?q=id:%22ontology%22

## Search Service

This project also provides restful services for full-text search and autocomplete support. These services are optimized query wrappers for Solr search queries. Through [configuration](src/config/search_config.ini) given parameters can be optimized:

* Which fields to return as response (_see `response_fields` parameter_):
  * For full-text search all fields and the lucene scores are returned
  * For autocomplete limited set of results are returned
* Importance of the fields (_see `field_weights` parameter_)
* Importance of the ontology domains (_see `domain_boosting` parameter_)

### Autocomplete:

    http://ec2-3-143-113-50.us-east-2.compute.amazonaws.com:8484/bds/api/autocomplete?query=L5/6%20NP

### Full-text search:

    http://ec2-3-143-113-50.us-east-2.compute.amazonaws.com:8484/bds/api/search?query=L5/6%20NP