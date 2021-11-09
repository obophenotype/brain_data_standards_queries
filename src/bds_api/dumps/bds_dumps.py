import json
import requests
from datetime import datetime
from bds_queries import IndividualDetailsQuery, ListAllAllenIndividuals, GetOntologyMetadata, ListAllTaxonomies

CROSS_SPECIES = "Euarchontoglires"

today = datetime.today().strftime('%Y%m%d')

DUMP_PATH = '../../../dumps/individuals_metadata_{}.json'.format(today)

SOLR_JSON_PATH = '../../../dumps/individuals_metadata_solr_{}.json'.format(today)


def individuals_metadata_dump():
    all_metadata = []
    all_individuals = ListAllAllenIndividuals().execute_query()

    for individual in all_individuals:
        result = IndividualDetailsQuery().execute_query({"accession": individual.replace("AllenDend:", "")})
        result["node"] = individual
        all_metadata.append(result)

    print(len(all_metadata))

    ont_metadata = GetOntologyMetadata().execute_query()

    result = dict()
    result["ontology"] = ont_metadata
    result["entities"] = all_metadata

    dump_to_file(result, DUMP_PATH)


def individuals_metadata_solr_dump():
    """
    Solr is only supporting flat json objects. So unpacking nested objets to a flat representation.
    :return: Solr index representation of the BDS individuals.
    """
    all_data = dict()
    all_individuals = ListAllAllenIndividuals().execute_query()
    all_datasets = ListAllTaxonomies().execute_query()

    extract_dataset_metadata(all_data, all_datasets)

    count = 0
    for individual in all_individuals:
        print("Processing individual: " + individual)
        result = IndividualDetailsQuery().execute_query({"accession": individual.replace("AllenDend:", "")})

        solr_doc = extract_class_metadata(result["class_metadata"][0]["class_metadata"])
        if solr_doc:
            solr_doc["tags"] = result["class_metadata"][0]["tags"]
        else:
            # some individuals don't have class, extract from individual itself
            solr_doc = extract_class_metadata(result["indv_metadata"])

        extract_individual_data(all_data, result, solr_doc)
        extract_parent_data(all_data, result, solr_doc)
        extract_marker_data(all_data, result, solr_doc)
        extract_reference_data(all_data, result, solr_doc)
        extract_taxonomy_data(all_data, result, solr_doc)
        extract_brain_region_data(all_data, result, solr_doc, all_datasets)
        solr_doc["individual"] = individual

        all_data[solr_doc["iri"]] = solr_doc
        count += 1

    print("Found Allen individual count is: " + str(count))

    all_data["ontology"] = get_version_metadata(all_data)

    dump_map_to_file(all_data, SOLR_JSON_PATH)


def extract_individual_data(all_data, result, solr_doc):
    indv_metadata = result["indv_metadata"]

    if "comment" in indv_metadata:
        solr_doc["comment_allen"] = indv_metadata["comment"]

    if "cell_type_rank" in indv_metadata:
        solr_doc["rank"] = indv_metadata["cell_type_rank"]

    if "has_exact_synonym" in indv_metadata:
        exact_synonyms = solr_doc["has_exact_synonym"]
        for synonym in indv_metadata["has_exact_synonym"]:
            synonym = str(synonym).split("\"value\":\"")[1].replace("\"}", "")
            if synonym not in exact_synonyms:
                exact_synonyms.append(synonym)
        solr_doc["has_exact_synonym"] = exact_synonyms


def extract_parent_data(all_data, result, solr_doc):
    parents = list()
    parent_labels = list()
    for parent in result["parents"]:
        if parent["class_metadata"] is not None:
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


def extract_reference_data(all_data, result, solr_doc):
    references = list()
    for reference in result["references"]:
        if reference["class_metadata"] is not None:
            reference_iri = reference["class_metadata"]["iri"]
            if reference_iri not in references:
                references.append(reference_iri)
            if reference_iri not in all_data:
                all_data[reference_iri] = extract_reference_class_metadata(reference["class_metadata"])
    solr_doc["references"] = references


def extract_taxonomy_data(all_data, result, solr_doc):
    base_taxonomy = ""
    parent_taxonomies = set()
    for taxon in result["taxonomy"]:
        if "taxon" in taxon and taxon["taxon"]:
            base_taxonomy = taxon["taxon"]["label"]
        elif "parent_taxon" in taxon and taxon["parent_taxon"]:
            parent_taxonomies.add(taxon["parent_taxon"]["label"])

    if base_taxonomy:
        solr_doc["species"] = base_taxonomy
    elif len(parent_taxonomies) == 1 and CROSS_SPECIES in next(iter(parent_taxonomies)):
        solr_doc["species"] = next(iter(parent_taxonomies))
    else:
        for parent_taxon in list(parent_taxonomies):
            if CROSS_SPECIES not in parent_taxon:
                solr_doc["species"] = parent_taxon
                break


