import unittest
import json
from bds_api.dumps.bds_queries import IndividualDetailsQuery, ListAllAllenIndividuals, GetOntologyMetadata, ListAllTaxonomies


class QueriesTest(unittest.TestCase):

    def test_individual_details_query(self):
        individual_details_query = IndividualDetailsQuery()
        result = individual_details_query.execute_query({"accession": "0011628"})
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

        self.assertEqual(4, len(result))
        self.assertTrue('202002013' in result)
        self.assertEqual(["UBERON:0001384"], result['202002013']["taxonomy"]["has_brain_region"])

        for key in result['202002013']["taxonomy"]:
            print(key + " : " + str(result['202002013']["taxonomy"][key]))

        self.assertTrue('cell_classes_count' in result['202002013']["taxonomy"])
        self.assertTrue(result['202002013']["taxonomy"]['cell_classes_count'])

        self.assertTrue('201912131' in result)
        self.assertTrue('201912132' in result)
        self.assertTrue('1908210' in result)

        datasets = result['202002013']["datasets"]
        self.assertEqual(11, len(datasets))

        first_mouse_dataset = result['202002013']["datasets"][0]["dataset_metadata"]
        self.assertTrue('comment' in first_mouse_dataset)
        self.assertTrue(first_mouse_dataset['comment'])

    def test_get_ontology_metadata(self):
        result = GetOntologyMetadata().execute_query()

        print(json.dumps(result))

        self.assertEqual(2, len(result))
        self.assertEqual("Brain Data Standards Cell Ontology", result["name"])
        self.assertTrue("version" in result)


if __name__ == '__main__':
    unittest.main()
