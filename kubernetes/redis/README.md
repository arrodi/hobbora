## Docker commands to run the container locally:

1. Pull the desired Docker image

docker pull redis:7.2-alpine

2. Create a docker volume for redis to persist data

docker volume create redis-data

3. Run the image as a container

docker run -p 6379:6379 --name redis \
  -v redis-data:/data \
  -d redis:7.2-alpine \
  redis-server --appendonly yes --save 60 1000

## Kubernetes deploy commands

kubectl apply -f kubernetes/redis/namespace.yaml
kubectl apply -f kubernetes/redis/service.yaml
kubectl apply -f kubernetes/redis/statefulset.yaml

## Example of entering the pod and using Redis CLI

```
# ENTER THE REDIS POD
kubectl -n redis exec -it redis-0 -- sh

# OPEN REDIS CLI
redis-cli

# WRITE A TEST KEY
SET session:test "hello-from-redis"

# READ THE TEST KEY
GET session:test

# LIST KEYS (DEV ONLY)
KEYS session:*

# EXIT REDIS CLI
exit
```

## Web UI env value

REDIS_URL=redis://redis-service.redis.svc.cluster.local:6379/0

## Notes

- Redis is used as a shared session store for multi-pod web-ui deployments.
- Browser stores only the session id cookie; session data is stored in Redis.
- For production hardening, add Redis auth and NetworkPolicies.
