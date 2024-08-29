FROM python:latest

RUN apt-get -y update && apt-get -y upgrade
RUN python -m pip install --upgrade pip
RUN python -m pip install poetry
RUN python -m pip install python-dotenv
ADD . /app/
COPY .env.example /app/config/.env
WORKDIR /app
RUN poetry install

# Asegura que el contenedor escuche en el puerto 8080
ENV PORT 8080
EXPOSE 8080

CMD [ "poetry", "run", "geppetto" ]
