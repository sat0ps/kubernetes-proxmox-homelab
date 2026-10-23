FROM nginx:1.28.0-alpine3.21

COPY nginx.conf /etc/nginx/nginx.conf
COPY --chown=101:101 index.html app.js style.css /usr/share/nginx/html/

RUN mkdir -p /tmp/nginx && chown 101:101 /tmp/nginx

USER 101:101
EXPOSE 8080
