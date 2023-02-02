# Brain Data Standards Queries
A repository for the Brain Data Standards Ontology services, queries and dumps. These queries are utilized to build dumps of the BDS ontology in json format. Provided dumps are indexed to the Solr and can be queried by the provided RESTful services.

* Dumps can be found in the [dumps](dumps) folder.
* Service details can be found in the [Swagger](http://ec2-3-143-113-50.us-east-2.compute.amazonaws.com:8484/bds)

## Solr

Latest version of the dump is also indexed to the [Solr](http://ec2-3-143-113-50.us-east-2.compute.amazonaws.com:8993/solr/#/bdsdump/query).

Solr is used as a document database to directly access entity metadata by IRI. This approach can also be used to traverse through related entities (parents, markers, references etc.): 

    http://ec2-3-143-113-50.us-east-2.compute.amazonaws.com:8993/solr/bdsdump/query?q=id:%22http://www.semanticweb.org/brain_data_standards/AllenDendClass_CS202002013_189%22

Version of the indexed ontology can be queried by:

    http://ec2-3-143-113-50.us-east-2.compute.amazonaws.com:8993/solr/bdsdump/query?q=id:%22ontology%22

## API

Search and query services are documented in [Swagger](http://ec2-3-143-113-50.us-east-2.compute.amazonaws.com:8484/bds)

Full-text search and autocomplete services are optimized query wrappers for Solr. Through [configuration](src/bds_api/config/search_config.ini) given parameters can be optimized:

* Which fields to return as response (_see `response_fields` parameter_):
  * For full-text search all fields and the lucene scores are returned
  * For autocomplete limited set of results are returned
* Importance of the fields (_see `field_weights` parameter_)
* Importance of the ontology domains (_see `domain_boosting` parameter_)

## Build

To build the service, please run the following commands in the project root folder. 

```
docker build -t bds/search-service .

docker run -p 8484:8080 -e SOLR_HOST=my_host -e SOLR_PORT=my_port -e SOLR_COLLECTION=bdsdump -e HTTPS=False -it bds/search-service 
```

_(Default value of the `HTTPS` parameter is `True`, so please set it based on your environment)_ 

If environment variables are not given to the run command, default values will be first read from the Dockerfile then from the [configuration](src/config/search_config.ini) file.


