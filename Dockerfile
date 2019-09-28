FROM continuumio/anaconda3:4.4.0
MAINTAINER UNP, https://unp.education

COPY /route_scout /usr/local/python/

EXPOSE 8050

WORKDIR /usr/local/python

RUN pip install -r requirements.txt

CMD python app.py
