from ninja import Router, Query, Form
from ninja.files import UploadedFile
from typing import List, Optional, Dict
from uuid import UUID
from .schemas import (
    HTTPStatusCode,
    StandardResponseDTO, 
    ZoneCreateSchema, 
    ZoneUpdateSchema, 
    ZoneOut, 
    OfficialCreateSchema, 
    OfficialUpdateSchema, 
    OfficialOut,
    PaginatedResponseSchema,
    ContactSubmissionCreateSchema,
    ContactSubmissionOut,
    NewsletterSubscribeSchema,
    NewsletterSubscriberOut,
    NewsletterUnsubscribeSchema
)
from .services import OfficialService, ZoneService, ContactService, NewsletterService
from django.http import HttpRequest
from ninja.pagination import paginate, PageNumberPagination

official_router = Router(tags=["Officials"])
zone_router = Router(tags=["Zones"])
contact_router = Router(tags=["Contact"])
newsletter_router = Router(tags=["Newsletter"])

# Zone Endpoints
@zone_router.post("/", response=StandardResponseDTO[ZoneOut], summary="Create a new zone")
def create_zone(request: HttpRequest, payload: ZoneCreateSchema):
    res = ZoneService.create_zone(**payload.dict())
    return zone_router.api.create_response(request, res, status=res.status_code)

@zone_router.get("/{zone_slug}/", response=StandardResponseDTO[ZoneOut], summary="Get a zone by slug")
def get_zone(request: HttpRequest, zone_slug: str):
    res = ZoneService.get_zone(zone_slug)
    return zone_router.api.create_response(request, res, status=res.status_code)

@zone_router.get("/", response=StandardResponseDTO[PaginatedResponseSchema[ZoneOut]], summary="Get all zones (paginated)")
def get_all_zones(
    request: HttpRequest,
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100)
):
    res = ZoneService.get_all_zones(page=page, per_page=per_page)
    return zone_router.api.create_response(request, res, status=res.status_code)

@zone_router.put("/{zone_slug}/", response=StandardResponseDTO[ZoneOut], summary="Update a zone")
def update_zone(request: HttpRequest, zone_slug: str, payload: ZoneUpdateSchema):
    res = ZoneService.update_zone(zone_slug, **payload.dict(exclude_unset=True))
    return zone_router.api.create_response(request, res, status=res.status_code)

@zone_router.delete("/{zone_slug}/", response=StandardResponseDTO[None], summary="Delete a zone")
def delete_zone(request: HttpRequest, zone_slug: str):
    res = ZoneService.delete_zone(zone_slug)
    return zone_router.api.create_response(request, res, status=res.status_code)

# Official Endpoints
@official_router.post("/", response=StandardResponseDTO[OfficialOut], 
                    summary="Create a new official with optional profile image upload")
def create_official(
    request: HttpRequest,
    firstname: str = Form(...),
    lastname: str = Form(...),
    zone_name: str = Form(...),
    phone: str = Form(...),
    position: str = Form(...),
    official_type: str = Form(...),
    email: Optional[str] = Form(None),
    bio: Optional[str] = Form(None),
    profile_image: Optional[UploadedFile] = None,
    image_title: Optional[str] = Form(None, description="Title for the profile image"),
    image_alt_text: Optional[str] = Form(None, description="Alt text for the profile image"),
    image_caption: Optional[str] = Form(None, description="Caption for the profile image")
):
    """Create a new official with optional direct profile image upload"""
    
    # Validate image if provided
    if profile_image:
        allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
        if profile_image.content_type not in allowed_types:
            return official_router.api.create_response(
                request,
                StandardResponseDTO[OfficialOut](
                    data=None,
                    status_code=400,
                    success=False,
                    message=f"Unsupported image type. Allowed types: {', '.join(allowed_types)}"
                ),
                status=400
            )
        
        # Validate file size (5MB limit)
        max_size = 5 * 1024 * 1024  # 5MB
        if profile_image.size > max_size:
            return official_router.api.create_response(
                request,
                StandardResponseDTO[OfficialOut](
                    data=None,
                    status_code=400,
                    success=False,
                    message="Image size exceeds 5MB limit"
                ),
                status=400
            )
    
    res = OfficialService.create_official_with_image(
        firstname=firstname,
        lastname=lastname,
        zone_name=zone_name,
        phone=phone,
        position=position,
        official_type=official_type,
        email=email,
        bio=bio,
        profile_image=profile_image,
        image_title=image_title,
        image_alt_text=image_alt_text,
        image_caption=image_caption
    )
    return official_router.api.create_response(request, res, status=res.status_code)

