FROM nginx:1.28.0-alpine3.21

ENV API_UPSTREAM=api:8000 \
    NGINX_ENVSUBST_OUTPUT_DIR=/tmp/nginx/conf.d

COPY nginx.conf /etc/nginx/nginx.conf
COPY default.conf.template /etc/nginx/templates/default.conf.template
COPY --chown=101:101 index.html app.js style.css /usr/share/nginx/html/

RUN mkdir -p /tmp/nginx/conf.d && chown -R 101:101 /tmp/nginx

USER 101:101
EXPOSE 8080
