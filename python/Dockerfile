FROM python:3.7

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY . .
CMD python -m squawkapi
EXPOSE 5000