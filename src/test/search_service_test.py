import unittest
import json
from search.search_service import app
from search.search_config import search_config


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
        self.assertEqual(["http://purl.obolibrary.org/obo/NCBITaxon_10090"], results[0]["species"])

    def test_search_species_filter(self):
        response = self.app.get("""/bds/api/search?query=Lamp5%20Lhx6""")
        self.assertEqual(200, response.status_code)

        results = json.loads(response.get_data())["response"]["docs"]
        self.assertEqual(4, len(results))
        species = set()
        for result in results:
            species.update(result["species"])
        self.assertTrue("http://purl.obolibrary.org/obo/NCBITaxon_10090" in species)
        self.assertTrue("http://purl.obolibrary.org/obo/NCBITaxon_9483" in species)
        self.assertTrue("http://purl.obolibrary.org/obo/NCBITaxon_314146" in species)
        self.assertTrue("http://purl.obolibrary.org/obo/NCBITaxon_9606" in species)

        response = self.app.get("""/bds/api/search?query=Lamp5%20Lhx6&species=Mouse""")
        results = json.loads(response.get_data())["response"]["docs"]
        self.assertEqual(1, len(results))
        species = set()
        for result in results:
            species.update(result["species"])
        self.assertTrue("http://purl.obolibrary.org/obo/NCBITaxon_10090" in species)

        response = self.app.get("""/bds/api/search?query=Lamp5%20Lhx6&species=\"http://purl.obolibrary.org/obo/NCBITaxon_9483\"""")
        results = json.loads(response.get_data())["response"]["docs"]
        self.assertEqual(1, len(results))
        species = set()
        for result in results:
            species.update(result["species"])
        self.assertTrue("http://purl.obolibrary.org/obo/NCBITaxon_9483" in species)

        response = self.app.get("""/bds/api/search?query=Lamp5%20Lhx6&species=mouse,human""")
        results = json.loads(response.get_data())["response"]["docs"]
        self.assertEqual(2, len(results))
        species = set()
        for result in results:
            species.update(result["species"])
        self.assertTrue("http://purl.obolibrary.org/obo/NCBITaxon_10090" in species)
        self.assertTrue("http://purl.obolibrary.org/obo/NCBITaxon_9606" in species)

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


if __name__ == '__main__':
    unittest.main()
