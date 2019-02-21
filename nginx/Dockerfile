FROM nginx:1.15.0-alpine

# remove default nginx config and use ours
RUN rm /etc/nginx/conf.d/default.conf
COPY nginx.conf /etc/nginx/conf.d