import logging
from neo4j import GraphDatabase
from abc import ABC, abstractmethod
from neo4j_config import neo4j_config


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
        MATCH (i:Individual)-[:exemplar_data_of]->(c:Class) 
        WHERE i.curie = 'AllenDend:' + $accession 
        OPTIONAL MATCH (c)-[scr:SUBCLASSOF]->(parent) 
        OPTIONAL MATCH (c)-[er:expresses]->(marker)
        OPTIONAL MATCH (c)-[src:source]->(reference) 
        RETURN apoc.map.mergeList([properties(c), {tags: labels(c)}]) AS class_metadata, 
        collect(distinct {relation: properties(scr), class_metadata: properties(parent)}) AS parents, 
        collect(distinct { relation: properties(er), class_metadata: properties(marker)}) AS markers,
        collect(distinct { relation: properties(src), class_metadata: properties(reference)}) AS references 
        """

    def parse_response(self, response):
        node = {}
        for record in response:
            node = {"class_metadata": record["class_metadata"], "parents": record["parents"],
                    "markers": record["markers"], "references": record["references"]}

        return node


class ListAllAllenIndividuals(BDSQuery):

    def get_query(self):
        log.info("Executing: ListAllAllenIndividuals")
        return """
        MATCH (i:Individual)-[:exemplar_data_of]->(c:Class)
        WHERE c.curie STARTS WITH 'AllenDendClass:'
        RETURN DISTINCT i.curie 
        """

    def parse_response(self, response):
        nodes = []
        for record in response:
            nodes.append(record[0])

        return nodes


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

