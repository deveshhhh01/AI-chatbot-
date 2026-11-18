from typing import Optional
from fastapi import APIRouter, Query, HTTPException
from backend.app.database.repositories import ProjectRepository
from backend.app.schemas.project_schema import ProjectListResponse, ProjectItem

router = APIRouter(prefix="/projects", tags=["Projects"])


@router.get("", response_model=ProjectListResponse)
def list_projects(
    source: Optional[str] = Query(default=None, description="Filter by source: 'DarGlobal' or 'Wasalt'"),
    country: Optional[str] = Query(default=None, description="Filter by country"),
    city: Optional[str] = Query(default=None, description="Filter by city"),
    property_type: Optional[str] = Query(default=None, description="Filter by property type"),
    q: Optional[str] = Query(default=None, description="Search term in project name or location"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100)
):
    offset = (page - 1) * page_size
    raw_projects = ProjectRepository.list_projects(
        source=source,
        country=country,
        city=city,
        property_type=property_type,
        search_query=q,
        limit=page_size,
        offset=offset
    )
    total_count = ProjectRepository.count_projects(source=source)

    items = [ProjectItem(**p) for p in raw_projects]
    return ProjectListResponse(
        total=total_count,
        page=page,
        page_size=page_size,
        projects=items
    )


@router.get("/{project_id}", response_model=ProjectItem)
def get_project(project_id: str):
    project = ProjectRepository.get_project_by_id(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project or listing not found")
    return ProjectItem(**project)
