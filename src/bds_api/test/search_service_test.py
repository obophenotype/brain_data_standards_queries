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
        self.assertTrue(len(results) >= 3)
        self.assertEqual(["PCL:0011008"], results[0]["curie"])
        self.assertEqual(["Lamp5 Lhx6 MOp (Mouse)"], results[0]["symbol"])
        self.assertEqual(["Mus musculus"], results[0]["species"])

    def test_search_species_filter(self):
        response = self.app.get("""/bds/api/search?query=Lamp5%20Lhx6""")
        self.assertEqual(200, response.status_code)

        results = json.loads(response.get_data())["response"]["docs"]
        self.assertTrue(len(results) >= 3)
        species = set()
        for result in results:
            species.update(result["species"])
        self.assertTrue("Mus musculus" in species)
        self.assertTrue("Homo sapiens" in species)
        self.assertTrue("Callithrix jacchus" in species)

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
        self.assertTrue(len(results) >= 3)
        curies = set()
        for result in results:
            curies.update(result["curie"])
        self.assertTrue("PCL:0011008" in curies)
        self.assertTrue("PCL:0019004" in curies)
        self.assertTrue("PCL:0015153" in curies)

        response = self.app.get("""/bds/api/search?query=Lamp5%20Lhx6&rank=Cell Type""")
        results = json.loads(response.get_data())["response"]["docs"]
        self.assertTrue(len(results) >= 2)
        curies = set()
        for result in results:
            curies.update(result["curie"])
        self.assertTrue("PCL:0011008" in curies)
        self.assertTrue("PCL:0019004" in curies)

        response = self.app.get("""/bds/api/search?query=Lamp5%20Lhx6&rank=cell type""")
        results = json.loads(response.get_data())["response"]["docs"]
        self.assertTrue(len(results) >= 2)
        curies = set()
        for result in results:
            curies.update(result["curie"])
        self.assertTrue("PCL:0011008" in curies)
        self.assertTrue("PCL:0019004" in curies)

        response = self.app.get("""/bds/api/search?query=Lamp5%20Lhx6&rank=Cell Type, None""")
        results = json.loads(response.get_data())["response"]["docs"]
        self.assertTrue(len(results) >= 3)
        curies = set()
        for result in results:
            curies.update(result["curie"])
        self.assertTrue("PCL:0011008" in curies)
        self.assertTrue("PCL:0019004" in curies)
        self.assertTrue("PCL:0015153" in curies)

        response = self.app.get("""/bds/api/search?query=Lamp5%20Lhx6&rank=Class""")
        results = json.loads(response.get_data())["response"]["docs"]
        self.assertEqual(0, len(results))

    def test_search_taxonomy_filter(self):
        response = self.app.get("""/bds/api/search?query=*""")
        self.assertEqual(200, response.status_code)

        results = json.loads(response.get_data())["response"]["docs"]
        self.assertTrue(len(results) >= 300)

        response = self.app.get("""/bds/api/search?query=*&taxonomy=CCN202002013""")
        results = json.loads(response.get_data())["response"]["docs"]
        self.assertEqual(257, len(results))
        curies = set()
        for result in results:
            curies.update(result["individual"])
        self.assertTrue("PCL:0011501" in curies)
        self.assertTrue("PCL:0011757" in curies)

        response = self.app.get("""/bds/api/search?query=*&taxonomy=CCN202002013&rank=Class""")
        results = json.loads(response.get_data())["response"]["docs"]
        self.assertEqual(4, len(results))
        curies = set()
        for result in results:
            curies.update(result["individual"])
        self.assertTrue("PCL:0011623" in curies)
        self.assertTrue("PCL:0011679" in curies)
        self.assertTrue("PCL:0011719" in curies)
        self.assertTrue("PCL:0011735" in curies)

        response = self.app.get("""/bds/api/search?query=*&taxonomy=(CCN202002013 OR CCN201912131)&rank=Class""")
        results = json.loads(response.get_data())["response"]["docs"]
        self.assertEqual(8, len(results))
        curies = set()
        for result in results:
            curies.update(result["individual"])
        self.assertTrue("PCL:0011623" in curies)
        self.assertTrue("PCL:0011679" in curies)
        self.assertTrue("PCL:0011719" in curies)
        self.assertTrue("PCL:0011735" in curies)
        self.assertTrue("PCL:0015648" in curies)
        self.assertTrue("PCL:0015649" in curies)
        self.assertTrue("PCL:0015650" in curies)
        self.assertTrue("PCL:0015651" in curies)

    def test_search_multiple_filters(self):
        response = self.app.get("""/bds/api/search?query=Lamp5%20Lhx6""")
        self.assertEqual(200, response.status_code)

        results = json.loads(response.get_data())["response"]["docs"]
        self.assertTrue(len(results) >= 3)
        curies = set()
        for result in results:
            curies.update(result["curie"])
        self.assertTrue("PCL:0011008" in curies)
        self.assertTrue("PCL:0019004" in curies)
        self.assertTrue("PCL:0015153" in curies)

        response = self.app.get("""/bds/api/search?query=Lamp5%20Lhx6&rank=cell type""")
        results = json.loads(response.get_data())["response"]["docs"]
        self.assertEqual(2, len(results))
        curies = set()
        for result in results:
            curies.update(result["curie"])
        self.assertTrue("PCL:0011008" in curies)
        self.assertTrue("PCL:0019004" in curies)

        response = self.app.get("""/bds/api/search?query=Lamp5%20Lhx6&rank=cell type&species=mouse,human""")
        results = json.loads(response.get_data())["response"]["docs"]
        self.assertEqual(1, len(results))
        curies = set()
        for result in results:
            curies.update(result["curie"])
        self.assertTrue("PCL:0011008" in curies)

        response = self.app.get("""/bds/api/search?query=Lamp5%20Lhx6&rank=cell type&species=mouse,marmoset""")
        results = json.loads(response.get_data())["response"]["docs"]
        self.assertEqual(2, len(results))
        curies = set()
        for result in results:
            curies.update(result["curie"])
        self.assertTrue("PCL:0011008" in curies)
        self.assertTrue("PCL:0019004" in curies)

    def test_search_rank_filter_error(self):
        response = self.app.get("""/bds/api/search?query=Lamp5%20Lhx6&rank=Not Exists""")
        self.assertEqual(400, response.status_code)
        self.assertEqual("Error: unrecognised rank: 'Not Exists'", json.loads(response.get_data())["message"])

    def test_config_lists(self):
        self.assertEqual("ec2-3-143-113-50.us-east-2.compute.amazonaws.com", search_config["solr_host"])
        self.assertEqual("bdsdump", search_config["solr_collection"])
        self.assertEqual("[\"*\", \"score\"]", search_config["response_fields"])

    def test_search_limit(self):
        response = self.app.get("""/bds/api/search?query=*""")
        self.assertEqual(200, response.status_code)
        results = json.loads(response.get_data())["response"]["docs"]
        self.assertTrue(len(results) >= 100)

        response = self.app.get("""/bds/api/search?query=*&limit=4""")
        self.assertEqual(200, response.status_code)
        results = json.loads(response.get_data())["response"]["docs"]
        self.assertEqual(4, len(results))


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

        curies = list()
        for result in results:
            curies.append(result["curie"][0])
        self.assertTrue("PCL:0011000" in curies)

        mouse_taxon = results[curies.index("PCL:0011000")]
        self.assertEqual(["CCN202002013"], mouse_taxon["accession_id"])
        self.assertEqual([116], mouse_taxon["cell_types_count"])


class GetServiceTest(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()

    def test_get_by_id(self):
        response = self.app.get("""/bds/api/get?identifier=\"http://purl.obolibrary.org/obo/PCL_0011189\"""")
        self.assertEqual(200, response.status_code)

        response_data = json.loads(response.get_data())
        print(response_data)
        results = response_data["response"]["docs"]
        self.assertEqual(1, len(results))
        self.assertEqual(["PCL:0011189"], results[0]["curie"])

    def test_get_by_curie(self):
        response = self.app.get("""/bds/api/get?identifier=\"PCL:0011189\"""")
        self.assertEqual(200, response.status_code)

        response_data = json.loads(response.get_data())
        print(response_data)
        results = response_data["response"]["docs"]
        self.assertEqual(1, len(results))
        self.assertEqual(["PCL:0011189"], results[0]["curie"])

    def test_get_by_accession_id(self):
        response = self.app.get("""/bds/api/get?identifier=CS202002013_189""")
        self.assertEqual(200, response.status_code)

        response_data = json.loads(response.get_data())
        print(response_data)
        results = response_data["response"]["docs"]
        self.assertEqual(1, len(results))
        self.assertEqual(["PCL:0011189"], results[0]["curie"])


if __name__ == '__main__':
    unittest.main()
