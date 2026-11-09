"""Core OpenAPI Mock Contract Generator implementation."""
import json
import re
from typing import Dict, List, Optional, Any


class MockResponse:
    def __init__(self, status_code: int, headers: Dict[str, str], body: Any):
        self.status_code = status_code
        self.headers = headers
        self.body = body


class OpenAPIMockGenerator:
    def __init__(self):
        self.routes: Dict[str, Dict[str, Any]] = {}  # "METHOD:PATH" -> route_spec
        self.call_history: List[Dict[str, Any]] = []

    def load_spec_dict(self, spec: Dict[str, Any]):
        paths = spec.get("paths", {})
        for path_pattern, methods in paths.items():
            for method, details in methods.items():
                route_key = f"{method.upper()}:{path_pattern}"
                self.routes[route_key] = details

    def synthesize_mock_value(self, schema: Dict[str, Any]) -> Any:
        t = schema.get("type", "string")
        if t == "string":
            if "example" in schema:
                return schema["example"]
            return "sample_text"
        elif t == "integer":
            return schema.get("example", 42)
        elif t == "number":
            return schema.get("example", 3.14)
        elif t == "boolean":
            return schema.get("example", True)
        elif t == "array":
            items_schema = schema.get("items", {"type": "string"})
            return [self.synthesize_mock_value(items_schema)]
        elif t == "object":
            props = schema.get("properties", {})
            return {k: self.synthesize_mock_value(v) for k, v in props.items()}
        return None

    def dispatch(self, method: str, path: str) -> MockResponse:
        self.call_history.append({"method": method.upper(), "path": path})

        # Match exact route or path param route
        target_details = None
        for r_key, details in self.routes.items():
            r_method, r_path = r_key.split(":", 1)
            if r_method != method.upper():
                continue

            # Convert OpenAPI {id} to regex
            regex_pattern = "^" + re.sub(r"\{[a-zA-Z0-9_]+\}", r"[^/]+", r_path) + "$"
            if re.match(regex_pattern, path):
                target_details = details
                break

        if not target_details:
            return MockResponse(404, {"Content-Type": "application/json"}, {"error": "Route not found in OpenAPI spec"})

        responses = target_details.get("responses", {})
        # Look for 200 or 201
        success_code = "200" if "200" in responses else ("201" if "201" in responses else list(responses.keys())[0])
        resp_spec = responses[success_code]
        content_schema = resp_spec.get("content", {}).get("application/json", {}).get("schema", {})

        body_data = self.synthesize_mock_value(content_schema) if content_schema else {}
        return MockResponse(int(success_code), {"Content-Type": "application/json"}, body_data)
