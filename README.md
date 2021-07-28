# Brain Data Standards Queries
A repository for the Brain Data Standards Ontology cypher queries.

These queries are utilized to build dumps of the BDS ontology in json format. Related dumps can be found in the [dumps](dumps) folder.

## Solr

Latest version of the dump is also indexed to the [Solr](http://ec2-3-143-113-50.us-east-2.compute.amazonaws.com:8993/solr/#/bdsdump/query).

Solr can be used to search BDS entities by label (or by any other field): 

    http://ec2-3-143-113-50.us-east-2.compute.amazonaws.com:8993/solr/bdsdump/query?q=label:*L5%20IT* 

Or directly access to entity metadata by IRI. This approach can also be used to traverse through related entities (parents, markers, references etc.): 

    http://ec2-3-143-113-50.us-east-2.compute.amazonaws.com:8993/solr/bdsdump/query?q=id:%22http://www.semanticweb.org/brain_data_standards/AllenDendClass_CS202002013_189%22