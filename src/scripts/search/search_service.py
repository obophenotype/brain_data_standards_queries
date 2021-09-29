import flask
import requests
import ast
from flask import request
from search_config import search_config, autocomplete_config
from api_exception import QueryTermException

app = flask.Flask(__name__)
app.config["DEBUG"] = True

solr_escape_rules = {'+':r'\+','-':r'\-','&':r'\&','|':r'\|','!':r'\!','(':r'\(',')':r'\)','{':r'\{','}':r'\}',
                     '[':r'\[',']':r'\]','~':r'\~','*':r'\*','?':r'\?',':':r'\:','"':r'\"',';':r'\;','/':r'\/'}


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
    return request_url


def escaped_seq(term):
    """
    Yield the next string based on the next character (either this char or escaped version
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


app.run(host="0.0.0.0", port="8080")
