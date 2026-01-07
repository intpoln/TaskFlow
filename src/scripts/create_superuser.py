import asyncio
from sqlalchemy import select

from src.database import async_session_maker
from src.models.users import UserOrm
from src.services.auth import AuthService
from src.config import settings


async def create_superuser():
    async with async_session_maker() as db:
        query = select(UserOrm).filter_by(email=settings.SUPERUSER_EMAIL)
        result = await db.execute(query)
        existing = result.scalar_one_or_none()

        if existing:
            return

        hashed_password = AuthService.hash_password(settings.SUPERUSER_PASSWORD)
        superuser = UserOrm(
            email=settings.SUPERUSER_EMAIL,
            username=settings.SUPERUSER_USERNAME,
            hashed_password=hashed_password,
            is_superuser=True
        )
        db.add(superuser)
        await db.commit()
        print(f"Superuser {settings.SUPERUSER_EMAIL} created!")


if __name__ == "__main__":
    asyncio.run(create_superuser())