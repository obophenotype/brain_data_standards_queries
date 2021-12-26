#!/bin/bash
#
# This script updates bdsdump schema with ngram based new search fields. These new fields has naming: *_autosuggest_e
# and enable partial matching capability. To run this script, your solr should be up and running and the latest dump
# file is uploaded. You don't need to run this script in a server, can be run in any client.
#
# Important: After the schema change, reindexing is required. For this purpose, you can simply re-upload the dump data
# to the bdsdump collection.
#
# Usage:
# bash solr_post_config.sh -h localhost -p 8993

set -e

core_name=bdsdump
autocomplete_single_val_fields=(label prefLabel accession_id species)
autocomplete_multi_val_fields=(has_exact_synonym aliases tags marker_labels nsforest_marker_labels)

autocomplete_fields=("${autocomplete_single_val_fields[@]}" "${autocomplete_multi_val_fields[@]}")

while getopts h:p: flag
do
    case "${flag}" in
        h) host=${OPTARG};;
        p) port=${OPTARG};;
        *) echo "!!! Invalid flag. Only -h and -p flags are supported."
    esac
done

echo "Updating $core_name in server $host:$port"

echo "Adding textEdge field type"
curl -X POST -H 'Content-type:application/json' --data-binary "{
  \"add-field-type\":{
    \"name\":\"textEdge\",
    \"class\":\"solr.TextField\",
    \"indexAnalyzer\":{
      \"tokenizer\":{
         \"class\":\"solr.PatternTokenizerFactory\",
         \"pattern\":\"______\" },
       \"filters\":[{\"class\":\"solr.LowerCaseFilterFactory\" },
                   {\"class\":\"solr.RemoveDuplicatesTokenFilterFactory\" },
                   {\"class\":\"solr.EdgeNGramFilterFactory\",
                   \"minGramSize\":\"1\",
                   \"maxGramSize\":\"35\"}]
    },
    \"queryAnalyzer\":{
      \"tokenizer\":{
         \"class\":\"solr.PatternTokenizerFactory\",
         \"pattern\":\"______\" },
       \"filters\":[{\"class\":\"solr.LowerCaseFilterFactory\" },
                   {\"class\":\"solr.RemoveDuplicatesTokenFilterFactory\" }]
    }
  }
}" http://$host:$port/solr/$core_name/schema --show-error --fail

echo "Adding auto complete single value fields: ${autocomplete_single_val_fields[*]}"
for field in "${autocomplete_single_val_fields[@]}"; do

  echo "Adding auto complete field: ${field}"
  curl -X POST -H 'Content-type:application/json' --data-binary "{
    \"add-field\":{
       \"name\":\"${field}_autosuggest_e\",
       \"type\":\"textEdge\",
       \"indexed\":true,
       \"stored\":true,
       \"multiValued\":false
     }
  }" http://$host:$port/solr/$core_name/schema --show-error --fail

# end for
done

echo "Adding auto complete multi value fields: ${autocomplete_multi_val_fields[*]}"
for field in "${autocomplete_multi_val_fields[@]}"; do

  echo "Adding auto complete field: ${field}"
  curl -X POST -H 'Content-type:application/json' --data-binary "{
    \"add-field\":{
       \"name\":\"${field}_autosuggest_e\",
       \"type\":\"textEdge\",
       \"indexed\":true,
       \"stored\":true,
       \"multiValued\":true
     }
  }" http://$host:$port/solr/$core_name/schema --show-error --fail

# end for
done

echo "Copying auto complete fields: ${autocomplete_fields[*]}"
for field in "${autocomplete_fields[@]}"; do

  echo "Copying auto complete field: ${field}"
  # Now configure with the Schema API
  # Modify this with your desired schema configuration
  curl -X POST -H 'Content-type:application/json' --data-binary "{
    \"add-copy-field\":{
    \"source\":\"${field}\",
    \"dest\":\"${field}_autosuggest_e\"}
  }" http://$host:$port/solr/$core_name/schema --show-error --fail

# end for
done

echo "successfully finished configuring solr schema with the Schema API."
echo "SUCCESS"
