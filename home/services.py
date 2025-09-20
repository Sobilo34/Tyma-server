from typing import Optional, List, Union
from uuid import UUID
from django.db.models import QuerySet
from django.contrib.contenttypes.models import ContentType
from django.core.files.uploadedfile import InMemoryUploadedFile, TemporaryUploadedFile
import traceback
from .models import Official, Zone, ContactSubmission, NewsletterSubscriber, TYMAImage
from .schemas import (
    HTTPStatusCode,
    StandardResponseDTO,
    OfficialOut,
    ZoneOut,
    PaginatedResponseSchema,
    OfficialCreateSchema,
    OfficialUpdateSchema,
    ZoneCreateSchema,
    ZoneUpdateSchema,
    ContactSubmissionOut,
    NewsletterSubscriberOut,
    TYMAImageOut
    
)
from django.core.exceptions import ObjectDoesNotExist
from .utils import generate_user_id, generate_zone_id


def create_detailed_error_response(exception: Exception, operation: str) -> str:
    """Create detailed error message with traceback for debugging"""
    error_details = f"Error during {operation}: {str(exception)}"
    if hasattr(exception, '__traceback__'):
        error_details += f"\nTraceback: {traceback.format_exc()}"
    return error_details


class ZoneService:
    @staticmethod
    def _zone_to_schema(zone: Zone) -> ZoneOut:
        """Convert Zone model instance to ZoneOut schema"""
        return ZoneOut(
            id=zone.id,
            name=zone.name,
            slug=zone.slug,
            description=zone.description,
            created_at=zone.created_at,
            updated_at=zone.updated_at
        )

    @staticmethod
    def _get_paginated_response(
        queryset: QuerySet,
        page: int,
        per_page: int,
        schema_converter
    ) -> PaginatedResponseSchema:
        """Generic pagination helper with error handling"""
        try:
            # Ensure page and per_page are positive
            page = max(1, page)
            per_page = max(1, min(per_page, 100))  # Cap at 100 items per page
            
            offset = (page - 1) * per_page
            total = queryset.count()
            
            # Check if page number is valid
            if offset >= total and total > 0:
                # Return last valid page instead of empty result
                last_page = (total - 1) // per_page + 1
                offset = (last_page - 1) * per_page
                page = last_page
            
            items = queryset[offset:offset + per_page]
            return PaginatedResponseSchema(
                items=[schema_converter(item) for item in items],
                total=total,
                page=page,
                per_page=per_page
            )
        except Exception as e:
            # Return empty pagination result on error
            return PaginatedResponseSchema(
                items=[],
                total=0,
                page=1,
                per_page=per_page
            )

    @staticmethod
    def create_zone(
        name: str,
        description: str = None
    ) -> StandardResponseDTO[ZoneOut]:
        """Create a new zone"""
        try:
            if Zone.objects.filter(name__iexact=name).exists():
                return StandardResponseDTO[ZoneOut](
                    data=None,
                    status_code=HTTPStatusCode.CONFLICT,
                    success=False,
                    message=f"Zone '{name}' already exists"
                )
                
            zone = Zone.objects.create(
                name=name.title(),
                description=description,
                slug=generate_zone_id(name)
            )
            
            return StandardResponseDTO[ZoneOut](
                data=ZoneService._zone_to_schema(zone),
                status_code=HTTPStatusCode.CREATED,
                message="Zone created successfully"
            )
        except Exception as e:
            return StandardResponseDTO[ZoneOut](
                data=None,
                status_code=HTTPStatusCode.BAD_REQUEST,
                success=False,
                message=str(e)
            )

    @staticmethod
    def get_zone(slug: str) -> StandardResponseDTO[ZoneOut]:
        """Get a single zone by slug"""
        try:
            zone = Zone.objects.get(slug=slug)
            return StandardResponseDTO[ZoneOut](
                data=ZoneService._zone_to_schema(zone),
                status_code=HTTPStatusCode.OK,
                message="Zone retrieved successfully"
            )
        except Zone.DoesNotExist:
            return StandardResponseDTO[ZoneOut](
                data=None,
                status_code=HTTPStatusCode.NOT_FOUND,
                success=False,
                message=f"Zone with slug '{slug}' not found"
            )
        except Exception as e:
            return StandardResponseDTO[ZoneOut](
                data=None,
                status_code=HTTPStatusCode.INTERNAL_SERVER_ERROR,
                success=False,
                message=str(e)
            )

    @staticmethod
    def get_all_zones(
        page: int = 1,
        per_page: int = 10
    ) -> StandardResponseDTO[PaginatedResponseSchema[ZoneOut]]:
        """Get paginated list of all zones"""
        try:
            queryset = Zone.objects.all().order_by('name')
            paginated_data = ZoneService._get_paginated_response(
                queryset,
                page,
                per_page,
                ZoneService._zone_to_schema
            )
            return StandardResponseDTO[PaginatedResponseSchema[ZoneOut]](
                data=paginated_data,
                status_code=HTTPStatusCode.OK,
                message="Zones retrieved successfully"
            )
        except Exception as e:
            return StandardResponseDTO[PaginatedResponseSchema[ZoneOut]](
                data=None,
                status_code=HTTPStatusCode.INTERNAL_SERVER_ERROR,
                success=False,
                message=str(e)
            )

    @staticmethod
    def update_zone(
        slug: str,
        name: str = None,
        description: str = None
    ) -> StandardResponseDTO[ZoneOut]:
        """Update an existing zone"""
        try:
            zone = Zone.objects.get(slug=slug)
            
            if name:
                if Zone.objects.filter(name__iexact=name).exclude(slug=slug).exists():
                    return StandardResponseDTO[ZoneOut](
                        data=None,
                        status_code=HTTPStatusCode.CONFLICT,
                        success=False,
                        message=f"Zone name '{name}' already exists"
                    )
                zone.name = name.title()
                
            if description is not None:
                zone.description = description
                
            zone.save()
            return StandardResponseDTO[ZoneOut](
                data=ZoneService._zone_to_schema(zone),
                status_code=HTTPStatusCode.OK,
                message="Zone updated successfully"
            )
        except Zone.DoesNotExist:
            return StandardResponseDTO[ZoneOut](
                data=None,
                status_code=HTTPStatusCode.NOT_FOUND,
                success=False,
                message=f"Zone with slug '{slug}' not found"
            )
        except Exception as e:
            return StandardResponseDTO[ZoneOut](
                data=None,
                status_code=HTTPStatusCode.BAD_REQUEST,
                success=False,
                message=str(e)
            )

    @staticmethod
    def delete_zone(slug: str) -> StandardResponseDTO[None]:
        """Delete a zone by slug"""
        try:
            zone = Zone.objects.get(slug=slug)
            
            if zone.officials.exists():
                return StandardResponseDTO[None](
                    status_code=HTTPStatusCode.CONFLICT,
                    success=False,
                    message="Cannot delete zone with associated officials"
                )
                
            zone.delete()
            return StandardResponseDTO[None](
                status_code=HTTPStatusCode.OK,
                message="Zone deleted successfully"
            )
        except Zone.DoesNotExist:
            return StandardResponseDTO[None](
                status_code=HTTPStatusCode.NOT_FOUND,
                success=False,
                message="Zone not found"
            )
        except Exception as e:
            return StandardResponseDTO[None](
                status_code=HTTPStatusCode.INTERNAL_SERVER_ERROR,
                success=False,
                message=str(e)
            )


