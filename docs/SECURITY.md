# Security

Current controls include strict Pydantic input validation, CORS allowlist, safe filenames, UUID storage paths, file extension and size limits, no browser secrets, stable public errors, provider exception wrapping, and prompt/data separation. Logs contain request IDs and operational fields but never configuration secrets.

Before production, add authentication, RBAC, tenant filters, malware scanning, MIME signature validation, encrypted object storage, rate limits, CSRF strategy where cookies are used, webhook signatures, secret management and retention policies. Treat uploaded content as adversarial even after parsing.