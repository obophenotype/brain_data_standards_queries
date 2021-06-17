import json
from bds_queries import IndividualDetailsQuery, ListAllAllenIndividuals


def individuals_metadata_dump():
    all_metadata = []
    all_individuals = ListAllAllenIndividuals().execute_query()

    for individual in all_individuals:
        individual_details_query = IndividualDetailsQuery()
        result = individual_details_query.execute_query({"accession": individual.replace("AllenDend:", "")})
        result["node"] = individual
        all_metadata.append(result)

    print(len(all_metadata))

    dump_to_file(all_metadata, '../../dumps/individuals_metadata.json')


def dump_to_file(data, path):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    individuals_metadata_dump()
