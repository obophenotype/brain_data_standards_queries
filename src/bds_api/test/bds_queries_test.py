import unittest
import json
from bds_api.dumps.bds_queries import IndividualDetailsQuery, ListAllAllenIndividuals, GetOntologyMetadata, ListAllTaxonomies


class QueriesTest(unittest.TestCase):

    def test_individual_details_query(self):
        individual_details_query = IndividualDetailsQuery()
        result = individual_details_query.execute_query({"accession": "0011528"})
        print(json.dumps(result))

        self.assertTrue(result["class_metadata"])
        self.assertTrue(result["parents"])
        self.assertEqual(1, len(result["parents"]))
        self.assertTrue(result["markers"])
        self.assertEqual(2, len(result["markers"]))
        self.assertTrue(result["references"])
        self.assertEqual(2, len(result["references"]))

    def test_list_all_indv_query(self):
        result = ListAllAllenIndividuals().execute_query()
        print(json.dumps(result))

        self.assertTrue(len(result) >= 515)
        self.assertTrue("PCL:0011528" in result)
        self.assertTrue("PCL:0011588" in result)

    def test_list_all_taxonomies_query(self):
        result = ListAllTaxonomies().execute_query()
        print(result)

        self.assertEqual(4, len(result))
        self.assertTrue('CCN202002013' in result)
        self.assertEqual(["UBERON:0001384"], result['CCN202002013']["has_brain_region"])

        for key in result['CCN202002013']:
            print(key + " : " + str(result['CCN202002013'][key]))

        self.assertTrue('CCN201912131' in result)
        self.assertTrue('CCN201912132' in result)
        self.assertTrue('CS1908210' in result)

    def test_get_ontology_metadata(self):
        result = GetOntologyMetadata().execute_query()

        print(json.dumps(result))

        self.assertEqual(2, len(result))
        self.assertEqual("Brain Data Standards Cell Ontology", result["name"])
        self.assertTrue("version" in result)


if __name__ == '__main__':
    unittest.main()
