from ninja import Router, Form, Query
from ninja.files import UploadedFile
from typing import List, Optional
from uuid import UUID
from django.http import HttpRequest
from .schemas import (
    StandardResponseDTO,
    TYMAImageOut,
    TYMAImageCreateSchema,
    TYMAImageUpdateSchema,
    PaginatedResponseSchema
)
from .image_services import ImageService

image_router = Router(tags=["Images"])


@image_router.post("/upload/", response=StandardResponseDTO[TYMAImageOut], 
                  summary="Upload a new image")
def upload_image(
    request: HttpRequest,
    file: UploadedFile,
    title: str = Form(None),
    alt_text: str = Form(None),
    caption: str = Form(None),
    image_type: str = Form('OTHER'),
    content_type_id: int = Form(None)
):
    """Upload a new image to TYMA Image storage"""
    # Validate file type
    allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
    if file.content_type not in allowed_types:
        return image_router.api.create_response(
            request,
            StandardResponseDTO[TYMAImageOut](
                data=None,
                status_code=400,
                success=False,
                message=f"Unsupported file type. Allowed types: {', '.join(allowed_types)}"
            ),
            status=400
        )
    
    # Validate file size (5MB limit)
    max_size = 5 * 1024 * 1024  # 5MB
    if file.size > max_size:
        return image_router.api.create_response(
            request,
            StandardResponseDTO[TYMAImageOut](
                data=None,
                status_code=400,
                success=False,
                message="File size exceeds 5MB limit"
            ),
            status=400
        )
    
    res = ImageService.create_image(
        image_file=file,
        title=title,
        alt_text=alt_text,
        caption=caption,
        image_type=image_type,
        content_type_id=content_type_id
    )
    return image_router.api.create_response(request, res, status=res.status_code)


@image_router.get("/", response=StandardResponseDTO[PaginatedResponseSchema[TYMAImageOut]], 
                 summary="Get all images with optional filters (paginated)")
def get_all_images(
    request: HttpRequest,
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    image_type: Optional[str] = Query(None, description="Filter by image type"),
    content_type: Optional[str] = Query(None, description="Filter by content type"),
    object_id: Optional[str] = Query(None, description="Filter by object ID")
):
    """Get all images with optional filters"""
    res = ImageService.get_all_images(
        page=page,
        per_page=per_page,
        image_type=image_type,
        content_type=content_type,
        object_id=object_id
    )
    return image_router.api.create_response(request, res, status=res.status_code)


@image_router.get("/{image_id}/", response=StandardResponseDTO[TYMAImageOut], 
                 summary="Get an image by ID")
def get_image(request: HttpRequest, image_id: str):
    """Get a single image by ID"""
    res = ImageService.get_image(image_id)
    return image_router.api.create_response(request, res, status=res.status_code)


@image_router.put("/{image_id}/", response=StandardResponseDTO[TYMAImageOut], 
                 summary="Update an image")
def update_image(request: HttpRequest, image_id: str, payload: TYMAImageUpdateSchema):
    """Update an existing image's metadata"""
    res = ImageService.update_image(
        image_id=image_id,
        **payload.dict(exclude_unset=True)
    )
    return image_router.api.create_response(request, res, status=res.status_code)


@image_router.delete("/{image_id}/", response=StandardResponseDTO[None], 
                    summary="Delete an image")
def delete_image(request: HttpRequest, image_id: str):
    """Delete an image"""
    res = ImageService.delete_image(image_id)
    return image_router.api.create_response(request, res, status=res.status_code)


@image_router.post("/{image_id}/link/", response=StandardResponseDTO[TYMAImageOut], 
                  summary="Link an image to an object")
def link_image_to_object(
    request: HttpRequest,
    image_id: str,
    content_type_id: int = Form(...),
    object_id: str = Form(...)
):
    """Link an existing image to a model instance"""
    res = ImageService.link_image_to_object(
        image_id=image_id,
        content_type_id=content_type_id,
        object_id=object_id
    )
    return image_router.api.create_response(request, res, status=res.status_code)


@image_router.get("/for-object/", response=StandardResponseDTO[List[TYMAImageOut]], 
                 summary="Get all images for a specific object")
def get_images_for_object(
    request: HttpRequest,
    content_type: str = Query(..., description="Model name (e.g., 'official', 'newsevent')"),
    object_id: str = Query(..., description="Object ID"),
    image_type: Optional[str] = Query(None, description="Filter by image type")
):
    """Get all images linked to a specific object"""
    res = ImageService.get_images_for_object(
        content_type=content_type,
        object_id=object_id,
        image_type=image_type
    )
    return image_router.api.create_response(request, res, status=res.status_code)
