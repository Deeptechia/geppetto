FROM python:latest

# Actualizar apt y actualizar pip
RUN apt-get -y update && apt-get -y upgrade
RUN python -m pip install --upgrade pip
RUN python -m pip install poetry python-dotenv

# Copiar los archivos de la aplicación
ADD . /app/
WORKDIR /app

# Crear archivo .env con variables de entorno pasadas como argumentos al build
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

# Crear el archivo .env basado en los argumentos
RUN echo "SLACK_BOT_TOKEN=$SLACK_BOT_TOKEN" > /app/config/.env && \
    echo "SLACK_APP_TOKEN=$SLACK_APP_TOKEN" >> /app/config/.env && \
    echo "OPENAI_API_KEY=$OPENAI_API_KEY" >> /app/config/.env && \
    echo "CHATGPT_MODEL=$CHATGPT_MODEL" >> /app/config/.env && \
    echo "DALLE_MODEL=$DALLE_MODEL" >> /app/config/.env && \
    echo "SIGNING_SECRET=$SIGNING_SECRET" >> /app/config/.env && \
    echo "GOOGLE_API_KEY=$GOOGLE_API_KEY" >> /app/config/.env && \
    echo "GEMINI_MODEL=$GEMINI_MODEL" >> /app/config/.env && \
    echo "CLAUDE_API_KEY=$CLAUDE_API_KEY" >> /app/config/.env && \
    echo "CLAUDE_MODEL=$CLAUDE_MODEL" >> /app/config/.env && \
    echo "GEPPETTO_VERSION=$GEPPETTO_VERSION" >> /app/config/.env

RUN poetry install

# Asegurarse de que el contenedor escuche en el puerto 8080
ENV PORT 8080

CMD ["poetry", "run", "geppetto"]
