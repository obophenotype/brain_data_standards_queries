import logging
from neo4j import GraphDatabase
from abc import ABC, abstractmethod
from bds_api.dumps.neo4j_config import neo4j_config


log = logging.getLogger(__name__)


class BDSQuery(ABC):
    """
    Abstract base class for Bran Data Standards queries.
    """

    def __init__(self):
        try:
            self.driver = GraphDatabase.driver(neo4j_config["bolt_url"],
                                               auth=(neo4j_config["user"], neo4j_config["password"]))
        except Exception:
            log.exception("Failed to create the Neo4j driver.")

    def close(self):
        if self.driver is not None:
            self.driver.close()

    def execute_query(self, parameters=None, **kwparameters):
        session = None
        response = None
        try:
            session = self.driver.session(database="neo4j")
            log.info("Executing query...")
            response = list(session.run(query=self.get_query(), parameters=parameters, kwparameters=kwparameters))
        except Exception:
            log.exception("Query failed execution failed.")
        finally:
            if session is not None:
                session.close()

        result = self.parse_response(response)
        self.close()
        return result

    @abstractmethod
    def get_query(self):
        pass

    @abstractmethod
    def parse_response(self, response):
        pass


class IndividualDetailsQuery(BDSQuery):

    def get_query(self):
        log.info("Executing: IndividualDetailsQuery")
        return """
        MATCH (i:Individual) 
        WHERE i.curie = 'PCL:' + $accession  
        OPTIONAL MATCH (i:Individual)-[:exemplar_data_of]->(c:Class)
        OPTIONAL MATCH (c)-[scr:SUBCLASSOF]->(parent) 
        OPTIONAL MATCH (c)-[er:expresses]->(marker)
        OPTIONAL MATCH (c)-[:SUBCLASSOF*]->()-[erp:expresses]->(parent_marker)
        OPTIONAL MATCH (c)-[src:source]->(reference) 
        OPTIONAL MATCH (c)-[:in_taxon]->(in_taxon) 
        OPTIONAL MATCH (c)-[:SUBCLASSOF*]->()-[:in_taxon]->(in_taxon_parent)
        OPTIONAL MATCH (c)-[:has_soma_location]->(soma_location) 
        OPTIONAL MATCH (c)-[:SUBCLASSOF*]->()-[:has_soma_location]->(parent_soma_location)
        OPTIONAL MATCH (c)-[:in_historical_homology_relationship_with]->(homologous_to)
        RETURN apoc.map.mergeList([properties(i), {tags: labels(i)}]) AS indv_metadata,
        collect(distinct { tags: labels(c), class_metadata: properties(c)}) AS class_metadata,
        collect(distinct { relation: properties(scr), class_metadata: properties(parent)}) AS parents, 
        collect(distinct { relation: properties(er), class_metadata: properties(marker)}) AS markers,
        collect(distinct { relation: properties(erp), class_metadata: properties(parent_marker)}) AS parent_markers,
        collect(distinct { relation: properties(src), class_metadata: properties(reference)}) AS references,
        collect(distinct { taxon: properties(in_taxon), parent_taxon: properties(in_taxon_parent)}) AS taxonomy, 
        collect(distinct { soma_location: properties(soma_location), parent_soma_location: properties(parent_soma_location)}) AS region,
        collect(distinct { class_metadata: properties(homologous_to)}) AS homologous_to
        """

    def parse_response(self, response):
        node = {}
        for record in response:
            node = {"class_metadata": record["class_metadata"], "indv_metadata": record["indv_metadata"],
                    "parents": record["parents"], "markers": record["markers"],
                    "parent_markers": record["parent_markers"], "references": record["references"],
                    "taxonomy": record["taxonomy"], "region": record["region"], "homologous_to": record["homologous_to"]
                    }

        return node


class ListAllAllenIndividuals(BDSQuery):

    def get_query(self):
        log.info("Executing: ListAllAllenIndividuals")
        return """
        MATCH (i:Individual)
        WHERE EXISTS(i.cell_type_rank)
        RETURN DISTINCT i.curie 
        """

    def parse_response(self, response):
        nodes = []
        for record in response:
            nodes.append(record[0])

        return nodes


class ListAllTaxonomies(BDSQuery):

    def get_query(self):
        log.info("Executing: ListAllTaxonomies")
        return """
        MATCH (i:Individual)-[]->(c:Class) 
        WHERE c.curie = 'PCL:0010002' 
        RETURN i 
        """

    def parse_response(self, response):
        taxonomies = dict()
        for record in response:
            taxonomies[record[0]["label"]] = record[0]

        return taxonomies


class GetOntologyMetadata(BDSQuery):

    def get_query(self):
        log.info("Executing: GetOntologyMetadata")
        return """
        MATCH (ontology:Ontology) 
        RETURN properties(ontology) AS ont_metadata
        LIMIT 1
        """

    def parse_response(self, response):
        for record in response:
            return {"name": record["ont_metadata"]["label"], "version": record["ont_metadata"]["versionInfo"]}
        return None

