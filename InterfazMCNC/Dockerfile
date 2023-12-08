
# Click nbfs://nbhost/SystemFileSystem/Templates/Licenses/license-default.txt to change this license
# Click nbfs://nbhost/SystemFileSystem/Templates/Other/Dockerfile to edit this template

FROM azul/zulu-openjdk:17.0.9
WORKDIR /app

# Copia los archivos necesarios a la imagen
COPY ./dist/ /app

# Instala las bibliotecas necesarias
RUN apt-get update && \
    apt-get install -y libxext6 libxrender1 libxtst6 libxi6

# Ejecuta tu aplicación
CMD ["java", "-jar", "InterfazMCNC.jar"]