# Dumps

Two sets of the same data are provided. 

`individuals_metadata_{date}.json` provides data in a nested format:

```
json
└───ontology
│   │   name
│   │   version   
│
└───entities
│   └───entity1
│       │   node            (name of the entity)
│       │   class_metadata  (metadata of the entity)
│       │   parents         (list of parents' metadata)
│       │   markers         (list of markers expressing the entity)
│       │   references      (references where definitions come from)
│   └───entity2
│       │   node
│       │   class_metadata
│       │   parents
│       │   markers
│       │   references
│   └───...
```

`individuals_metadata_solr_{date}.json` provides the same data in a flat format, which is compatible with Solr. 
Id references (to parents, markers, references etc.) should be traced to access their details. 

Latest version of the solr dump is indexed to [Solr](http://ec2-3-143-113-50.us-east-2.compute.amazonaws.com:8993/solr/#/bdsdump/query).