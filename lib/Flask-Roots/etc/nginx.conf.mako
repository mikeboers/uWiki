server {
	listen 80;
	server_name www.${DOMAIN};
	rewrite ^ http://${DOMAIN}$request_uri? permanent;
}

server {
    listen 80;
    server_name ${DOMAIN};
	
    location / {
        proxy_pass http://localhost:${PORT};
        proxy_buffering off;
        proxy_set_header Host $http_host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