class OfficialService:
    @staticmethod
    def _official_to_schema(official: Official) -> OfficialOut:
        """Convert Official model instance to OfficialOut schema"""
        return OfficialOut(
            id=official.id,
            zone=ZoneOut(
                id=official.zone.id,
                name=official.zone.name,
                slug=official.zone.slug,
                description=official.zone.description,
                created_at=official.zone.created_at,
                updated_at=official.zone.updated_at
            ),
            name=official.name,
            official_id=official.official_id,
            phone=official.phone,
            email=official.email,
            position=official.position,
            official_type=official.official_type,
            bio=official.bio,
            profile_image=TYMAImageOut(
                id=official.profile_image.id,
                title=official.profile_image.title,
                url=official.profile_image.get_image_url(),
                alt_text=official.profile_image.alt_text,
                caption=official.profile_image.caption,
                image_type=official.profile_image.image_type,
                content_type=official.profile_image.content_type.model if official.profile_image.content_type else None,
                object_id=str(official.profile_image.object_id) if official.profile_image.object_id else None,
                created_at=official.profile_image.created_at,
                updated_at=official.profile_image.updated_at
            ) if official.profile_image else None,
            is_active=official.is_active,
            order=official.order,
            start_date=official.start_date,
            end_date=official.end_date,
            created_at=official.created_at,
            updated_at=official.updated_at
        )

    @staticmethod
    def create_official(
        firstname: str,
        lastname: str,
        zone_name: str,
        phone: str,
        position: str,
        official_type: str,
        email: str = None,
        bio: str = None,
        profile_image_id: str = None
    ) -> StandardResponseDTO[OfficialOut]:
        """Create a new official"""
        try:
            zone = Zone.objects.get(name__iexact=zone_name.title())
            
            existing_official = Official.objects.filter(
                name__iexact=f"{firstname} {lastname}",
                email__iexact=email if email else None
            ).first()
            
            if existing_official:
                return StandardResponseDTO[OfficialOut](
                    data=None,
                    status_code=HTTPStatusCode.CONFLICT,
                    success=False,
                    message=f"Official '{firstname} {lastname}' with email '{email}' already exists"
                )
            
            # Get profile image if provided
            profile_image_instance = None
            if profile_image_id:
                try:
                    profile_image_instance = TYMAImage.objects.get(id=UUID(profile_image_id))
                    # Link the image to the official (we'll update this after creating the official)
                except (ValueError, TYMAImage.DoesNotExist):
                    return StandardResponseDTO[OfficialOut](
                        data=None,
                        status_code=HTTPStatusCode.NOT_FOUND,
                        success=False,
                        message="Profile image not found"
                    )
                
            official = Official.objects.create(
                name=f"{firstname} {lastname}",
                zone=zone,
                phone=phone,
                position=position,
                official_id=generate_user_id(firstname, lastname),
                official_type=official_type,
                email=email,
                bio=bio,
                profile_image=profile_image_instance
            )
            
            # Update the image's generic foreign key to link it to this official
            if profile_image_instance:
                from django.contrib.contenttypes.models import ContentType
                official_ct = ContentType.objects.get_for_model(Official)
                profile_image_instance.content_type = official_ct
                profile_image_instance.object_id = official.id
                profile_image_instance.image_type = 'PROFILE'
                profile_image_instance.save()
            
            return StandardResponseDTO[OfficialOut](
                data=OfficialService._official_to_schema(official),
                status_code=HTTPStatusCode.CREATED,
                message="Official created successfully"
            )
        except Zone.DoesNotExist:
            return StandardResponseDTO[OfficialOut](
                data=None,
                status_code=HTTPStatusCode.NOT_FOUND,
                success=False,
                message=f"Zone '{zone_name}' not found"
            )
        except Exception as e:
            return StandardResponseDTO[OfficialOut](
                data=None,
                status_code=HTTPStatusCode.BAD_REQUEST,
                success=False,
                message=str(e)
            )

    @staticmethod
    def create_official_with_image(
        firstname: str,
        lastname: str,
        zone_name: str,
        phone: str,
        position: str,
        official_type: str,
        email: str = None,
        bio: str = None,
        profile_image: Optional[Union[InMemoryUploadedFile, TemporaryUploadedFile]] = None,
        image_title: Optional[str] = None,
        image_alt_text: Optional[str] = None,
        image_caption: Optional[str] = None
    ) -> StandardResponseDTO[OfficialOut]:
        """Create a new official with direct image upload"""
        try:
            zone = Zone.objects.get(name__iexact=zone_name.title())
            
            existing_official = Official.objects.filter(
                name__iexact=f"{firstname} {lastname}",
                email__iexact=email if email else None
            ).first()
            
            if existing_official:
                return StandardResponseDTO[OfficialOut](
                    data=None,
                    status_code=HTTPStatusCode.CONFLICT,
                    success=False,
                    message=f"Official '{firstname} {lastname}' with email '{email}' already exists"
                )
            
            # Create profile image if provided
            profile_image_instance = None
            if profile_image:
                try:
                    # Create the TYMA image first
                    image = TYMAImage.objects.create(
                        title=image_title or f"Profile image for {firstname} {lastname}",
                        image=profile_image,
                        alt_text=image_alt_text or f"Profile image of {firstname} {lastname}",
                        caption=image_caption or "",
                        image_type='PROFILE'
                    )
                    profile_image_instance = image
                except Exception as e:
                    return StandardResponseDTO[OfficialOut](
                        data=None,
                        status_code=HTTPStatusCode.BAD_REQUEST,
                        success=False,
                        message=f"Error uploading profile image: {str(e)}"
                    )
                
            official = Official.objects.create(
                name=f"{firstname} {lastname}",
                zone=zone,
                phone=phone,
                position=position,
                official_id=generate_user_id(firstname, lastname),
                official_type=official_type,
                email=email,
                bio=bio,
                profile_image=profile_image_instance
            )
            
            # Link the image to the official using generic foreign key
            if profile_image_instance:
                official_ct = ContentType.objects.get_for_model(Official)
                profile_image_instance.content_type = official_ct
                profile_image_instance.object_id = official.id
                profile_image_instance.save()
            
            return StandardResponseDTO[OfficialOut](
                data=OfficialService._official_to_schema(official),
                status_code=HTTPStatusCode.CREATED,
                message="Official created successfully with profile image"
            )
        except Zone.DoesNotExist:
            return StandardResponseDTO[OfficialOut](
                data=None,
                status_code=HTTPStatusCode.NOT_FOUND,
                success=False,
                message=f"Zone '{zone_name}' not found"
            )
        except Exception as e:
            return StandardResponseDTO[OfficialOut](
                data=None,
                status_code=HTTPStatusCode.BAD_REQUEST,
                success=False,
                message=str(e)
            )

    @staticmethod
    def get_official(official_id: str) -> StandardResponseDTO[OfficialOut]:
        """Get a single official by ID"""
        try:
            official = Official.objects.get(official_id=official_id)
            return StandardResponseDTO[OfficialOut](
                data=OfficialService._official_to_schema(official),
                status_code=HTTPStatusCode.OK,
                success=True,
                message="Official retrieved successfully"
            )
        except Official.DoesNotExist:
            return StandardResponseDTO[OfficialOut](
                data=None,
                status_code=HTTPStatusCode.NOT_FOUND,
                success=False,
                message=f"Official with ID '{official_id}' not found"
            )
        except Exception as e:
            return StandardResponseDTO[OfficialOut](
                data=None,
                status_code=HTTPStatusCode.INTERNAL_SERVER_ERROR,
                success=False,
                message=f"Error retrieving official: {str(e)}"
            )

    @staticmethod
    def get_filtered_officials(
        official_type: Optional[str] = None,
        position: Optional[str] = None,
        zone_slug: Optional[str] = None,
        page: int = 1,
        per_page: int = 10
    ) -> StandardResponseDTO[PaginatedResponseSchema[OfficialOut]]:
        """Get paginated list of officials with optional filters"""
        try:
            queryset = Official.objects.all().order_by('order')
            
            if official_type:
                queryset = queryset.filter(official_type__iexact=official_type)
            if position:
                queryset = queryset.filter(position__iexact=position)
            if zone_slug:
                queryset = queryset.filter(zone__slug=zone_slug)
            
            paginated_data = ZoneService._get_paginated_response(
                queryset,
                page,
                per_page,
                OfficialService._official_to_schema
            )
            return StandardResponseDTO[PaginatedResponseSchema[OfficialOut]](
                data=paginated_data,
                status_code=HTTPStatusCode.OK,
                message="Officials retrieved successfully"
            )
        except Exception as e:
            return StandardResponseDTO[PaginatedResponseSchema[OfficialOut]](
                data=None,
                status_code=HTTPStatusCode.INTERNAL_SERVER_ERROR,
                success=False,
                message=str(e)
            )

    @staticmethod
    def update_official(
        official_id: str,
        **kwargs
    ) -> StandardResponseDTO[OfficialOut]:
        """Update an existing official"""
        try:
            official = Official.objects.get(official_id=official_id)
            
            if 'firstname' in kwargs or 'lastname' in kwargs:
                firstname = kwargs.pop('firstname', official.name.split()[0])
                lastname = kwargs.pop('lastname', official.name.split()[-1])
                official.name = f"{firstname} {lastname}"
            
            if 'zone_name' in kwargs:
                zone = Zone.objects.get(name__iexact=kwargs.pop('zone_name'))
                official.zone = zone
            
            # Handle profile image update
            if 'profile_image_id' in kwargs:
                profile_image_id = kwargs.pop('profile_image_id')
                if profile_image_id:
                    try:
                        profile_image_instance = TYMAImage.objects.get(id=UUID(profile_image_id))
                        # Update the old image's generic foreign key if it exists
                        if official.profile_image:
                            official.profile_image.content_type = None
                            official.profile_image.object_id = None
                            official.profile_image.save()
                        
                        # Link new image to official
                        from django.contrib.contenttypes.models import ContentType
                        official_ct = ContentType.objects.get_for_model(Official)
                        profile_image_instance.content_type = official_ct
                        profile_image_instance.object_id = official.id
                        profile_image_instance.image_type = 'PROFILE'
                        profile_image_instance.save()
                        
                        official.profile_image = profile_image_instance
                    except (ValueError, TYMAImage.DoesNotExist):
                        return StandardResponseDTO[OfficialOut](
                            data=None,
                            status_code=HTTPStatusCode.NOT_FOUND,
                            success=False,
                            message="Profile image not found"
                        )
                else:
                    # Remove current profile image link
                    if official.profile_image:
                        official.profile_image.content_type = None
                        official.profile_image.object_id = None
                        official.profile_image.save()
                    official.profile_image = None
                
            for key, value in kwargs.items():
                if value is not None and hasattr(official, key):
                    setattr(official, key, value)
            
            official.save()
            return StandardResponseDTO[OfficialOut](
                data=OfficialService._official_to_schema(official),
                status_code=HTTPStatusCode.OK,
                message="Official updated successfully"
            )
        except Official.DoesNotExist:
            return StandardResponseDTO[OfficialOut](
                data=None,
                status_code=HTTPStatusCode.NOT_FOUND,
                success=False,
                message=f"Official with ID '{official_id}' not found"
            )
        except Zone.DoesNotExist:
            return StandardResponseDTO[OfficialOut](
                data=None,
                status_code=HTTPStatusCode.NOT_FOUND,
                success=False,
                message="Zone not found"
            )
        except Exception as e:
            return StandardResponseDTO[OfficialOut](
                data=None,
                status_code=HTTPStatusCode.BAD_REQUEST,
                success=False,
                message=str(e)
            )

    @staticmethod
    def update_official_with_image(
        official_id: str,
        firstname: Optional[str] = None,
        lastname: Optional[str] = None,
        zone_name: Optional[str] = None,
        phone: Optional[str] = None,
        position: Optional[str] = None,
        official_type: Optional[str] = None,
        email: Optional[str] = None,
        bio: Optional[str] = None,
        profile_image: Optional[Union[InMemoryUploadedFile, TemporaryUploadedFile]] = None,
        remove_image: bool = False,
        image_title: Optional[str] = None,
        image_alt_text: Optional[str] = None,
        image_caption: Optional[str] = None
    ) -> StandardResponseDTO[OfficialOut]:
        """Update an existing official with image replacement"""
        try:
            official = Official.objects.get(official_id=official_id)
            
            if firstname is not None or lastname is not None:
                fname = firstname if firstname is not None else official.name.split()[0]
                lname = lastname if lastname is not None else official.name.split()[-1]
                official.name = f"{fname} {lname}"
            
            if zone_name is not None:
                try:
                    zone = Zone.objects.get(name__iexact=zone_name)
                    official.zone = zone
                except Zone.DoesNotExist:
                    return StandardResponseDTO[OfficialOut](
                        data=None,
                        status_code=HTTPStatusCode.NOT_FOUND,
                        success=False,
                        message="Zone not found"
                    )
            
            # Handle profile image updates
            if remove_image:
                # Remove current image link but don't delete the image itself
                if official.profile_image:
                    official.profile_image.content_type = None
                    official.profile_image.object_id = None
                    official.profile_image.save()
                official.profile_image = None
            elif profile_image:
                # Upload new image and replace current one
                try:
                    # Remove old image link if exists
                    if official.profile_image:
                        official.profile_image.content_type = None
                        official.profile_image.object_id = None
                        official.profile_image.save()
                    
                    # Create new image
                    new_image = TYMAImage.objects.create(
                        title=image_title or f"Profile image for {official.name}",
                        image=profile_image,
                        alt_text=image_alt_text or f"Profile image of {official.name}",
                        caption=image_caption or "",
                        image_type='PROFILE'
                    )
                    
                    # Link to official
                    official_ct = ContentType.objects.get_for_model(Official)
                    new_image.content_type = official_ct
                    new_image.object_id = official.id
                    new_image.save()
                    
                    official.profile_image = new_image
                except Exception as e:
                    return StandardResponseDTO[OfficialOut](
                        data=None,
                        status_code=HTTPStatusCode.BAD_REQUEST,
                        success=False,
                        message=f"Error uploading profile image: {str(e)}"
                    )
            
            # Update other fields
            if phone is not None:
                official.phone = phone
            if position is not None:
                official.position = position
            if official_type is not None:
                official.official_type = official_type
            if email is not None:
                official.email = email
            if bio is not None:
                official.bio = bio
            
            official.save()
            return StandardResponseDTO[OfficialOut](
                data=OfficialService._official_to_schema(official),
                status_code=HTTPStatusCode.OK,
                message="Official updated successfully with image"
            )
        except Official.DoesNotExist:
            return StandardResponseDTO[OfficialOut](
                data=None,
                status_code=HTTPStatusCode.NOT_FOUND,
                success=False,
                message=f"Official with ID '{official_id}' not found"
            )
        except Exception as e:
            return StandardResponseDTO[OfficialOut](
                data=None,
                status_code=HTTPStatusCode.BAD_REQUEST,
                success=False,
                message=str(e)
            )

    @staticmethod
    def delete_official(official_id: str) -> StandardResponseDTO[None]:
        """Delete an official by ID"""
        try:
            official = Official.objects.get(official_id=official_id)
            official.delete()
            return StandardResponseDTO[None](
                message="Official deleted successfully"
            )
        except ObjectDoesNotExist:
            return StandardResponseDTO[None](
                status_code=HTTPStatusCode.NOT_FOUND,
                success=False,
                message="Official not found"
            )
        except Exception as e:
            return StandardResponseDTO[None](
                status_code=HTTPStatusCode.INTERNAL_SERVER_ERROR,
                success=False,
                message=str(e)
            )


