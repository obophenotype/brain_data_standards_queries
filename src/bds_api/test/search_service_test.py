import unittest
import json
from flask import Flask, Blueprint
from bds_api.restplus import api
from bds_api.app import app
from bds_api.endpoints.search_service import ns as api_namespace
from bds_api.endpoints.search_config import search_config

app = Flask(__name__)

# config should be same with app.py
blueprint = Blueprint('bds', __name__, url_prefix='/bds')
api.init_app(blueprint)
api.add_namespace(api_namespace)
app.register_blueprint(blueprint)


class SearchTest(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()

    def test_basic_search(self):
        response = self.app.get("""/bds/api/search?query=Lamp5%20Lhx6""")
        self.assertEqual(200, response.status_code)

        response_data = json.loads(response.get_data())
        print(response_data)
        results = response_data["response"]["docs"]
        self.assertEqual(4, len(results))
        self.assertEqual(["AllenDendClass:CS202002013_8"], results[0]["curie"])
        self.assertEqual(["Lamp5 Lhx6 MOp (Mouse)"], results[0]["symbol"])
        self.assertEqual(["Mus musculus"], results[0]["species"])

    def test_search_species_filter(self):
        response = self.app.get("""/bds/api/search?query=Lamp5%20Lhx6""")
        self.assertEqual(200, response.status_code)

        results = json.loads(response.get_data())["response"]["docs"]
        self.assertEqual(4, len(results))
        species = set()
        for result in results:
            species.update(result["species"])
        self.assertTrue("Mus musculus" in species)
        self.assertTrue("Homo sapiens" in species)
        self.assertTrue("Callithrix jacchus" in species)
        self.assertTrue("Euarchontoglires" in species)

        response = self.app.get("""/bds/api/search?query=Lamp5%20Lhx6&species=Mouse""")
        results = json.loads(response.get_data())["response"]["docs"]
        self.assertEqual(1, len(results))
        species = set()
        for result in results:
            species.update(result["species"])
        self.assertTrue("Mus musculus" in species)

        response = self.app.get("""/bds/api/search?query=Lamp5%20Lhx6&species=\"Callithrix jacchus\"""")
        results = json.loads(response.get_data())["response"]["docs"]
        self.assertEqual(1, len(results))
        species = set()
        for result in results:
            species.update(result["species"])
        self.assertTrue("Callithrix jacchus" in species)

        response = self.app.get("""/bds/api/search?query=Lamp5%20Lhx6&species=mouse,human""")
        results = json.loads(response.get_data())["response"]["docs"]
        self.assertEqual(2, len(results))
        species = set()
        for result in results:
            species.update(result["species"])
        self.assertTrue("Mus musculus" in species)
        self.assertTrue("Homo sapiens" in species)

    def test_search_species_filter_error(self):
        response = self.app.get("""/bds/api/search?query=Lamp5%20Lhx6&species=mousexx""")
        self.assertEqual(400, response.status_code)
        self.assertEqual("Error: unrecognised species: 'mousexx'", json.loads(response.get_data())["message"])

    def test_search_rank_filter(self):
        response = self.app.get("""/bds/api/search?query=Lamp5%20Lhx6""")
        self.assertEqual(200, response.status_code)

        results = json.loads(response.get_data())["response"]["docs"]
        self.assertEqual(4, len(results))
        curies = set()
        for result in results:
            curies.update(result["curie"])
        self.assertTrue("AllenDendClass:CS202002013_8" in curies)
        self.assertTrue("AllenDendClass:CS201912132_4" in curies)
        self.assertTrue("AllenDendClass:CS202002270_4" in curies)
        self.assertTrue("AllenDendClass:CS201912131_153" in curies)

        response = self.app.get("""/bds/api/search?query=Lamp5%20Lhx6&rank=Cell Type""")
        results = json.loads(response.get_data())["response"]["docs"]
        self.assertEqual(2, len(results))
        curies = set()
        for result in results:
            curies.update(result["curie"])
        self.assertTrue("AllenDendClass:CS202002013_8" in curies)
        self.assertTrue("AllenDendClass:CS201912132_4" in curies)

        response = self.app.get("""/bds/api/search?query=Lamp5%20Lhx6&rank=cell type""")
        results = json.loads(response.get_data())["response"]["docs"]
        self.assertEqual(2, len(results))
        curies = set()
        for result in results:
            curies.update(result["curie"])
        self.assertTrue("AllenDendClass:CS202002013_8" in curies)
        self.assertTrue("AllenDendClass:CS201912132_4" in curies)

        response = self.app.get("""/bds/api/search?query=Lamp5%20Lhx6&rank=Cell Type, None""")
        results = json.loads(response.get_data())["response"]["docs"]
        self.assertEqual(4, len(results))
        curies = set()
        for result in results:
            curies.update(result["curie"])
        self.assertTrue("AllenDendClass:CS202002013_8" in curies)
        self.assertTrue("AllenDendClass:CS201912132_4" in curies)
        self.assertTrue("AllenDendClass:CS202002270_4" in curies)
        self.assertTrue("AllenDendClass:CS201912131_153" in curies)

        response = self.app.get("""/bds/api/search?query=Lamp5%20Lhx6&rank=Class""")
        results = json.loads(response.get_data())["response"]["docs"]
        self.assertEqual(0, len(results))

    def test_search_multiple_filters(self):
        response = self.app.get("""/bds/api/search?query=Lamp5%20Lhx6""")
        self.assertEqual(200, response.status_code)

        results = json.loads(response.get_data())["response"]["docs"]
        self.assertEqual(4, len(results))
        curies = set()
        for result in results:
            curies.update(result["curie"])
        self.assertTrue("AllenDendClass:CS202002013_8" in curies)
        self.assertTrue("AllenDendClass:CS201912132_4" in curies)
        self.assertTrue("AllenDendClass:CS202002270_4" in curies)
        self.assertTrue("AllenDendClass:CS201912131_153" in curies)

        response = self.app.get("""/bds/api/search?query=Lamp5%20Lhx6&rank=cell type""")
        results = json.loads(response.get_data())["response"]["docs"]
        self.assertEqual(2, len(results))
        curies = set()
        for result in results:
            curies.update(result["curie"])
        self.assertTrue("AllenDendClass:CS202002013_8" in curies)
        self.assertTrue("AllenDendClass:CS201912132_4" in curies)

        response = self.app.get("""/bds/api/search?query=Lamp5%20Lhx6&rank=cell type&species=mouse,human""")
        results = json.loads(response.get_data())["response"]["docs"]
        self.assertEqual(1, len(results))
        curies = set()
        for result in results:
            curies.update(result["curie"])
        self.assertTrue("AllenDendClass:CS202002013_8" in curies)

        response = self.app.get("""/bds/api/search?query=Lamp5%20Lhx6&rank=cell type&species=mouse,marmoset""")
        results = json.loads(response.get_data())["response"]["docs"]
        self.assertEqual(2, len(results))
        curies = set()
        for result in results:
            curies.update(result["curie"])
        self.assertTrue("AllenDendClass:CS202002013_8" in curies)
        self.assertTrue("AllenDendClass:CS201912132_4" in curies)

    def test_search_rank_filter_error(self):
        response = self.app.get("""/bds/api/search?query=Lamp5%20Lhx6&rank=Not Exists""")
        self.assertEqual(400, response.status_code)
        self.assertEqual("Error: unrecognised rank: 'Not Exists'", json.loads(response.get_data())["message"])

    def test_config_lists(self):
        self.assertEqual("ec2-3-143-113-50.us-east-2.compute.amazonaws.com", search_config["solr_host"])
        self.assertEqual("bdsdump", search_config["solr_collection"])
        self.assertEqual("[\"*\", \"score\"]", search_config["response_fields"])


class TaxonomiesTest(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()

    def test_list_taxonomies(self):
        response = self.app.get("""/bds/api/taxonomies""")
        self.assertEqual(200, response.status_code)

        response_data = json.loads(response.get_data())
        print(response_data)
        results = response_data["response"]["docs"]
        self.assertEqual(4, len(results))
        self.assertEqual(["AllenDend:CCN202002013"], results[0]["curie"])
        self.assertEqual(["CCN202002013"], results[0]["accession_id"])
        self.assertEqual([116], results[0]["cell_types_count"])


class GetServiceTest(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()

    def test_get_by_id(self):
        response = self.app.get("""/bds/api/get?identifier=\"http://www.semanticweb.org/brain_data_standards/AllenDendClass_CS202002013_189\"""")
        self.assertEqual(200, response.status_code)

        response_data = json.loads(response.get_data())
        print(response_data)
        results = response_data["response"]["docs"]
        self.assertEqual(1, len(results))
        self.assertEqual(["AllenDendClass:CS202002013_189"], results[0]["curie"])

    def test_get_by_curie(self):
        response = self.app.get("""/bds/api/get?identifier=\"AllenDendClass:CS202002013_189\"""")
        self.assertEqual(200, response.status_code)

        response_data = json.loads(response.get_data())
        print(response_data)
        results = response_data["response"]["docs"]
        self.assertEqual(1, len(results))
        self.assertEqual(["AllenDendClass:CS202002013_189"], results[0]["curie"])

    def test_get_by_accession_id(self):
        response = self.app.get("""/bds/api/get?identifier=CS202002013_189""")
        self.assertEqual(200, response.status_code)

        response_data = json.loads(response.get_data())
        print(response_data)
        results = response_data["response"]["docs"]
        self.assertEqual(1, len(results))
        self.assertEqual(["AllenDendClass:CS202002013_189"], results[0]["curie"])



if __name__ == '__main__':
    unittest.main()
