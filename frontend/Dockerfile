# Dockerfile pour servir des fichiers statiques avec nginx
FROM nginx:alpine


COPY templates/ /usr/share/nginx/html/
COPY static/ /usr/share/nginx/html/static/
COPY media/ /usr/share/nginx/html/media/


EXPOSE 80
