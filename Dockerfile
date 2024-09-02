FROM python:latest

# Actualizar apt y actualizar pip
RUN apt-get -y update && apt-get -y upgrade
RUN python -m pip install --upgrade pip
RUN python -m pip install poetry python-dotenv

# Copiar los archivos de la aplicación
ADD . /app/
WORKDIR /app
RUN poetry install

# Asegurarse de que el contenedor escuche en el puerto 8080
ENV PORT 8080
EXPOSE 8080
CMD ["poetry", "run", "geppetto"]
