from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from src.database.models import Contact, User
from src.schemas import ContactResponse


async def get_contacts(limit: int, offset: int, db: AsyncSession, user: User):
    sq = select(Contact).filter_by(user=user).offset(offset).limit(limit)
    contacts = await db.execute(sq)
    return contacts.scalars().all()


async def get_contact(contact_id: int, db: AsyncSession, user: User):
    sq = select(Contact).filter_by(id=contact_id, user=user)
    contact = await db.execute(sq)
    return contact.scalar_one_or_none() 


async def create_contact(body: ContactResponse, db: AsyncSession, user: User):
    contact = Contact(name=body.name, surname=body.surname, birthday=body.birthday, phone=body.phone, email=body.email,
                      user=user)
    if body.description:
        contact.description = body.description
    db.add(contact)
    await db.commit()
    await db.refresh(contact)
    return contact 


async def update_contact(contact_id: int, body: ContactResponse, db: AsyncSession, user: User):
    sq = select(Contact).filter_by(id=contact_id, user=user)
    result = await db.execute(sq)
    contact = result.scalar_one_or_none()
    if contact:
        contact.name = body.name
        contact.surname = body.surname
        contact.phone = body.phone
        contact.email = body.email
        contact.user = user
        contact.description = body.description
        await db.commit()
        await db.refresh(contact)
    return contact


async def remove_contact(contact_id: int, db: AsyncSession, user: User):
    sq = select(Contact).filter_by(id=contact_id, user=user)
    result = await db.execute(sq)
    contact = result.scalar_one_or_none()
    if contact:
        await db.delete(contact)
        await db.commit()
    return contact


async def search_contact(user: User,
                         db: AsyncSession,
                         contact_name: str,
                         surname: str,
                         email: str):
    sq = select(Contact).filter_by(user=user)
    if contact_name:
        sq = sq.filter(or_(Contact.name.ilike(f'%{contact_name}%')))
    elif surname:
        sq = sq.filter(or_(Contact.surname.ilike(f'%{surname}%')))
    elif email:
        sq = sq.filter(or_(Contact.email.ilike(f'%{email}%')))

    result = await db.execute(sq)
    contact_found = result.scalars().first()
    return contact_found


async def upcoming_birthdays(user: User, db):
    current_date = datetime.now().date()
    future_birthday = current_date + timedelta(days=7)
    sq = select(Contact).filter_by(user=user)
    result = await db.execute(sq)
    list_bd_contacts = result.scalars().all()
    happy_contacts = []
    for data in list_bd_contacts:
        ccy = data.birthday.replace(year=current_date.year)
        cfy = data.birthday.replace(year=future_birthday.year)
        if ccy >= current_date and cfy <= future_birthday:
            happy_contacts.append(data)
    return happy_contacts
