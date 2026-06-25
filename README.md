# Travel Planner API

A CRUD application for managing travel projects and places, built with FastAPI and SQLite.

## Features

- Create, read, update, delete travel projects
- Add places to projects from the Art Institute of Chicago API
- Add notes to places and mark them as visited
- Automatic project completion when all places are visited
- Validation to prevent duplicate places in a project
- Limit of 10 places per project
- Cannot delete projects with visited places

## Requirements

- Python 3.8+
- Dependencies listed in `requirements.txt`

## Setup

1. Clone the repository
2. Create a virtual environment: `python -m venv venv`
3. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - Unix/Linux/macOS: `source venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Run the application: `uvicorn app.main:app --reload`

## Docker Support

The application includes a `Dockerfile` for easy containerization:

```bash
# Build the Docker image
docker build -t travel-planner .

# Run the container
docker run -p 8000:8000 travel-planner
```

## API Testing with Postman

A Postman collection (`travel_planner.postman_collection.json`) is included for testing all endpoints. Simply import this file into Postman to get started with pre-configured requests.

## API Endpoints

### Projects
- `GET /api/v1/projects/` - List all projects
- `POST /api/v1/projects/` - Create a new project
- `GET /api/v1/projects/{id}` - Get a specific project
- `PUT /api/v1/projects/{id}` - Update a project
- `DELETE /api/v1/projects/{id}` - Delete a project (only if no places are visited)

### Places
- `GET /api/v1/projects/{project_id}/places/` - List places in a project
- `POST /api/v1/projects/{project_id}/places/` - Add a place to a project
- `GET /api/v1/projects/{project_id}/places/{place_id}` - Get a specific place
- `PUT /api/v1/projects/{project_id}/places/{place_id}` - Update a place
- `DELETE /api/v1/projects/{project_id}/places/{place_id}` - Delete a place
- `PATCH /api/v1/projects/{project_id}/places/{place_id}/notes` - Update place notes
- `PATCH /api/v1/projects/{project_id}/places/{place_id}/visit` - Mark place as visited

## Documentation

Interactive API documentation is available at http://localhost:8000/docs