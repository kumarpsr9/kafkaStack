FROM python:3.9
WORKDIR /code
#COPY ./code/requirements.txt /code/requirements.txt
#COPY ./code /code
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
#CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
RUN chmod +x /code/run.sh
CMD ["/code/run.sh"]