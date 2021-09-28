FROM python:3.6.2

RUN mkdir /code /code/src /code/vfb_connect_api
ADD requirements.txt /code/

RUN pip install -r /code/requirements.txt
# copy except __init__.py file and test folder
ADD src/scripts/search /code/scripts/search
ADD src/config/search_config.ini /code/config/

WORKDIR /code

RUN ls -l /code && ls -l /code/scripts && ls -l /code/scripts/search

ENTRYPOINT bash -c "cd /code/scripts; python3 search/search_service.py"