"""Unit tests for openapi-mock-contract-generator."""
import unittest
from openapi_mock_contract_generator.generator import OpenAPIMockGenerator


class TestOpenAPIMockGenerator(unittest.TestCase):
    def setUp(self):
        self.gen = OpenAPIMockGenerator()
        spec = {
            "paths": {
                "/health": {
                    "get": {
                        "responses": {
                            "200": {
                                "content": {
                                    "application/json": {
                                        "schema": {"type": "object", "properties": {"status": {"type": "string", "example": "ok"}}}
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
        self.gen.load_spec_dict(spec)

    def test_mock_dispatch_match(self):
        res = self.gen.dispatch("GET", "/health")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.body.get("status"), "ok")

    def test_mock_dispatch_404(self):
        res = self.gen.dispatch("GET", "/unknown")
        self.assertEqual(res.status_code, 404)