class ContactService:
    @staticmethod
    def _contact_to_schema(contact: ContactSubmission) -> ContactSubmissionOut:
        """Convert ContactSubmission model instance to ContactSubmissionOut schema"""
        from .schemas import ContactSubmissionOut
        return ContactSubmissionOut(
            id=contact.id,
            name=contact.name,
            email=contact.email,
            phone=contact.phone,
            subject=contact.subject,
            message=contact.message,
            submitted_at=contact.submitted_at,
            is_responded=contact.is_responded,
            response_notes=contact.response_notes
        )

    @staticmethod
    def create_contact_submission(name: str, email: str, subject: str, message: str, 
                                 phone: Optional[str] = None) -> StandardResponseDTO['ContactSubmissionOut']:
        """Create a new contact submission"""
        try:
            from .models import ContactSubmission
            from .schemas import ContactSubmissionOut
            from django.core.validators import validate_email
            from django.core.exceptions import ValidationError
            import html
            
            # Validate email format
            try:
                validate_email(email)
            except ValidationError:
                return StandardResponseDTO[ContactSubmissionOut](
                    data=None,
                    status_code=HTTPStatusCode.BAD_REQUEST,
                    success=False,
                    message="Invalid email format"
                )
            
            # Sanitize inputs
            name = html.escape(name.strip())
            message = html.escape(message.strip())
            phone = html.escape(phone.strip()) if phone else ""
            
            # Additional validation
            if len(name) < 2:
                return StandardResponseDTO[ContactSubmissionOut](
                    data=None,
                    status_code=HTTPStatusCode.BAD_REQUEST,
                    success=False,
                    message="Name must be at least 2 characters long"
                )
                
            if len(message) < 10:
                return StandardResponseDTO[ContactSubmissionOut](
                    data=None,
                    status_code=HTTPStatusCode.BAD_REQUEST,
                    success=False,
                    message="Message must be at least 10 characters long"
                )
            
            # Validate subject choice
            valid_subjects = dict(ContactSubmission.SUBJECT_CHOICES).keys()
            if subject not in valid_subjects:
                return StandardResponseDTO[ContactSubmissionOut](
                    data=None,
                    status_code=HTTPStatusCode.BAD_REQUEST,
                    success=False,
                    message=f"Invalid subject. Valid choices are: {', '.join(valid_subjects)}"
                )
            
            contact = ContactSubmission.objects.create(
                name=name,
                email=email.lower(),  # Normalize email
                phone=phone,
                subject=subject,
                message=message
            )
            
            return StandardResponseDTO[ContactSubmissionOut](
                data=ContactService._contact_to_schema(contact),
                status_code=HTTPStatusCode.CREATED,
                message="Contact submission created successfully"
            )
        except Exception as e:
            return StandardResponseDTO[ContactSubmissionOut](
                data=None,
                status_code=HTTPStatusCode.INTERNAL_SERVER_ERROR,
                success=False,
                message=f"Failed to create contact submission: {str(e)}"
            )

    @staticmethod
    def get_all_contact_submissions(
        page: int = 1, 
        per_page: int = 10, 
        email: Optional[str] = None, 
        subject: Optional[str] = None
    ) -> StandardResponseDTO[PaginatedResponseSchema['ContactSubmissionOut']]:
        """Get all contact submissions with pagination and optional filtering"""
        try:
            from .models import ContactSubmission
            from .schemas import ContactSubmissionOut
            import html
            
            queryset = ContactSubmission.objects.all()
            
            # Apply filters if provided (with sanitization)
            if email:
                # Sanitize email input to prevent injection
                email_clean = html.escape(email.strip())
                if len(email_clean) > 0:
                    queryset = queryset.filter(email__icontains=email_clean)
            
            if subject:
                # Validate subject is from allowed choices
                valid_subjects = dict(ContactSubmission.SUBJECT_CHOICES).keys()
                if subject in valid_subjects:
                    queryset = queryset.filter(subject=subject)
            
            # Ensure reasonable pagination limits
            per_page = min(per_page, 100)  # Cap at 100 items per page
            
            paginated_data = ZoneService._get_paginated_response(
                queryset, page, per_page, ContactService._contact_to_schema
            )
            
            return StandardResponseDTO[PaginatedResponseSchema[ContactSubmissionOut]](
                data=paginated_data,
                message="Contact submissions retrieved successfully"
            )
        except Exception as e:
            return StandardResponseDTO[PaginatedResponseSchema[ContactSubmissionOut]](
                data=None,
                status_code=HTTPStatusCode.INTERNAL_SERVER_ERROR,
                success=False,
                message=f"Failed to retrieve contact submissions: {str(e)}"
            )

    @staticmethod
    def get_subject_choices() -> StandardResponseDTO[List[dict]]:
        """Get all available subject choices for contact submissions"""
        try:
            from .models import ContactSubmission
            
            choices = [
                {"value": choice[0], "label": choice[1]} 
                for choice in ContactSubmission.SUBJECT_CHOICES
            ]
            
            return StandardResponseDTO[List[dict]](
                data=choices,
                message="Subject choices retrieved successfully"
            )
        except Exception as e:
            return StandardResponseDTO[List[dict]](
                data=None,
                status_code=HTTPStatusCode.INTERNAL_SERVER_ERROR,
                success=False,
                message=f"Failed to retrieve subject choices: {str(e)}"
            )


