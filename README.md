# Brain Data Standards Queries
A repository for the Brain Data Standards Ontology queries and dumps. These queries are utilized to build dumps of the BDS ontology in json format. Related dumps can be found in the [dumps](dumps) folder.

## Solr

Latest version of the dump is also indexed to the [Solr](http://ec2-3-143-113-50.us-east-2.compute.amazonaws.com:8993/solr/#/bdsdump/query).

Solr is used as a document database to directly access entity metadata by IRI. This approach can also be used to traverse through related entities (parents, markers, references etc.): 

    http://ec2-3-143-113-50.us-east-2.compute.amazonaws.com:8993/solr/bdsdump/query?q=id:%22http://www.semanticweb.org/brain_data_standards/AllenDendClass_CS202002013_189%22

Metadata of all taxonomies can be queried by:

    http://ec2-3-143-113-50.us-east-2.compute.amazonaws.com:8993/solr/bdsdump/query?q=type:%22taxonomy%22

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

### Filtering search results:

Filtering search/autocomplete results by species and rank are supported.

#### Filter by Species

Species can be specified by their simple name or by their NCBITaxon ID. When more than one species are provided, results that meet any of the species (OR the given species) are returned. Supported species are:

```
["mouse", "human", "marmoset", "euarchontoglires"]

or

["Mus musculus", "Homo sapiens", "Callithrix jacchus", "Euarchontoglires"]
```

Sample queries are:

    bds/api/search?query=L5/6%20NP&species=mouse

    bds/api/search?query=L5/6%20NP&species=mouse,human

    bds/api/search?query=L5/6%20NP&species="Callithrix jacchus"

    bds/api/search?query=L5/6%20NP&species="Mus musculus","Homo sapiens"

#### Filter by Rank

Supported ranks are: Cell Type, Subclass, Class and None

Sample queries are:

    bds/api/search?query=Lamp5%20Lhx6&rank=Cell Type
    bds/api/search?query=Lamp5%20Lhx6&rank=Cell Type,Class

### Build:

To build the service, please run the following commands in the project root folder. 

```
docker build -t bds/search-service .

docker run -p 8484:8080 -e SOLR_HOST=my_host -e SOLR_PORT=my_port SOLR_COLLECTION=bdsdump -it bds/search-service 
```

If environment variables are not given to the run command, default values will be first read from the Dockerfile then from the [configuration](src/config/search_config.ini) file.