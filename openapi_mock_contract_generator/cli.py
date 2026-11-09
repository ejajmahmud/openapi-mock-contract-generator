"""CLI for openapi-mock-contract-generator."""
import sys
import argparse
from .generator import OpenAPIMockGenerator


def main():
    parser = argparse.ArgumentParser(description="OpenAPI Mock Contract Generator CLI")
    parser.add_argument("--demo", action="store_true", help="Run OpenAPI mock dispatch demo")
    args = parser.parse_args()

    if args.demo:
        gen = OpenAPIMockGenerator()
        sample_spec = {
            "paths": {
                "/users/{id}": {
                    "get": {
                        "responses": {
                            "200": {
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "type": "object",
                                            "properties": {
                                                "id": {"type": "integer", "example": 101},
                                                "name": {"type": "string", "example": "Alice Smith"}
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
        gen.load_spec_dict(sample_spec)
        resp = gen.dispatch("GET", "/users/101")
        print(f"Dispatched GET /users/101 -> Status {resp.status_code}")
        print(f"Mock Response Body: {resp.body}")
    else:
        parser.print_help()
    sys.exit(0)


if __name__ == "__main__":
    main()
