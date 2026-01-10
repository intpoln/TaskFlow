from src.models import ProjectOrm
from src.repositories.base import BaseRepository


class ProjectRepository(BaseRepository):
    model = ProjectOrm