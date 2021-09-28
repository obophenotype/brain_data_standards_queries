import unittest
import ast
from search.search_config import search_config


class SearchTest(unittest.TestCase):

    def test_config_lists(self):
        # value = search_config["search_field_weights"]
        # parsed = ast.literal_eval(value)
        # print(parsed)
        # print(type(parsed))
        value = search_config["autocomplete_response_fields"]
        parsed = ast.literal_eval(value)
        result = [item.strip() for item in parsed]
        print(result)
        print(type(result))
