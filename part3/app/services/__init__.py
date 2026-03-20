from app.services.facade import HBnBFacade

# This is the single global instance of the Facade (Singleton-like pattern)
# All API endpoints must import this exact instance to share the in-memory data.
facade = HBnBFacade()
