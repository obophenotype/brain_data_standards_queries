import flask
import requests
import ast
import logging
from flask import request
from flask_restplus import Resource
from bds_api.restplus import api
from bds_api.endpoints.search_config import search_config, autocomplete_config
from bds_api.exception.api_exception import BDSApiException
from bds_api.endpoints.parser import search_arguments, get_arguments

ns = api.namespace('api', description='Brain Data Standards Ontologies API')

log = logging.getLogger(__name__)

solr_escape_rules = {'+':r'\+','-':r'\-','&':r'\&','|':r'\|','!':r'\!','(':r'\(',')':r'\)','{':r'\{','}':r'\}',
                     '[':r'\[',']':r'\]','~':r'\~','*':r'\*','?':r'\?',':':r'\:','"':r'\"',';':r'\;','/':r'\/'}

species_mapping = {"mouse": "Mus musculus",
                   "human": "Homo sapiens",
                   "marmoset": "Callithrix jacchus",
                   "euarchontoglires": "Euarchontoglires"}
ranks = ["Cell Type", "Subclass", "Class", "None"]


@ns.route('/search', methods=['GET'])
class SearchEndpoint(Resource):

    @api.expect(search_arguments, validate=True)
    def get(self):
        """
        Search service wrapper for Solr.

        Search service wrapper for Solr. Search and response fields, their weights are configured through the [configuration](https://github.com/obophenotype/brain_data_standards_queries/blob/main/src/config/search_config.ini) file.

        * query (mandatory): search terms

        ```
        ?query=L5/6%20NP
        ```

        * species (optional): Filters documents for the given species. Species can be specified by their simple name or by their NCBITaxon label. When more than one species are provided, results that meet any of the species (OR the given species) are returned.
        Supported species are:
        ["mouse", "human", "marmoset", "euarchontoglires"] or ["Mus musculus", "Homo sapiens", "Callithrix jacchus", "Euarchontoglires"]

        ```
        ?query=L5/6%20NP&species=mouse
        ?query=L5/6%20NP&species=mouse,human
        ?query=L5/6%20NP&species="Callithrix jacchus"
        ?query=L5/6%20NP&species="Mus musculus","Homo sapiens"
        ```

        * rank (optional): Filters documents for the given Cell Type ranks. Supported ranks are: Cell Type, Subclass, Class and None

        ```
        ?query=Lamp5%20Lhx6&rank=Cell Type
        ?query=Lamp5%20Lhx6&rank=Cell Type,Class
        ```


        Return: list of related Solr documents

        """
        request_url = generate_request(search_config)
        log.info("Request: " + request_url)
        solr_response = requests.get(request_url)
        response = flask.jsonify(solr_response.json())
        add_cors_headers(response)
        return response


@ns.route('/autocomplete', methods=['GET'])
class AutocompleteEndpoint(Resource):

    @api.expect(search_arguments, validate=True)
    def get(self):
        """
        Autocomplete service wrapper for Solr.

        Autocomplete service wrapper for Solr. Compared to search service, returns limited fields that are specified in the [configuration](https://github.com/obophenotype/brain_data_standards_queries/blob/main/src/config/search_config.ini) file.

        * query (mandatory): search terms

        ```
        ?query=L5/6%20NP
        ```

        * species (optional): Filters documents for the given species. Species can be specified by their simple name or by their NCBITaxon label. When more than one species are provided, results that meet any of the species (OR the given species) are returned.
        Supported species are:
        ["mouse", "human", "marmoset", "euarchontoglires"] or ["Mus musculus", "Homo sapiens", "Callithrix jacchus", "Euarchontoglires"]

        ```
        ?query=L5/6%20NP&species=mouse
        ?query=L5/6%20NP&species=mouse,human
        ?query=L5/6%20NP&species="Callithrix jacchus"
        ?query=L5/6%20NP&species="Mus musculus","Homo sapiens"
        ```

        * rank (optional): Filters documents for the given Cell Type ranks. Supported ranks are: Cell Type, Subclass, Class and None

        ```
        ?query=Lamp5%20Lhx6&rank=Cell Type
        ?query=Lamp5%20Lhx6&rank=Cell Type,Class
        ```


        Return: list of related Solr documents

        """
        request_url = generate_request(autocomplete_config)
        log.info("Request: " + request_url)
        solr_response = requests.get(request_url)
        response = flask.jsonify(solr_response.json())
        add_cors_headers(response)
        return response


@ns.route('/taxonomies', methods=['GET'])
class TaxonomiesEndpoint(Resource):

    def get(self):
        """
        Taxonomies listing

        Returns the metadata of all registered taxonomies.
        """
        request_url = "http://{host}:{port}/solr/{collection}/query?q=type:\"taxonomy\""\
            .format(host=search_config["solr_host"], port=search_config["solr_port"],
                    collection=search_config["solr_collection"])
        log.info("Request: Listing all taxonomies.")
        solr_response = requests.get(request_url)
        response = flask.jsonify(solr_response.json())
        add_cors_headers(response)
        return response


