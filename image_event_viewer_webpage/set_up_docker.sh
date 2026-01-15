
# Clean up docker environment of containers and images
docker rm python-flask-server_container
docker rmi python-flask-server_image:latest

# Set up image viewer webpage docker image/container
docker build --progress=plain -t python-flask-server_image .
docker run -v ..:/pipeline -p 8000:8000 --name python-flask-server_container python-flask-server_image

