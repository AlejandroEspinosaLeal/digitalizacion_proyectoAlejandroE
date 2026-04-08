"""
Dependencies module.

Provides FastAPI dependency injections such as database sessions and current user access.
"""

def get_db():
    """Yields a database session."""
    pass

def get_current_user():
    """Decodes JWT tokens and returns the active user."""
    pass
