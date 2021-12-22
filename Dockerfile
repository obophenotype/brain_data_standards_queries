FROM python:3.6.2

ENV SOLR_HOST=ec2-3-143-113-50.us-east-2.compute.amazonaws.com
ENV SOLR_PORT=8993
ENV SOLR_COLLECTION=bdsdump

RUN mkdir /code /code/src /code/bds_api
ADD requirements.txt run.sh setup.py logging.conf /code/

RUN chmod 777 /code/run.sh
RUN pip install -r /code/requirements.txt
# copy except __init__.py file and test folder
ADD src/bds_api/endpoints /code/bds_api/endpoints
ADD src/bds_api/exception /code/bds_api/exception
ADD src/bds_api/utils /code/bds_api/utils
ADD src/bds_api/config /code/bds_api/config
ADD src/bds_api/app.py src/bds_api/settings.py src/bds_api/restplus.py /code/bds_api/

WORKDIR /code

RUN cd /code && python3 setup.py develop
RUN ls -l /code && ls -l /code/bds_api

ENTRYPOINT bash -c "cd /code; python3 bds_api/app.py"