@official_router.get("/", response=StandardResponseDTO[PaginatedResponseSchema[OfficialOut]], summary="Get all officials (paginated)")
def get_all_officials(
    request: HttpRequest,
    official_type: Optional[str] = Query(None),
    position: Optional[str] = Query(None),
    zone_slug: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100)
):
    res = OfficialService.get_filtered_officials(
        official_type=official_type,
        position=position,
        zone_slug=zone_slug,
        page=page,
        per_page=per_page
    )
    return official_router.api.create_response(request, res, status=res.status_code)

@official_router.get("/{official_id}/", response=StandardResponseDTO[OfficialOut], summary="Get an official by ID")
def get_official(request: HttpRequest, official_id: str):
    res = OfficialService.get_official(official_id)
    return official_router.api.create_response(request, res, status=res.status_code)

@official_router.put("/{official_id}/", response=StandardResponseDTO[OfficialOut], 
                    summary="Update an official with optional profile image replacement")
def update_official(
    request: HttpRequest,
    official_id: str,
    firstname: Optional[str] = Form(None),
    lastname: Optional[str] = Form(None),
    zone_name: Optional[str] = Form(None),
    phone: Optional[str] = Form(None),
    position: Optional[str] = Form(None),
    official_type: Optional[str] = Form(None),
    email: Optional[str] = Form(None),
    bio: Optional[str] = Form(None),
    profile_image: Optional[UploadedFile] = None,
    remove_image: bool = Form(False, description="Set to true to remove current profile image"),
    image_title: Optional[str] = Form(None, description="Title for the profile image"),
    image_alt_text: Optional[str] = Form(None, description="Alt text for the profile image"),
    image_caption: Optional[str] = Form(None, description="Caption for the profile image")
):
    """Update an official with optional profile image replacement"""
    
    # Validate image if provided
    if profile_image:
        allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
        if profile_image.content_type not in allowed_types:
            return official_router.api.create_response(
                request,
                StandardResponseDTO[OfficialOut](
                    data=None,
                    status_code=400,
                    success=False,
                    message=f"Unsupported image type. Allowed types: {', '.join(allowed_types)}"
                ),
                status=400
            )
        
        # Validate file size (5MB limit)
        max_size = 5 * 1024 * 1024  # 5MB
        if profile_image.size > max_size:
            return official_router.api.create_response(
                request,
                StandardResponseDTO[OfficialOut](
                    data=None,
                    status_code=400,
                    success=False,
                    message="Image size exceeds 5MB limit"
                ),
                status=400
            )
    
    res = OfficialService.update_official_with_image(
        official_id=official_id,
        firstname=firstname,
        lastname=lastname,
        zone_name=zone_name,
        phone=phone,
        position=position,
        official_type=official_type,
        email=email,
        bio=bio,
        profile_image=profile_image,
        remove_image=remove_image,
        image_title=image_title,
        image_alt_text=image_alt_text,
        image_caption=image_caption
    )
    return official_router.api.create_response(request, res, status=res.status_code)

@official_router.delete("/{official_id}/", response=StandardResponseDTO[None], summary="Delete an official")
def delete_official(request: HttpRequest, official_id: str):
    res = OfficialService.delete_official(official_id)
    return official_router.api.create_response(request, res, status=res.status_code)


