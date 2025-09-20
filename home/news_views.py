from ninja import Router, Query, Form, File
from ninja.files import UploadedFile
from typing import List, Optional
from uuid import UUID
from django.http import HttpRequest
from datetime import datetime
from .schemas import (
    StandardResponseDTO,
    NewsOut,
    NewsCategoryOut,
    NewsCreateSchema,
    NewsUpdateSchema,
    NewsCategoryCreateSchema,
    PaginatedResponseSchema
)
from .news_services import NewsService, NewsCategoryService

news_router = Router(tags=["News"])
category_router = Router(tags=["News Categories"])


# News Category Endpoints
@category_router.post("/", response=StandardResponseDTO[NewsCategoryOut], 
                     summary="Create a new news category")
def create_category(request: HttpRequest, payload: NewsCategoryCreateSchema):
    res = NewsCategoryService.create_category(**payload.dict())
    return category_router.api.create_response(request, res, status=res.status_code)

@category_router.get("/", response=StandardResponseDTO[PaginatedResponseSchema[NewsCategoryOut]], 
                    summary="Get all news categories (paginated)")
def get_all_categories(
    request: HttpRequest,
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100)
):
    res = NewsCategoryService.get_all_categories(page=page, per_page=per_page)
    return category_router.api.create_response(request, res, status=res.status_code)

@category_router.get("/{slug}/", response=StandardResponseDTO[NewsCategoryOut], 
                    summary="Get a news category by slug")
def get_category(request: HttpRequest, slug: str):
    res = NewsCategoryService.get_category_by_slug(slug)
    return category_router.api.create_response(request, res, status=res.status_code)

@category_router.put("/{slug}/", response=StandardResponseDTO[NewsCategoryOut], 
                    summary="Update a news category")
def update_category(request: HttpRequest, slug: str, payload: NewsCategoryCreateSchema):
    res = NewsCategoryService.update_category(slug, **payload.dict(exclude_unset=True))
    return category_router.api.create_response(request, res, status=res.status_code)

@category_router.delete("/{slug}/", response=StandardResponseDTO[None], 
                       summary="Delete a news category")
def delete_category(request: HttpRequest, slug: str):
    res = NewsCategoryService.delete_category(slug)
    return category_router.api.create_response(request, res, status=res.status_code)


# News Endpoints
@news_router.post("/", response=StandardResponseDTO[NewsOut], 
                 summary="Create a new news article or event with optional image upload")
def create_news(
    request: HttpRequest,
    title: str = Form(...),
    news_type: str = Form(...),
    short_description: str = Form(...),
    content: str = Form(...),
    author_id: str = Form(...),
    category_slugs: Optional[str] = Form(None, description="Comma-separated category slugs"),
    is_featured: bool = Form(False),
    event_date: Optional[datetime] = Form(None),
    event_location: Optional[str] = Form(None),
    featured_image: Optional[UploadedFile] = File(None),
    image_title: Optional[str] = Form(None, description="Title for the uploaded image"),
    image_alt_text: Optional[str] = Form(None, description="Alt text for the uploaded image"),
    image_caption: Optional[str] = Form(None, description="Caption for the uploaded image")
):
    """Create a new news article or event with optional direct image upload"""
    
    # Validate image if provided
    if featured_image:
        allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
        if featured_image.content_type not in allowed_types:
            return news_router.api.create_response(
                request,
                StandardResponseDTO[NewsOut](
                    data=None,
                    status_code=400,
                    success=False,
                    message=f"Unsupported image type. Allowed types: {', '.join(allowed_types)}"
                ),
                status=400
            )
        
        # Validate file size (5MB limit)
        max_size = 5 * 1024 * 1024  # 5MB
        if featured_image.size > max_size:
            return news_router.api.create_response(
                request,
                StandardResponseDTO[NewsOut](
                    data=None,
                    status_code=400,
                    success=False,
                    message="Image size exceeds 5MB limit"
                ),
                status=400
            )
    
    # Parse category slugs
    parsed_category_slugs = None
    if category_slugs:
        parsed_category_slugs = [slug.strip() for slug in category_slugs.split(',') if slug.strip()]
    
    res = NewsService.create_news_with_image(
        title=title,
        news_type=news_type,
        short_description=short_description,
        content=content,
        author_id=author_id,
        category_slugs=parsed_category_slugs,
        is_featured=is_featured,
        event_date=event_date,
        event_location=event_location,
        featured_image=featured_image,
        image_title=image_title,
        image_alt_text=image_alt_text,
        image_caption=image_caption
    )
    return news_router.api.create_response(request, res, status=res.status_code)

