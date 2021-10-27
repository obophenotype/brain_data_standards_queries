import flask
import requests
import ast
import logging
from flask import request
from search.search_config import search_config, autocomplete_config
from search.api_exception import QueryTermException

app = flask.Flask(__name__)
app.config["DEBUG"] = True

log = logging.getLogger(__name__)

solr_escape_rules = {'+':r'\+','-':r'\-','&':r'\&','|':r'\|','!':r'\!','(':r'\(',')':r'\)','{':r'\{','}':r'\}',
                     '[':r'\[',']':r'\]','~':r'\~','*':r'\*','?':r'\?',':':r'\:','"':r'\"',';':r'\;','/':r'\/'}

species_mapping = {"mouse": "Mus musculus",
                   "human": "Homo sapiens",
                   "marmoset": "Callithrix jacchus",
                   "euarchontoglires": "Euarchontoglires"}
ranks = ["Cell Type", "Subclass", "Class", "None"]


@app.route('/bds/api/search', methods=['GET'])
def search():
    request_url = generate_request(search_config)
    print(request_url)
    solr_response = requests.get(request_url)
    response = flask.jsonify(solr_response.json())
    # handle CORS
    headers = response.headers
    headers['Access-Control-Allow-Origin'] = '*'
    return response


@app.route('/bds/api/autocomplete', methods=['GET'])
def autocomplete():
    request_url = generate_request(autocomplete_config)
    print(request_url)
    solr_response = requests.get(request_url)
    response = flask.jsonify(solr_response.json())
    # handle CORS
    headers = response.headers
    headers['Access-Control-Allow-Origin'] = '*'
    return response


@app.errorhandler(QueryTermException)
def handle_bad_request(error):
    log.exception(error.message)
    return {'message': error.message}, error.status_code


def generate_request(config):
    if 'query' in request.args and request.args['query']:
        query = request.args['query']
    else:
        raise QueryTermException("Error: query string is empty. Please specify a search term.")
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
            raise QueryTermException("Error: unrecognised rank: '" + str(rank) + "'")
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
            raise QueryTermException("Error: unrecognised species: '" + str(species) + "'")
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


def main():
    app.run(host="0.0.0.0", port="8080")


if __name__ == '__main__':
    main()