@ns.route('/get', methods=['GET'])
class GetEndpoint(Resource):

    @api.expect(get_arguments, validate=True)
    def get(self):
        """
        Direct document access.

        Returns a single document specified by the given identifier.

        * identifier (mandatory): Document identifier. Identifier can be 'id' or 'curie' or 'accession_id' of the solr document.

        ```
        ?identifier="http://www.semanticweb.org/brain_data_standards/AllenDendClass_CS202002013_189"
        ?identifier="AllenDendClass:CS202002013_189"
        ?identifier=CS202002013_189
        ```
        """
        if 'identifier' in request.args and request.args['identifier']:
            identifier = str(request.args['identifier']).replace("\"", "").strip()
        else:
            raise BDSApiException("Error: identifier string is empty. Please specify an identifier.")

        if identifier.startswith("http:"):
            search_field = "id"
        elif ":" in identifier:
            search_field = "curie"
        else:
            search_field = "accession_id"

        request_url = "http://{host}:{port}/solr/{collection}/query?q="\
            .format(host=search_config["solr_host"], port=search_config["solr_port"],
                    collection=search_config["solr_collection"])
        request_url += search_field + ":\"" + identifier + "\""

        log.info("Request: " + request_url)
        solr_response = requests.get(request_url)
        response = flask.jsonify(solr_response.json())
        add_cors_headers(response)
        return response


def add_cors_headers(response):
    """
    Adds cross origin request support.
    """
    headers = response.headers
    headers['Access-Control-Allow-Origin'] = '*'


def generate_request(config):
    if 'query' in request.args and request.args['query']:
        query = request.args['query']
    else:
        raise BDSApiException("Error: query string is empty. Please specify a search term.")
    request_url = "http://{host}:{port}/solr/{collection}/query?defType=edismax".format(host=config["solr_host"],
                                                                                       port=config["solr_port"],
                                                                                       collection=config[
                                                                                           "solr_collection"])
    request_url += "&q=(" + create_intersection_string(query) + ")"
    request_url += "&fl=" + ",".join(get_list_value(config, "response_fields"))
    request_url += "&qf=" + " ".join(get_list_value(config, "field_weights")) + " "
    for domain_boosting in get_list_value(config, "domain_boosting"):
        request_url += "&bq=iri:" + escape_solr_arg(domain_boosting)
    request_url += "&hl=true"
    request_url += "&hl.simple.pre=<b>"
    request_url += "&hl.fl=" + ",".join(get_list_value(config, "highlight_fields"))

    if 'species' in request.args and request.args['species']:
        request_url += "&fq=species: (" + " OR ".join(list(parse_species_filter())) + ")"
    if 'rank' in request.args and request.args['rank']:
        request_url += "&fq=rank: (" + " OR ".join(list(parse_rank_filter())) + ")"

    print(request_url)
    return request_url


def parse_rank_filter():
    rank_list = request.args['rank'].split(",")
    rank_decode = set()
    for rank in rank_list:
        if rank.strip().lower() not in (term.lower() for term in ranks):
            raise BDSApiException("Error: unrecognised rank: '" + str(rank) + "'")
        for term in ranks:
            if term.lower() == rank.strip().lower():
                rank_decode.add(term)

    return rank_decode


def parse_species_filter():
    """
    Parses species filter parameters and generates list of NCBITaxon IDs. Species can be specified by their simple
    name or by their NCBITaxon ID. When more than one species are provided, results that meet any of the species (OR the given species) are returned.
    """
    species_list = request.args['species'].split(",")
    species_decode = set()
    for species in species_list:
        species_lower = str(species).strip().lower()
        if species_lower in species_mapping:
            species_decode.add("\"" + species_mapping[species_lower] + "\"")
        elif species.strip() in list(species_mapping.values()):
            species_decode.add("\"" + species.strip() + "\"")
        elif species.strip().replace("\"", "") in list(species_mapping.values()):
            species_decode.add(species.strip())
        else:
            raise BDSApiException("Error: unrecognised species: '" + str(species) + "'")
    return species_decode


def escaped_seq(term):
    """
    Yield the next string based on the next character (either this char or escaped version)
    """
    for char in term:
        if char in solr_escape_rules.keys():
            yield solr_escape_rules[char]
        else:
            yield char


def escape_solr_arg(term):
    """
    Apply escaping to the passed in query terms escaping special characters like : , etc
    """
    term = term.replace('\\', r'\\')  # escape \ first
    return "".join([nextStr for nextStr in escaped_seq(term)])


def create_intersection_string(query):
    tokens = query.split(" ")
    return " AND ".join(tokens)


def get_list_value(config, name):
    """
    Reads list type configuration. By default all configuration values are string, this function parses value to list.
    """
    parsed = ast.literal_eval(config[name])
    return [item.strip() for item in parsed]
