## Docker commands to run the container locally:

1. Pull the desired Docker image

docker pull minio/minio

2. Create a docker volume for minio to persist data

docker volume create minio-data

3. Run the image as a container

docker run -p 9000:9000 -p 9001:9001 --name minio \
  -v minio-data:/data \
  -e "MINIO_ROOT_USER=minioadmin" \
  -e "MINIO_ROOT_PASSWORD=super_secure_password_987" \
  minio/minio server /data --console-address ":9001"

