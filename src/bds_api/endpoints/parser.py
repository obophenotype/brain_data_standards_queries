from flask_restplus import reqparse

search_arguments = reqparse.RequestParser()
search_arguments.add_argument('query', type=str, action="append", required=True)
search_arguments.add_argument('species', type=str, required=False)
search_arguments.add_argument('taxonomy', type=str, required=False)
search_arguments.add_argument('rank', type=str, required=False)
search_arguments.add_argument('limit', type=int, required=False)

get_arguments = reqparse.RequestParser()
get_arguments.add_argument('identifier', type=str, action="append", required=True)
