from typing import List

from fastapi import APIRouter, HTTPException, Depends, Path, Query, status, Security
from fastapi.security import HTTPAuthorizationCredentials

from src.database.db import get_db
from src.database.models import User
from src.routes.auth import security
from src.schemas import ContactResponse, ContactModel
from sqlalchemy.ext.asyncio import AsyncSession

from src.repository import contacts as response_contacts
from src.services.auth import auth_service

router = APIRouter(prefix="/contacts", tags=["contacts"])


@router.get("/", response_model=List[ContactResponse], status_code=status.HTTP_200_OK)
async def get_contacts(limit: int = Query(10, ge=10, le=500), offset: int = Query(0, ge=0, le=200),
                       credentials: HTTPAuthorizationCredentials = Security(security),
                       db: AsyncSession = Depends(get_db)):
    token = credentials.credentials
    user = await auth_service.authorised_user(token, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized",
        )
    contacts = await response_contacts.get_contacts(limit, offset, db, user)
    return contacts 


@router.get("/{contact_id}", response_model=ContactResponse)
async def get_contact(contact_id: int = Path(ge=1), credentials: HTTPAuthorizationCredentials = Security(security),
                      db: AsyncSession = Depends(get_db)):
    token = credentials.credentials
    user = await auth_service.authorised_user(token, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized",
        )
    contact = await response_contacts.get_contact(contact_id, db, user)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="NOT FOUND",
        )
    return contact


@router.post("", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
async def create_contact(body: ContactModel,
                         credentials: HTTPAuthorizationCredentials = Security(security),
                         db: AsyncSession = Depends(get_db)):
    token = credentials.credentials
    user = await auth_service.authorised_user(token, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized",
        )
    contact = await response_contacts.create_contact(body, db, user)
    return contact


@router.put("/{contact_id}", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
async def update_contact(body: ContactModel, contact_id: int = Path(ge=1),
                         credentials: HTTPAuthorizationCredentials = Security(security),
                         db: AsyncSession = Depends(get_db)):
    token = credentials.credentials
    user = await auth_service.authorised_user(token, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized",
        )
    contact = await response_contacts.update_contact(contact_id, body, db, user)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="NOT FOUND",
        )
    return contact


@router.delete("/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_contact(contact_id: int = Path(ge=1),
                         credentials: HTTPAuthorizationCredentials = Security(security),
                         db: AsyncSession = Depends(get_db)):
    token = credentials.credentials
    user = await auth_service.authorised_user(token, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized",
        )
    contact = await response_contacts.remove_contact(contact_id, db, user)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="NOT FOUND",
        )
    return contact


@router.get("/search/{user_id}", response_model=ContactResponse, status_code=status.HTTP_200_OK)
async def search_contact(credentials: HTTPAuthorizationCredentials = Security(security),
                         contact_name: str = Query(None, min_length=2),
                         surname: str = Query(None, min_length=2),
                         email: str = Query(None),
                         db: AsyncSession = Depends(get_db)
                         ):
    token = credentials.credentials
    user = await auth_service.authorised_user(token, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized",
        )
    contact = await response_contacts.search_contact(user, db, contact_name, surname, email)
    if contact is None:
        raise HTTPException(
            status_code=404,
            detail="NOT FOUND",
        )
    return contact


@router.get("/birthdays/{user_id}", response_model=List[ContactResponse])
async def upcoming_birthdays(credentials: HTTPAuthorizationCredentials = Security(security),
                             db: AsyncSession = Depends(get_db)):
    token = credentials.credentials
    user = await auth_service.authorised_user(token, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized",
        )
    contacts = await response_contacts.upcoming_birthdays(user, db)
    if not contacts:
        raise HTTPException(
            status_code=404,
            detail="No upcoming birthdays found for the user.",
        )
    return contacts
