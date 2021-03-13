FROM colares07/python-redes-neurais:latest

COPY ./src /app
WORKDIR /app

#RUN pip install --upgrade pip
RUN pip install -r requirements.txt

#RUN conda install -c conda-forge pika

ENTRYPOINT [ "python" ]
CMD [ "-u","consumer.py" ]
