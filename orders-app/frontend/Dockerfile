FROM nginx:1.28.0-alpine3.21

COPY nginx.conf /etc/nginx/nginx.conf
COPY --chown=101:101 index.html app.js style.css /usr/share/nginx/html/

USER 101:101
EXPOSE 8080
