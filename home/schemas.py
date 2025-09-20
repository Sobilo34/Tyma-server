from ninja import Schema
from typing import List, Optional, Generic, TypeVar
from datetime import date, datetime
from enum import Enum
from uuid import UUID
from ninja.pagination import PaginationBase

T = TypeVar('T')

class PaginatedResponseSchema(Schema, Generic[T]):
    items: List[T]
    total: int
    per_page: int
    page: int

class CustomPagination(PaginationBase):
    class Input(Schema):
        page: int = 1
        per_page: int = 10

    class Output(PaginatedResponseSchema[T]):
        pass

    def paginate_queryset(self, queryset, pagination: Input, **params):
        page = pagination.page
        per_page = pagination.per_page
        offset = (page - 1) * per_page
        total = queryset.count()
        return {
            "items": queryset[offset:offset + per_page],
            "total": total,
            "page": page,
            "per_page": per_page,
        }

class HTTPStatusCode(int, Enum):
    OK = 200
    SUCCESS = 200
    CREATED = 201
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    UNPROCESSABLE_ENTITY = 422
    INTERNAL_SERVER_ERROR = 500
    MULTI_STATUS = 207
    NOT_MODIFIED = 304
    CONFLICT = 409
    NOT_ACCEPTABLE = 406
    NOT_IMPLEMENTED = 501

class StandardResponseDTO(Schema, Generic[T]):
    data: Optional[T] = None
    status_code: HTTPStatusCode = HTTPStatusCode.OK
    success: bool = True
    message: str

class ZoneOut(Schema):
    id: UUID
    name: str
    slug: str
    description: str
    created_at: datetime
    updated_at: datetime

class TYMAImageOut(Schema):
    id: UUID
    title: Optional[str]
    url: Optional[str]
    alt_text: Optional[str]
    caption: Optional[str]
    image_type: str
    content_type: Optional[str]
    object_id: Optional[str]
    created_at: datetime
    updated_at: datetime

class TYMAImageCreateSchema(Schema):
    title: Optional[str] = None
    alt_text: Optional[str] = None
    caption: Optional[str] = None
    image_type: str = 'OTHER'
    content_type_id: Optional[int] = None
    object_id: Optional[str] = None

class TYMAImageUpdateSchema(Schema):
    title: Optional[str] = None
    alt_text: Optional[str] = None
    caption: Optional[str] = None
    image_type: Optional[str] = None

class OfficialOut(Schema):
    id: UUID
    zone: ZoneOut
    name: str
    official_id: str
    phone: str
    email: Optional[str] = None
    position: str
    official_type: str
    bio: Optional[str] = None
    profile_image: Optional[TYMAImageOut]
    is_active: bool
    order: int
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    created_at: datetime
    updated_at: datetime

ZoneOut.update_forward_refs()

class OfficialCreateSchema(Schema):
    firstname: str
    lastname: str
    zone_name: str
    phone: str
    position: str
    official_type: str
    email: Optional[str] = None
    bio: Optional[str] = None
    profile_image_id: Optional[str] = None

class OfficialUpdateSchema(Schema):
    firstname: Optional[str] = None
    lastname: Optional[str] = None
    zone_name: Optional[str] = None
    phone: Optional[str] = None
    position: Optional[str] = None
    official_type: Optional[str] = None
    email: Optional[str] = None
    bio: Optional[str] = None
    profile_image_id: Optional[str] = None

class ZoneCreateSchema(Schema):
    name: str
    description: Optional[str] = None

class ZoneUpdateSchema(Schema):
    name: Optional[str] = None
    description: Optional[str] = None

class NewsCategoryOut(Schema):
    id: UUID
    name: str
    slug: str
    description: Optional[str]
    created_at: datetime
    updated_at: datetime

class NewsOut(Schema):
    id: UUID
    title: str
    slug: str
    news_type: str
    categories: List[NewsCategoryOut]
    short_description: str
    content: str
    featured_image: Optional[TYMAImageOut]  # Updated to use TYMAImageOut
    is_featured: bool
    event_date: Optional[datetime]
    event_location: Optional[str]
    published_at: datetime
    author: Optional[str]
    views: int
    created_at: datetime
    updated_at: datetime

class NewsCreateSchema(Schema):
    title: str
    news_type: str
    short_description: str
    content: str
    author_id: str 
    category_slugs: Optional[List[str]] = None 
    featured_image_id: Optional[str] = None
    is_featured: bool = False
    event_date: Optional[datetime] = None
    event_location: Optional[str] = None

class NewsUpdateSchema(Schema):
    title: str
    news_type: str
    short_description: str
    content: str
    author_id: str 
    category_slugs: Optional[List[str]] = None 
    featured_image_id: Optional[str] = None
    is_featured: bool = False
    event_date: Optional[datetime] = None
    event_location: Optional[str] = None

class NewsSearchSchema(Schema):
    search: Optional[str] = None
    news_type: Optional[str] = None
    category_slug: Optional[str] = None
    is_featured: Optional[bool] = None
    author_id: Optional[str] = None
    year: Optional[int] = None
    month: Optional[int] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    sort_by: str = "-published_at"

class NewsCategoryCreateSchema(Schema):
    name: str
    description: Optional[str] = None

# Contact Us Schemas
class ContactSubmissionCreateSchema(Schema):
    name: str
    email: str
    phone: Optional[str] = None
    subject: str  # Should match SUBJECT_CHOICES in model
    message: str

    # Add custom validation
    def __init__(self, **data):
        super().__init__(**data)
        # Validate name length
        if len(self.name.strip()) < 2:
            raise ValueError("Name must be at least 2 characters long")
        if len(self.name) > 200:
            raise ValueError("Name cannot exceed 200 characters")
        
        # Validate message length
        if len(self.message.strip()) < 10:
            raise ValueError("Message must be at least 10 characters long")
        if len(self.message) > 5000:
            raise ValueError("Message cannot exceed 5000 characters")
            
        # Validate phone if provided
        if self.phone and len(self.phone) > 20:
            raise ValueError("Phone number cannot exceed 20 characters")

class ContactSubmissionOut(Schema):
    id: UUID
    name: str
    email: str
    phone: Optional[str] = None
    subject: str
    message: str
    submitted_at: datetime
    is_responded: bool
    response_notes: Optional[str] = None

# Newsletter Schemas
class NewsletterSubscribeSchema(Schema):
    email: str

class NewsletterSubscriberOut(Schema):
    id: UUID
    email: str
    is_active: bool
    subscribed_at: datetime
    unsubscribed_at: Optional[datetime] = None

class NewsletterUnsubscribeSchema(Schema):
    email: str