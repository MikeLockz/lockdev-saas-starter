# API Reference

The API reference is automatically generated from the FastAPI application.

## Local Documentation
When running the application locally, you can access the interactive documentation at:
- Swagger UI: [http://localhost:8001/docs](http://localhost:8001/docs)
- Redoc: [http://localhost:8001/redoc](http://localhost:8001/redoc)

## OpenAPI Specification
The raw OpenAPI JSON schema can be found at:
- [http://localhost:8001/openapi.json](http://localhost:8001/openapi.json)

## Type Generation
Frontend types are generated using the following command:
```bash
make generate:types
```
This script dumps the OpenAPI schema and generates TypeScript interfaces and Zod schemas.
