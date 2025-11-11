import logging
import pytest
from fastapi import FastAPI, Depends
from fastapi.testclient import TestClient
from pyfunclog.async_support import FastAPILoggingSupport
from pyfunclog import async_secure_log_function

class TestFastAPI:
    def test_fastapi_middleware(self):
        """Test FastAPI middleware integration"""
        app = FastAPI()
        logging_support = FastAPILoggingSupport()
        
        # Add middleware
        logging_support.middleware(app)
        
        @app.get("/test")
        @async_secure_log_function()
        async def test_endpoint():
            return {"message": "Hello World"}
        
        client = TestClient(app)
        response = client.get("/test")
        
        assert response.status_code == 200
        assert response.json() == {"message": "Hello World"}

    def test_fastapi_dependency_injection(self, caplog):
        """Test FastAPI with dependency injection"""
        app = FastAPI()
        
        async def get_database():
            return {"db": "connection"}
        
        @app.get("/items/{item_id}")
        @async_secure_log_function()
        async def read_item(item_id: int, db: dict = Depends(get_database)):
            result = {"item_id": item_id, "db_connected": True}
            return result
        
        client = TestClient(app)
        
        with caplog.at_level(logging.INFO):
            response = client.get("/items/42")
            
        assert response.status_code == 200
        assert "read_item" in caplog.text
        assert "item_id" in caplog.text