# BDS Production Environment Deployment Guide

# Table of Contents
1. [Deploy Knowledge Graph](#deploy-knowledge-graph)
2. [Deploy Solr](#deploy-solr)
3. [Deploy Knowledge API](#deploy-knowledge-api)

Knowledge Graph is a standalone application and can be deployed independently of the other two components. Knowledge API uses Solr for searching and data access.

In this documentation all deployments will be done to the same server.

`$WORKSPACE` indicates a folder in the server where we will clone projects into it.

`$SERVER_IP` indicates the ip address of the server where the deployment will be made.

## Deploy Knowledge Graph

To build the project, clone the project to your server.
```
cd $WORKSPACE
git clone https://github.com/hkir-dev/brain_data_standards_kb.git
```

Navigate to the project folder and build the docker image:
```
cd brain_data_standards_kb
docker build -t bds/kb-prod:standalone .
```

To run the built Docker image:
```
docker run -d -p:7474:7474 -p 7687:7687 bds/kb-prod:standalone
```

At startup, KB automatically loads the backup data, and you can start exploring the knowledge graph through your browser.

Open http://SERVER_IP:7474/browser/ in your browser. You do not need to enter any `Username` or `Password`, so you can leave these fields blank and directly click the `Connect` button. 

Click the `Database` icon in the upper left corner . Under the `Node Labels` section, you can find the labels of the KB entities. Click on one of the labels and start browsing.

### __Alternative:__ Deploy Knowledge Graph (DockerHub Based)
Alternative to local build based approach, [DockerHub image](https://hub.docker.com/r/hkir/kb-prod/tags) can be used for the deployment of the knowledge graph:
```
docker run -d -p:7474:7474 -p 7687:7687 hkir/kb-prod:standalone
```

## Deploy Solr

To build the Solr, clone the project to your server.
```
cd $WORKSPACE
git clone https://github.com/hkir-dev/brain_data_standards_solr.git
```

Navigate to the project folder and build the docker image:
```
cd brain_data_standards_solr
docker build -t bds/solr-prod .
```

To run the built Docker image:
```
mkdir solr_data
sudo chown 8983:8983 solr_data  # necessary on Linux, not Mac.
docker run -d -v "$PWD/solr_data:/var/solr" -p 8983:8983 --name bds_solr bds/solr-prod
```
Now you should be able to see [Solr home page](http://SERVER_IP:8983/solr) and the [created core](http://SERVER_IP:8983/solr/#/~cores/bdsdump).

To index the bds data:
```
docker exec -it bds_solr post -c bdsdump /opt/bds_data/index.json
```

Now you should see indexed data when you browse the [query interface](http://SERVER_IP:8983/solr/#/bdsdump/query) and click the 'Execute Query' button.

Run BDS schema update script:
```
wget https://raw.githubusercontent.com/obophenotype/brain_data_standards_queries/main/src/bds_api/scripts/solr_post_config.sh -O solr_post_config.sh
bash solr_post_config.sh -h $SERVER_IP -p 8983
```

Re-index the BDS data to make use of the new schema
```
docker exec -it bds_solr post -c bdsdump /opt/bds_data/index.json
```

Now Solr is ready to be used by the Knowledge API.

## Deploy Knowledge API

To build the Solr, clone the project to your server.
```
cd $WORKSPACE
git clone https://github.com/obophenotype/brain_data_standards_queries.git
```

Navigate to the project folder and build the docker image:
```
cd brain_data_standards_queries
docker build -t bds/search-service .
```

To run the built Docker image:
```
docker run -p 8484:8080 -e SOLR_HOST=$SERVER_IP -e SOLR_PORT=8983 -e SOLR_COLLECTION=bdsdump -e HTTPS=True -it bds/search-service 
```
_(Default value of the `HTTPS` parameter is `True`, so please set it based on your environment. If your deployment environment is not https, setting HTTPS=True will cause swagger interface to crash)_ 

Now you can browse the API [Swagger interface](http://SERVER_IP:8484/bds/) and run one of the example queries. Such as: http://SERVER_IP:8484/bds/api/autocomplete?query=L5%2F6%2520NP
