# syntax=docker/dockerfile:1
FROM ghcr.io/berriai/litellm@sha256:a3715fa7ad8387941ab697259bd2881d68931657247a41984f90fae6d11c62bf

COPY infra/litellm/config.yaml /app/config.yaml

ENTRYPOINT ["docker/prod_entrypoint.sh"]
CMD ["--config", "/app/config.yaml", "--port", "4000", "--telemetry", "false"]