# Contact Endpoints
@contact_router.post("/", response=StandardResponseDTO[ContactSubmissionOut], summary="Submit a contact form")
def submit_contact_form(request: HttpRequest, payload: ContactSubmissionCreateSchema):
    """Submit a contact form with name, email, subject, and message"""
    try:
        # Additional input validation at view level
        payload_dict = payload.dict()
        
        # Trim whitespace from string fields
        payload_dict['name'] = payload_dict['name'].strip()
        payload_dict['message'] = payload_dict['message'].strip()
        payload_dict['email'] = payload_dict['email'].strip().lower()
        
        if payload_dict.get('phone'):
            payload_dict['phone'] = payload_dict['phone'].strip()
        
        # Basic length validation
        if len(payload_dict['name']) < 2:
            return contact_router.api.create_response(
                request, 
                StandardResponseDTO[ContactSubmissionOut](
                    data=None,
                    status_code=HTTPStatusCode.BAD_REQUEST,
                    success=False,
                    message="Name must be at least 2 characters long"
                ), 
                status=400
            )
        
        if len(payload_dict['message']) < 10:
            return contact_router.api.create_response(
                request,
                StandardResponseDTO[ContactSubmissionOut](
                    data=None,
                    status_code=HTTPStatusCode.BAD_REQUEST,
                    success=False,
                    message="Message must be at least 10 characters long"
                ),
                status=400
            )
        
        res = ContactService.create_contact_submission(**payload_dict)
        return contact_router.api.create_response(request, res, status=res.status_code)
        
    except Exception as e:
        return contact_router.api.create_response(
            request,
            StandardResponseDTO[ContactSubmissionOut](
                data=None,
                status_code=HTTPStatusCode.BAD_REQUEST,
                success=False,
                message=f"Invalid input: {str(e)}"
            ),
            status=400
        )

@contact_router.get("/", response=StandardResponseDTO[PaginatedResponseSchema[ContactSubmissionOut]], summary="Get all contact submissions (Admin only)")
def get_contact_submissions(
    request: HttpRequest,
    page: int = Query(1, ge=1, le=1000),  # Add reasonable upper limit
    per_page: int = Query(10, ge=1, le=100),  # Cap at 100 items per page
    email: Optional[str] = Query(None, description="Filter by email (partial match)", max_length=254),
    subject: Optional[str] = Query(None, description="Filter by subject (exact match)", max_length=20)
):
    """Get all contact submissions with pagination and optional filtering (typically for admin use)"""
    # Additional validation for query parameters
    if email and len(email.strip()) == 0:
        email = None
    if subject and len(subject.strip()) == 0:
        subject = None
        
    res = ContactService.get_all_contact_submissions(
        page=page, 
        per_page=per_page, 
        email=email, 
        subject=subject
    )
    return contact_router.api.create_response(request, res, status=res.status_code)

@contact_router.get("/subjects/", response=StandardResponseDTO[List[dict]], summary="Get available contact subjects")
def get_contact_subjects(request: HttpRequest):
    """Get all available subject choices for contact forms"""
    res = ContactService.get_subject_choices()
    return contact_router.api.create_response(request, res, status=res.status_code)


# Newsletter Endpoints
@newsletter_router.post("/subscribe/", response=StandardResponseDTO[NewsletterSubscriberOut], summary="Subscribe to newsletter")
def subscribe_newsletter(request: HttpRequest, payload: NewsletterSubscribeSchema):
    """Subscribe to the newsletter with email address"""
    res = NewsletterService.subscribe_newsletter(payload.email)
    return newsletter_router.api.create_response(request, res, status=res.status_code)

@newsletter_router.post("/unsubscribe/", response=StandardResponseDTO[None], summary="Unsubscribe from newsletter")
def unsubscribe_newsletter(request: HttpRequest, payload: NewsletterUnsubscribeSchema):
    """Unsubscribe from the newsletter"""
    res = NewsletterService.unsubscribe_newsletter(payload.email)
    return newsletter_router.api.create_response(request, res, status=res.status_code)

@newsletter_router.get("/subscribers/", response=StandardResponseDTO[PaginatedResponseSchema[NewsletterSubscriberOut]], summary="Get all newsletter subscribers (Admin only)")
def get_newsletter_subscribers(
    request: HttpRequest,
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    active_only: bool = Query(True, description="Filter only active subscribers")
):
    """Get all newsletter subscribers with pagination (typically for admin use)"""
    res = NewsletterService.get_all_subscribers(page=page, per_page=per_page, active_only=active_only)
    return newsletter_router.api.create_response(request, res, status=res.status_code)