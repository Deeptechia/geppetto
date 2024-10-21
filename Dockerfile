FROM python:latest

# Actualizar e instalar dependencias necesarias para compilación
RUN apt-get -y update && apt-get -y upgrade && apt-get install -y \
    curl \
    build-essential \
    libssl-dev \
    pkg-config

# Instalar cargo (para dependencias Rust)
RUN curl https://sh.rustup.rs -sSf | sh -s -- -y && source $HOME/.cargo/env

# Actualizar pip y poetry
RUN python -m pip install --upgrade pip
RUN python -m pip install poetry

# Copiar los archivos de la aplicación al contenedor
ADD . /app/
WORKDIR /app

# Instalar dependencias usando poetry
RUN POETRY_VIRTUALENVS_CREATE=false poetry install --no-dev --no-root

# Comando por defecto para ejecutar la aplicación
CMD [ "poetry", "run", "geppetto" ]


#RUN apt-get -y update && apt-get -y upgrade
#RUN python -m pip install --upgrade pip
#RUN python -m pip install poetry
#ADD . /app/
#WORKDIR /app
#RUN poetry install
#CMD [ "poetry", "run", "geppetto" ]
