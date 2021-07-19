import json
import requests
from bds_queries import IndividualDetailsQuery, ListAllAllenIndividuals

SOLR_JSON_PATH = '../../dumps/individuals_metadata_solr.json'


def individuals_metadata_dump():
    all_metadata = []
    all_individuals = ListAllAllenIndividuals().execute_query()

    for individual in all_individuals:
        result = IndividualDetailsQuery().execute_query({"accession": individual.replace("AllenDend:", "")})
        result["node"] = individual
        all_metadata.append(result)

    print(len(all_metadata))

    dump_to_file(all_metadata, '../../dumps/individuals_metadata.json')


def individuals_metadata_solr_dump():
    """
    Solr is only supporting flat json objects. So unpacking nested objets to a flat representation.
    :return: Solr index representation of the BDS individuals.
    """
    all_data = dict()
    all_individuals = ListAllAllenIndividuals().execute_query()

    count = 0
    for individual in all_individuals:
        result = IndividualDetailsQuery().execute_query({"accession": individual.replace("AllenDend:", "")})

        solr_doc = extract_class_metadata(result["class_metadata"])
        solr_doc["individual"] = individual

        extract_parent_data(all_data, result, solr_doc)
        extract_marker_data(all_data, result, solr_doc)

        all_data[solr_doc["iri"]] = solr_doc
        count += 1

    print("Found Allen individual count is: " + str(count))

    dump_map_to_file(all_data, SOLR_JSON_PATH)


def extract_parent_data(all_data, result, solr_doc):
    parents = list()
    parent_labels = list()
    for parent in result["parents"]:
        parent_iri = parent["class_metadata"]["iri"]
        if parent_iri not in parents:
            parents.append(parent_iri)
            parent_labels.append(parent["class_metadata"]["label"])
        if parent_iri not in all_data:
            all_data[parent_iri] = extract_class_metadata(parent["class_metadata"])
    solr_doc["parents"] = parents
    solr_doc["parent_labels"] = parent_labels


def extract_marker_data(all_data, result, solr_doc):
    markers = list()
    marker_labels = list()
    relations = dict()
    for marker in result["markers"]:
        if marker["class_metadata"] is not None:
            marker_iri = marker["class_metadata"]["iri"]
            if marker_iri not in markers:
                markers.append(marker_iri)
                marker_labels.append(marker["class_metadata"]["label"])
            if marker_iri not in all_data:
                all_data[marker_iri] = extract_class_metadata(marker["class_metadata"])
            relation = marker["relation"]
            if relation["label"] not in relations.keys():
                relations[relation["label"]] = {marker_iri}
            else:
                relations[relation["label"]].add(marker_iri)

    for relation_type in relations:
        solr_doc[relation_type] = list(relations[relation_type])
    solr_doc["markers"] = markers
    solr_doc["marker_labels"] = marker_labels


def extract_class_metadata(node_meta_data):
    print("Processing: " + node_meta_data["iri"])
    solr_doc = dict()
    solr_doc["id"] = node_meta_data["iri"]
    solr_doc["iri"] = node_meta_data["iri"]
    solr_doc["curie"] = node_meta_data["curie"]
    solr_doc["label"] = node_meta_data["label"]
    if "short_form" in node_meta_data:
        solr_doc["short_form"] = node_meta_data["short_form"]
    if "comment" in node_meta_data:
        solr_doc["comment"] = node_meta_data["comment"]
    if "tags" in node_meta_data:
        solr_doc["tags"] = node_meta_data["tags"]
    if "prefLabel" in node_meta_data:
        solr_doc["prefLabel"] = node_meta_data["prefLabel"]
    if "label_rdfs" in node_meta_data:
        solr_doc["label_rdfs"] = node_meta_data["label_rdfs"]
    if "has_exact_synonym" in node_meta_data:
        exact_synonyms = list()
        for synonym in node_meta_data["has_exact_synonym"]:
            exact_synonyms.append(str(synonym).split("\"value\":\"")[1].replace("\"}", ""))
        solr_doc["has_exact_synonym"] = exact_synonyms
    if "hasOBONamespace" in node_meta_data:
        solr_doc["hasOBONamespace"] = node_meta_data["hasOBONamespace"]
    if "definition" in node_meta_data:
        solr_doc["definition"] = str(node_meta_data["definition"][0]).split("\"value\":\"")[1].replace("\"}", "")
    return solr_doc


def dump_to_file(data, path):
    print("Writing data to file. Object count is : " + str(len(data)))
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def dump_map_to_file(map_data, path):
    print("Writing data to file. Object count is : " + str(len(map_data.values())))
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(list(map_data.values()), f, ensure_ascii=False, indent=4)


def update_solr():
    url = "http://ec2-3-143-113-50.us-east-2.compute.amazonaws.com:8993/solr/bdsdump/update"
    # url = "http://localhost:8993/solr/bdsdump/update"
    headers = {"Content-type": "application/json"}
    params = {"commit": "true"}
    payload = open(SOLR_JSON_PATH, "rb").read()
    r = requests.post(url, data=payload, params=params, headers=headers)
    print("got back: %s" % r.text)


if __name__ == "__main__":
    individuals_metadata_solr_dump()
    # update_solr()
