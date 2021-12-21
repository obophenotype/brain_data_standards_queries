import urllib
import yaml
from urllib import request


TAXONOMY_DETAILS_YAML = "https://raw.githubusercontent.com/obophenotype/brain_data_standards_ontologies/pcl_migration/src/dendrograms/taxonomy_details.yaml"

species_mapping = {"mouse": "Mus musculus",
                   "human": "Homo sapiens",
                   "marmoset": "Callithrix jacchus"}


def read_taxonomy_details_yaml():
    remote_config = urllib.request.urlopen(TAXONOMY_DETAILS_YAML)
    config = yaml.full_load(remote_config)
    return config


def get_species_mapping():
    species = dict()
    config = read_taxonomy_details_yaml()
    for taxonomy_config in config:
        taxonomy_id = str(taxonomy_config["Taxonomy_id"]).replace("CCN", "").replace("CS", "")
        species[taxonomy_id] = species_mapping[str(taxonomy_config["Species_abbv"][0]).lower()]
    return species
