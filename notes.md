# FastAPI Backend Application

## Overview
This is a FastAPI backend application that provides REST API endpoints for managing users, products, companies, orders, employees, and accounts. The project was successfully imported from GitHub and configured to run in the Replit environment.

## Project Structure
- **Backend Framework**: FastAPI
- **Package Manager**: uv
- **Database**: SQLite (local file-based)
- **Port**: 8000 (backend server)

## Current Status
✅ Successfully set up and running in Replit environment
✅ All dependencies installed via uv
✅ Backend server running on port 8000
✅ API documentation available at `/docs`
✅ Deployment configuration set up for autoscale

## Key Features
- RESTful API with FastAPI
- SQLAlchemy ORM for database operations
- Automatic API documentation via Swagger UI
- CORS middleware configured
- Pydantic models for data validation
- Structured project layout with separate modules for:
  - API endpoints (`/api/v1/`)
  - Database models and schemas
  - CRUD operations
  - Core configuration

## API Endpoints
The application provides the following API endpoint groups:
- `/api/v1/users/` - User management
- `/api/v1/products/` - Product management
- `/api/v1/companies/` - Company management
- `/api/v1/orders/` - Order management
- `/api/v1/employees/` - Employee management
- `/api/v1/accounts/` - Account management

## Development
- Access API documentation: `http://localhost:8000/docs`
- Health check endpoint: `http://localhost:8000/health`
- The backend server automatically reloads on file changes

## Deployment
The project is configured for autoscale deployment, which is ideal for this stateless API backend.

## Architecture Decisions
- **Date**: September 20, 2025
- Kept existing SQLite database configuration for simplicity
- Maintained original project structure and dependencies
- Set up on port 8000 to avoid conflicts with potential frontend applications
- Used uv for package management as specified in the original project