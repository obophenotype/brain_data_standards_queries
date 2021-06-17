import unittest
import json
from bds_queries import IndividualDetailsQuery, ListAllAllenIndividuals


class TemplateUtilsTest(unittest.TestCase):

    def test_individual_details_query(self):
        individual_details_query = IndividualDetailsQuery()
        result = individual_details_query.execute_query({"accession": "CS202002013_128"})
        print(json.dumps(result))

        self.assertTrue(result["class_metadata"])
        self.assertTrue(result["parents"])
        self.assertEqual(2, len(result["parents"]))
        self.assertTrue(result["markers"])
        self.assertEqual(2, len(result["markers"]))

    def test_list_all_indv_query(self):
        result = ListAllAllenIndividuals().execute_query()
        print(json.dumps(result))

        self.assertEqual(134, len(result))
        self.assertTrue("AllenDend:CS202002013_128" in result)
        self.assertTrue("AllenDend:CS202002013_188" in result)


if __name__ == '__main__':
    unittest.main()