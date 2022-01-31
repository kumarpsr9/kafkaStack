FROM python:3.9
WORKDIR /code
#COPY ./code/requirements.txt /code/requirements.txt
COPY ./code /code
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
RUN chmod +x /code/run.sh
CMD ["/code/run.sh"]
