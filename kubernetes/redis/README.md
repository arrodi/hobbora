# Redis (Shared Web Session Store)

This deployment provides a shared Redis endpoint for the web-ui Flask sessions.

## Why this exists

For multi-pod web-ui deployments, session data cannot stay in pod memory/local filesystem.
All web-ui pods must read/write sessions from one shared store.

## Objects

- `namespace.yaml` → namespace `redis`
- `service.yaml` → internal service `redis-service.redis.svc.cluster.local:6379`
- `statefulset.yaml` → Redis 7.2 with persistent volume

## Deploy

```bash
kubectl apply -f kubernetes/redis/namespace.yaml
kubectl apply -f kubernetes/redis/service.yaml
kubectl apply -f kubernetes/redis/statefulset.yaml
```

## Verify

```bash
kubectl -n redis get pods,svc,pvc
kubectl -n redis logs statefulset/redis
```

## Web UI wiring

Set this in web-ui env/Helm values:

```bash
REDIS_URL=redis://redis-service.redis.svc.cluster.local:6379/0
```

## Notes

- This manifest currently runs Redis without auth/TLS for in-cluster access simplicity.
- For production hardening, add:
  - `requirepass` via Kubernetes Secret
  - NetworkPolicy to restrict access to only web-ui namespace/pods
