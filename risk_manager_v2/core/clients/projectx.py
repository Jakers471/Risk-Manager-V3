"""
Import adapter for ProjectXClient.
Keeps a stable import path: risk_manager_v2.core.clients.projectx.ProjectXClient
Agent B will replace this with the real implementation.
"""
try:
    # try a newer location if you had it
    from risk_manager_v2.core.projectx_client import ProjectXClient  # type: ignore
except Exception:
    try:
        # fallback to older name
        from risk_manager_v2.core.client import ProjectXClient  # type: ignore
    except Exception as e:
        raise ImportError(
            "ProjectXClient implementation not found. "
            "Provide core/projectx_client.py or core/client.py"
        ) from e

