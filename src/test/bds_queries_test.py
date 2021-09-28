import unittest
import json
from bds_queries import IndividualDetailsQuery, ListAllAllenIndividuals, GetOntologyMetadata


class QueriesTest(unittest.TestCase):

    def test_individual_details_query(self):
        individual_details_query = IndividualDetailsQuery()
        result = individual_details_query.execute_query({"accession": "CS202002013_128"})
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

        self.assertEqual(144, len(result))
        self.assertTrue("AllenDend:CS202002013_128" in result)
        self.assertTrue("AllenDend:CS202002013_188" in result)

    def test_get_ontology_metadata(self):
        result = GetOntologyMetadata().execute_query()

        print(json.dumps(result))

        self.assertEqual(2, len(result))
        self.assertEqual("Brain Data Standards Cell Ontology", result["name"])
        self.assertTrue("version" in result)


if __name__ == '__main__':
    unittest.main()