@news_router.get("/", response=StandardResponseDTO[PaginatedResponseSchema[NewsOut]], 
                summary="Get all news with advanced filters (paginated)")
def get_all_news(
    request: HttpRequest,
    search: Optional[str] = Query(None, description="Search in title/content"),
    news_type: Optional[str] = Query(None, description="Filter by news type (article/event)"),
    category_slug: Optional[str] = Query(None, description="Filter by category slug"),
    is_featured: Optional[bool] = Query(None, description="Filter by featured status"),
    author_id: Optional[str] = Query(None, description="Filter by author's official ID"),
    year: Optional[int] = Query(None, description="Filter by publication year"),
    month: Optional[int] = Query(None, description="Filter by publication month (1-12)"),
    start_date: Optional[datetime] = Query(None, description="Filter news published after this date"),
    end_date: Optional[datetime] = Query(None, description="Filter news published before this date"),
    latest: Optional[bool] = Query(None, description="Get only latest news (ignores pagination)"),
    sort_by: str = Query("-published_at", description="Sort field (- for descending)"),
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100)
):
    res = NewsService.get_filtered_news(
        search=search,
        news_type=news_type,
        category_slug=category_slug,
        is_featured=is_featured,
        author_id=author_id,
        year=year,
        month=month,
        start_date=start_date,
        end_date=end_date,
        latest_news=latest,
        sort_by=sort_by,
        page=page,
        per_page=per_page
    )
    return news_router.api.create_response(request, res, status=res.status_code)

@news_router.get("/{slug}/", response=StandardResponseDTO[NewsOut], 
                summary="Get a news item by slug")
def get_news(request: HttpRequest, slug: str):
    res = NewsService.get_news_by_slug(slug)
    return news_router.api.create_response(request, res, status=res.status_code)

@news_router.put("/{slug}/", response=StandardResponseDTO[NewsOut], 
                summary="Update a news item with optional image replacement")
def update_news(
    request: HttpRequest,
    slug: str,
    title: Optional[str] = Form(None),
    news_type: Optional[str] = Form(None),
    short_description: Optional[str] = Form(None),
    content: Optional[str] = Form(None),
    author_id: Optional[str] = Form(None),
    category_slugs: Optional[str] = Form(None, description="Comma-separated category slugs"),
    is_featured: Optional[bool] = Form(None),
    event_date: Optional[datetime] = Form(None),
    event_location: Optional[str] = Form(None),
    featured_image: Optional[UploadedFile] = None,
    remove_image: bool = Form(False, description="Set to true to remove current image"),
    image_title: Optional[str] = Form(None, description="Title for the uploaded image"),
    image_alt_text: Optional[str] = Form(None, description="Alt text for the uploaded image"),
    image_caption: Optional[str] = Form(None, description="Caption for the uploaded image")
):
    """Update a news article or event with optional image replacement"""
    
    # Validate image if provided
    if featured_image:
        allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
        if featured_image.content_type not in allowed_types:
            return news_router.api.create_response(
                request,
                StandardResponseDTO[NewsOut](
                    data=None,
                    status_code=400,
                    success=False,
                    message=f"Unsupported image type. Allowed types: {', '.join(allowed_types)}"
                ),
                status=400
            )
        
        # Validate file size (5MB limit)
        max_size = 5 * 1024 * 1024  # 5MB
        if featured_image.size > max_size:
            return news_router.api.create_response(
                request,
                StandardResponseDTO[NewsOut](
                    data=None,
                    status_code=400,
                    success=False,
                    message="Image size exceeds 5MB limit"
                ),
                status=400
            )
    
    # Parse category slugs
    parsed_category_slugs = None
    if category_slugs:
        parsed_category_slugs = [slug.strip() for slug in category_slugs.split(',') if slug.strip()]
    
    res = NewsService.update_news_with_image(
        slug=slug,
        title=title,
        news_type=news_type,
        short_description=short_description,
        content=content,
        author_id=author_id,
        category_slugs=parsed_category_slugs,
        is_featured=is_featured,
        event_date=event_date,
        event_location=event_location,
        featured_image=featured_image,
        remove_image=remove_image,
        image_title=image_title,
        image_alt_text=image_alt_text,
        image_caption=image_caption
    )
    return news_router.api.create_response(request, res, status=res.status_code)

@news_router.delete("/{slug}/", response=StandardResponseDTO[None], 
                   summary="Delete a news item")
def delete_news(request: HttpRequest, slug: str):
    res = NewsService.delete_news(slug)
    return news_router.api.create_response(request, res, status=res.status_code)