class NewsletterService:
    @staticmethod
    def _subscriber_to_schema(subscriber: NewsletterSubscriber) -> NewsletterSubscriberOut:
        """Convert NewsletterSubscriber model instance to NewsletterSubscriberOut schema"""
        from .schemas import NewsletterSubscriberOut
        return NewsletterSubscriberOut(
            id=subscriber.id,
            email=subscriber.email,
            is_active=subscriber.is_active,
            subscribed_at=subscriber.subscribed_at,
            unsubscribed_at=subscriber.unsubscribed_at
        )

    @staticmethod
    def subscribe_newsletter(email: str) -> StandardResponseDTO['NewsletterSubscriberOut']:
        """Subscribe to newsletter"""
        try:
            from .models import NewsletterSubscriber
            from .schemas import NewsletterSubscriberOut
            from django.core.validators import validate_email
            from django.core.exceptions import ValidationError
            from django.utils import timezone
            
            # Normalize and validate email
            email = email.lower().strip()
            
            # Validate email format
            try:
                validate_email(email)
            except ValidationError:
                return StandardResponseDTO[NewsletterSubscriberOut](
                    data=None,
                    status_code=HTTPStatusCode.BAD_REQUEST,
                    success=False,
                    message="Invalid email format"
                )
            
            # Check if already subscribed
            existing_subscriber = NewsletterSubscriber.objects.filter(email=email).first()
            if existing_subscriber:
                if existing_subscriber.is_active:
                    return StandardResponseDTO[NewsletterSubscriberOut](
                        data=NewsletterService._subscriber_to_schema(existing_subscriber),
                        status_code=HTTPStatusCode.CONFLICT,
                        success=False,
                        message="Email is already subscribed to newsletter"
                    )
                else:
                    # Reactivate subscription
                    existing_subscriber.is_active = True
                    existing_subscriber.unsubscribed_at = None
                    existing_subscriber.subscribed_at = timezone.now()  # Update subscription time
                    existing_subscriber.save()
                    return StandardResponseDTO[NewsletterSubscriberOut](
                        data=NewsletterService._subscriber_to_schema(existing_subscriber),
                        message="Newsletter subscription reactivated successfully"
                    )
            
            # Create new subscription
            subscriber = NewsletterSubscriber.objects.create(email=email)
            
            return StandardResponseDTO[NewsletterSubscriberOut](
                data=NewsletterService._subscriber_to_schema(subscriber),
                status_code=HTTPStatusCode.CREATED,
                message="Successfully subscribed to newsletter"
            )
        except Exception as e:
            return StandardResponseDTO[NewsletterSubscriberOut](
                data=None,
                status_code=HTTPStatusCode.INTERNAL_SERVER_ERROR,
                success=False,
                message=f"Failed to subscribe to newsletter: {str(e)}"
            )

    @staticmethod
    def unsubscribe_newsletter(email: str) -> StandardResponseDTO[None]:
        """Unsubscribe from newsletter"""
        try:
            from .models import NewsletterSubscriber
            from django.core.validators import validate_email
            from django.core.exceptions import ValidationError
            
            # Normalize and validate email
            email = email.lower().strip()
            
            # Validate email format
            try:
                validate_email(email)
            except ValidationError:
                return StandardResponseDTO[None](
                    data=None,
                    status_code=HTTPStatusCode.BAD_REQUEST,
                    success=False,
                    message="Invalid email format"
                )
            
            subscriber = NewsletterSubscriber.objects.filter(email=email, is_active=True).first()
            if not subscriber:
                return StandardResponseDTO[None](
                    data=None,
                    status_code=HTTPStatusCode.NOT_FOUND,
                    success=False,
                    message="Email not found in active subscribers"
                )
            
            subscriber.unsubscribe()
            
            return StandardResponseDTO[None](
                message="Successfully unsubscribed from newsletter"
            )
        except Exception as e:
            return StandardResponseDTO[None](
                data=None,
                status_code=HTTPStatusCode.INTERNAL_SERVER_ERROR,
                success=False,
                message=f"Failed to unsubscribe from newsletter: {str(e)}"
            )

    @staticmethod
    def get_all_subscribers(page: int = 1, per_page: int = 10, active_only: bool = True) -> StandardResponseDTO[PaginatedResponseSchema['NewsletterSubscriberOut']]:
        """Get all newsletter subscribers with pagination"""
        try:
            from .models import NewsletterSubscriber
            from .schemas import NewsletterSubscriberOut
            
            queryset = NewsletterSubscriber.objects.all()
            if active_only:
                queryset = queryset.filter(is_active=True)
            
            paginated_data = ZoneService._get_paginated_response(
                queryset, page, per_page, NewsletterService._subscriber_to_schema
            )
            
            return StandardResponseDTO[PaginatedResponseSchema[NewsletterSubscriberOut]](
                data=paginated_data,
                message="Newsletter subscribers retrieved successfully"
            )
        except Exception as e:
            return StandardResponseDTO[PaginatedResponseSchema[NewsletterSubscriberOut]](
                data=None,
                status_code=HTTPStatusCode.INTERNAL_SERVER_ERROR,
                success=False,
                message=f"Failed to retrieve newsletter subscribers: {str(e)}"
            )