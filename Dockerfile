FROM python:latest

# Instalar Nginx
RUN apt-get -y update && apt-get -y install nginx

# Copiar los archivos de la aplicación
ADD . /app/
WORKDIR /app

# Instalar las dependencias de Python
RUN python -m pip install poetry
RUN poetry install

# Crear una página en blanco para servir
RUN echo "<html><body></body></html>" > /var/www/html/index.html

# Configurar Nginx para servir la página en blanco
RUN echo "server { \
    listen 8080; \
    server_name localhost; \
    location / { \
        root /var/www/html; \
        index index.html; \
    } \
}" > /etc/nginx/conf.d/default.conf

# Exponer el puerto 8080 para Google Cloud Run
EXPOSE 8080

# Crear un script de inicio para manejar Nginx y la aplicación
RUN echo "#!/bin/sh\n\
service nginx start\n\
poetry run geppetto" > /app/entrypoint.sh

# Hacer que el script sea ejecutable
RUN chmod +x /app/entrypoint.sh

# Usar el script de inicio como el comando principal
CMD ["/app/entrypoint.sh"]