def extract_brain_region_data(all_data, result, solr_doc, all_datasets):
    indv_curie = solr_doc["curie"]
    taxonomy_name = indv_curie.replace("AllenDendClass:CS", "CCN").split("_")[0]

    brain_regions = dict()
    for region in result["region"]:
        if "soma_location" in region and region["soma_location"]:
            brain_regions[region["soma_location"]["curie"]] = region["soma_location"]["label"]
        if "parent_soma_location" in region and region["parent_soma_location"]:
            brain_regions[region["parent_soma_location"]["curie"]] = region["parent_soma_location"]["label"]

    if taxonomy_name in all_datasets:
        taxon = all_datasets[taxonomy_name]
        # if "prefLabel" in taxon:
        #     solr_doc["species"] = next(filter(None, taxon["prefLabel"]))
        if brain_regions and "has_brain_region" in taxon:
            brain_regions_set = set()
            for taxon_region in taxon["has_brain_region"]:
                brain_regions_set.add(brain_regions[taxon_region])
            solr_doc["anatomic_region"] = list(brain_regions_set)


def extract_class_metadata(node_meta_data):
    if node_meta_data is not None:
        print("Processing: " + node_meta_data["iri"])
        solr_doc = dict()
        solr_doc["id"] = node_meta_data["iri"]
        solr_doc["iri"] = node_meta_data["iri"]
        solr_doc["curie"] = node_meta_data["curie"]
        if ":" in node_meta_data["curie"]:
            solr_doc["accession_id"] = str(node_meta_data["curie"]).split(":")[1].strip()

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
        if "versionInfo" in node_meta_data:
            solr_doc["versionInfo"] = node_meta_data["versionInfo"]
        if "symbol" in node_meta_data:
            solr_doc["symbol"] = next(filter(None, node_meta_data["symbol"]))
    else:
        solr_doc = None
    return solr_doc


def extract_reference_class_metadata(node_meta_data):
    print("Processing: " + node_meta_data["iri"])
    solr_doc = dict()
    solr_doc["id"] = node_meta_data["iri"]
    solr_doc["iri"] = node_meta_data["iri"]
    solr_doc["curie"] = node_meta_data["curie"]
    solr_doc["label"] = node_meta_data["label"]
    if "creator" in node_meta_data:
        solr_doc["creator"] = node_meta_data["creator"]
    if "exactMatch" in node_meta_data:
        solr_doc["exactMatch"] = next(filter(None, node_meta_data["exactMatch"]))
    if "description" in node_meta_data:
        solr_doc["description"] = node_meta_data["description"]
    if "abstract" in node_meta_data:
        solr_doc["abstract"] = next(filter(None, node_meta_data["abstract"]))
    if "label_rdfs" in node_meta_data:
        solr_doc["label_rdfs"] = node_meta_data["label_rdfs"]
    if "bibliographicCitation" in node_meta_data:
        solr_doc["bibliographicCitation"] = next(filter(None, node_meta_data["bibliographicCitation"]))
    if "identifier" in node_meta_data:
        solr_doc["identifier"] = node_meta_data["identifier"]
    if "date" in node_meta_data:
        solr_doc["date"] = next(filter(None, node_meta_data["date"]))
    return solr_doc


def extract_dataset_metadata(all_data, all_taxonomies):
    for taxonomy in all_taxonomies:
        taxon = all_taxonomies[taxonomy]
        print("Processing taxonomy: " + taxon["iri"])
        solr_doc = dict()
        solr_doc["id"] = taxon["iri"]
        solr_doc["iri"] = taxon["iri"]
        solr_doc["curie"] = taxon["curie"]
        solr_doc["accession_id"] = taxon["label"]
        solr_doc["label"] = taxon["label"]
        solr_doc["type"] = "taxonomy"

        if "cell_types_count" in taxon:
            solr_doc["cell_types_count"] = next(filter(None, taxon["cell_types_count"]))
        if "cell_subclasses_count" in taxon:
            solr_doc["cell_subclasses_count"] = next(filter(None, taxon["cell_subclasses_count"]))
        if "cell_classes_count" in taxon:
            solr_doc["cell_classes_count"] = next(filter(None, taxon["cell_classes_count"]))
        if "prefLabel" in taxon:
            solr_doc["species"] = next(filter(None, taxon["prefLabel"]))
        if "has_brain_region" in taxon:
            solr_doc["anatomic_region"] = next(filter(None, taxon["has_brain_region"]))
        if "has_sex" in taxon:
            solr_doc["sex"] = next(filter(None, taxon["has_sex"]))
        if "has_age" in taxon:
            solr_doc["age"] = next(filter(None, taxon["has_age"]))
        if "database_cross_reference" in taxon:
            solr_doc["primary_citation"] = next(filter(None, taxon["database_cross_reference"]))

        all_data[solr_doc["iri"]] = solr_doc


def get_version_metadata(all_data):
    ont_metadata = GetOntologyMetadata().execute_query()

    solr_doc = dict()
    solr_doc["id"] = "ontology"
    solr_doc["iri"] = "ontology"
    solr_doc["label"] = ont_metadata["name"]
    solr_doc["version"] = ont_metadata["version"]

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
    # individuals_metadata_dump()
    individuals_metadata_solr_dump()
    # update_solr()