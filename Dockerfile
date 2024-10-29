FROM python:3.12

# Definir las variables como argumentos de build
ARG SLACK_BOT_TOKEN
ARG SLACK_APP_TOKEN
ARG OPENAI_API_KEY
ARG CHATGPT_MODEL
ARG DALLE_MODEL
ARG SIGNING_SECRET
ARG GOOGLE_API_KEY
ARG GEMINI_MODEL
ARG CLAUDE_API_KEY
ARG CLAUDE_MODEL
ARG GEPPETTO_VERSION

# Exportar las variables como variables de entorno para tiempo de ejecución
ENV SLACK_BOT_TOKEN=${SLACK_BOT_TOKEN}
ENV SLACK_APP_TOKEN=${SLACK_APP_TOKEN}
ENV OPENAI_API_KEY=${OPENAI_API_KEY}
ENV CHATGPT_MODEL=${CHATGPT_MODEL}
ENV DALLE_MODEL=${DALLE_MODEL}
ENV SIGNING_SECRET=${SIGNING_SECRET}
ENV GOOGLE_API_KEY=${GOOGLE_API_KEY}
ENV GEMINI_MODEL=${GEMINI_MODEL}
ENV CLAUDE_API_KEY=${CLAUDE_API_KEY}
ENV CLAUDE_MODEL=${CLAUDE_MODEL}
ENV GEPPETTO_VERSION=${GEPPETTO_VERSION}

# Actualizar e instalar dependencias necesarias para compilación
RUN apt-get -y update && apt-get -y upgrade && apt-get install -y \
    curl \
    build-essential \
    libssl-dev \
    pkg-config

# Instalar rustup y cargo (para dependencias Rust)
RUN curl https://sh.rustup.rs -sSf | sh -s -- -y

# Añadir cargo a la variable de entorno PATH
ENV PATH="/root/.cargo/bin:${PATH}"

# Actualizar pip y poetry
RUN python -m pip install --upgrade pip
RUN python -m pip install poetry
RUN poetry --version


# Instalar tokenizers sin PEP 517
RUN pip install --use-pep517 "tokenizers==0.20.1"

# Copiar los archivos de la aplicación al contenedor
ADD . /app/
WORKDIR /app

# Instalar dependencias usando poetry
#RUN POETRY_VIRTUALENVS_CREATE=false pip install --no-build-isolation --no-cache-dir tokenizers==0.20.1
RUN POETRY_VIRTUALENVS_CREATE=false poetry install --only main
RUN poetry run python -m dotenv --version

# Verificar que `dotenv` y otras dependencias estén instaladas
RUN poetry show

# Comando por defecto para ejecutar la aplicación
CMD [ "poetry", "run", "geppetto", "-m", "geppetto.main" ]


#RUN apt-get -y update && apt-get -y upgrade
#RUN python -m pip install --upgrade pip
#RUN python -m pip install poetry
#ADD . /app/
#WORKDIR /app
#RUN poetry install
#CMD [ "poetry", "run", "geppetto" ]
