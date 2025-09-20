from typing import Optional, List, Union
from uuid import UUID
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.core.files.uploadedfile import InMemoryUploadedFile, TemporaryUploadedFile
from datetime import datetime
import traceback
from .models import NewsEvent, NewsCategory, Official, TYMAImage
from .schemas import (
    HTTPStatusCode,
    StandardResponseDTO,
    NewsOut,
    NewsCategoryOut,
    PaginatedResponseSchema,
    TYMAImageOut
)
from .schemas import NewsCategoryCreateSchema, NewsCreateSchema, NewsUpdateSchema


def create_detailed_error_response(exception: Exception, operation: str) -> str:
    """Create detailed error message with traceback for debugging"""
    error_details = f"Error during {operation}: {str(exception)}"
    if hasattr(exception, '__traceback__'):
        error_details += f"\nTraceback: {traceback.format_exc()}"
    return error_details


class NewsCategoryService:
    @staticmethod
    def _category_to_schema(category: NewsCategory) -> NewsCategoryOut:
        """Converts NewsCategory model instance to NewsCategoryOut schema"""
        return NewsCategoryOut(
            id=category.id,
            name=category.name,
            slug=category.slug,
            description=category.description,
            created_at=category.created_at,
            updated_at=category.updated_at
        )

    @staticmethod
    def get_paginated_categories(queryset, page: int = 1, per_page: int = 10) -> PaginatedResponseSchema[NewsCategoryOut]:
        offset = (page - 1) * per_page
        total = queryset.count()
        categories = queryset[offset:offset + per_page]
        return PaginatedResponseSchema[NewsCategoryOut](
            items=[NewsCategoryService._category_to_schema(cat) for cat in categories],
            total=total,
            page=page,
            per_page=per_page
        )

    @staticmethod
    def create_category(
        name: str,
        description: str = None
    ) -> StandardResponseDTO[NewsCategoryOut]:
        """Creates a new news category"""
        try:
            if NewsCategory.objects.filter(name__iexact=name).exists():
                return StandardResponseDTO[NewsCategoryOut](
                    data=None,
                    status_code=HTTPStatusCode.CONFLICT,
                    success=False,
                    message=f"News category '{name}' already exists"
                )
                
            category = NewsCategory.objects.create(
                name=name,
                description=description
            )
            
            return StandardResponseDTO[NewsCategoryOut](
                data=NewsCategoryService._category_to_schema(category),
                status_code=HTTPStatusCode.CREATED,
                message="News category created successfully"
            )
        except Exception as e:
            return StandardResponseDTO[NewsCategoryOut](
                data=None,
                status_code=HTTPStatusCode.BAD_REQUEST,
                success=False,
                message=str(e)
            )

    @staticmethod
    def get_all_categories(page: int = 1, per_page: int = 10) -> StandardResponseDTO[PaginatedResponseSchema[NewsCategoryOut]]:
        """Retrieves all news categories with pagination"""
        try:
            queryset = NewsCategory.objects.all().order_by('name')
            paginated_data = NewsCategoryService.get_paginated_categories(queryset, page, per_page)
            return StandardResponseDTO[PaginatedResponseSchema[NewsCategoryOut]](
                data=paginated_data,
                status_code=HTTPStatusCode.OK,
                message="News categories retrieved successfully"
            )
        except Exception as e:
            return StandardResponseDTO[PaginatedResponseSchema[NewsCategoryOut]](
                data=None,
                status_code=HTTPStatusCode.INTERNAL_SERVER_ERROR,
                success=False,
                message=str(e)
            )

    @staticmethod
    def get_category_by_slug(slug: str) -> StandardResponseDTO[NewsCategoryOut]:
        """Retrieves a single news category by slug"""
        try:
            category = NewsCategory.objects.get(slug=slug)
            return StandardResponseDTO[NewsCategoryOut](
                data=NewsCategoryService._category_to_schema(category),
                status_code=HTTPStatusCode.OK,
                message="News category retrieved successfully"
            )
        except NewsCategory.DoesNotExist:
            return StandardResponseDTO[NewsCategoryOut](
                data=None,
                status_code=HTTPStatusCode.NOT_FOUND,
                success=False,
                message="News category not found"
            )
        except Exception as e:
            return StandardResponseDTO[NewsCategoryOut](
                data=None,
                status_code=HTTPStatusCode.INTERNAL_SERVER_ERROR,
                success=False,
                message=str(e)
            )

    @staticmethod
    def update_category(
        slug: str,
        name: str = None,
        description: str = None
    ) -> StandardResponseDTO[NewsCategoryOut]:
        """Updates an existing news category"""
        try:
            category = NewsCategory.objects.get(slug=slug)
            
            if name:
                if NewsCategory.objects.filter(name__iexact=name).exclude(slug=slug).exists():
                    return StandardResponseDTO[NewsCategoryOut](
                        data=None,
                        status_code=HTTPStatusCode.CONFLICT,
                        success=False,
                        message=f"News category '{name}' already exists"
                    )
                category.name = name
                
            if description is not None:
                category.description = description
                
            category.save()
            return StandardResponseDTO[NewsCategoryOut](
                data=NewsCategoryService._category_to_schema(category),
                status_code=HTTPStatusCode.OK,
                message="News category updated successfully"
            )
        except NewsCategory.DoesNotExist:
            return StandardResponseDTO[NewsCategoryOut](
                data=None,
                status_code=HTTPStatusCode.NOT_FOUND,
                success=False,
                message="News category not found"
            )
        except Exception as e:
            return StandardResponseDTO[NewsCategoryOut](
                data=None,
                status_code=HTTPStatusCode.BAD_REQUEST,
                success=False,
                message=str(e)
            )

    @staticmethod
    def delete_category(slug: str) -> StandardResponseDTO[None]:
        """Deletes a news category by slug"""
        try:
            category = NewsCategory.objects.get(slug=slug)
            
            # Check if category has any news before deletion
            if category.newsevent_set.exists():
                return StandardResponseDTO[None](
                    status_code=HTTPStatusCode.CONFLICT,
                    success=False,
                    message="Cannot delete category with associated news"
                )
                
            category.delete()
            return StandardResponseDTO[None](
                status_code=HTTPStatusCode.OK,
                message="News category deleted successfully"
            )
        except NewsCategory.DoesNotExist:
            return StandardResponseDTO[None](
                status_code=HTTPStatusCode.NOT_FOUND,
                success=False,
                message="News category not found"
            )
        except Exception as e:
            return StandardResponseDTO[None](
                status_code=HTTPStatusCode.INTERNAL_SERVER_ERROR,
                success=False,
                message=str(e)
            )


class NewsService:
    @staticmethod
    def _news_to_schema(news: NewsEvent) -> NewsOut:
        """Converts NewsEvent model instance to NewsOut schema"""
        return NewsOut(
            id=news.id,
            title=news.title,
            slug=news.slug,
            news_type=news.news_type,
            categories=[NewsCategoryOut(
                id=cat.id,
                name=cat.name,
                slug=cat.slug,
                description=cat.description,
                created_at=cat.created_at,
                updated_at=cat.updated_at
            ) for cat in news.categories.all()],
            short_description=news.short_description,
            content=news.content,
            featured_image=TYMAImageOut(
                id=news.featured_image.id,
                title=news.featured_image.title,
                url=news.featured_image.get_image_url(),
                alt_text=news.featured_image.alt_text,
                caption=news.featured_image.caption,
                image_type=news.featured_image.image_type,
                content_type=news.featured_image.content_type.model if news.featured_image.content_type else None,
                object_id=str(news.featured_image.object_id) if news.featured_image.object_id else None,
                created_at=news.featured_image.created_at,
                updated_at=news.featured_image.updated_at
            ) if news.featured_image else None,
            is_featured=news.is_featured,
            event_date=news.event_date,
            event_location=news.event_location,
            published_at=news.published_at,
            author=news.author.name if news.author else "Unknown",
            views=news.views,
            created_at=news.created_at,
            updated_at=news.updated_at
        )
        
    @staticmethod
    def get_paginated_news(queryset, page: int = 1, per_page: int = 10) -> PaginatedResponseSchema[NewsOut]:
        offset = (page - 1) * per_page
        total = queryset.count()
        news_items = queryset.select_related('author', 'featured_image').prefetch_related('categories')[offset:offset + per_page]
        return PaginatedResponseSchema[NewsOut](
            items=[NewsService._news_to_schema(news) for news in news_items],
            total=total,
            page=page,
            per_page=per_page
        )

    @staticmethod
    def create_news(
        title: str,
        news_type: str,
        short_description: str,
        content: str,
        author_id: str,
        category_slugs: List[str] = None,
        featured_image_id: Optional[str] = None,
        is_featured: bool = False,
        event_date: Optional[timezone.datetime] = None,
        event_location: Optional[str] = None,
    ) -> StandardResponseDTO[NewsOut]:
        """Creates a new news article or event"""
        try:
            # Validate news_type
            allowed_types = ['article', 'event']
            if news_type.lower() not in allowed_types:
                return StandardResponseDTO[NewsOut](
                    data=None,
                    status_code=HTTPStatusCode.BAD_REQUEST,
                    success=False,
                    message=f"Invalid news type. Allowed types are: {', '.join(allowed_types)}"
                )

            # Get the User instance
            try:
                author = Official.objects.get(official_id=author_id)
                if not author.official_type.lower() == 'admin':
                    return StandardResponseDTO[NewsOut](
                        data=None,
                        status_code=HTTPStatusCode.FORBIDDEN,
                        success=False,
                        message="Only admin users can create news"
                    )
            except Official.DoesNotExist:
                return StandardResponseDTO[NewsOut](
                    data=None,
                    status_code=HTTPStatusCode.NOT_FOUND,
                    success=False,
                    message="Author not found"
                )
            
            # Get featured image if provided
            featured_image_instance = None
            if featured_image_id:
                try:
                    featured_image_instance = TYMAImage.objects.get(id=UUID(featured_image_id))
                except (ValueError, TYMAImage.DoesNotExist):
                    return StandardResponseDTO[NewsOut](
                        data=None,
                        status_code=HTTPStatusCode.NOT_FOUND,
                        success=False,
                        message="Featured image not found"
                    )
            
            # Create the news item
            news = NewsEvent.objects.create(
                title=title,
                news_type=news_type,
                short_description=short_description,
                content=content,
                author=author,
                featured_image=featured_image_instance,
                is_featured=is_featured,
                event_date=event_date,
                event_location=event_location,
                published_at=timezone.now()
            )
            
            # Add categories by slug if provided
            if category_slugs:
                categories = NewsCategory.objects.filter(slug__in=category_slugs)
                if categories.exists():
                    news.categories.set(categories)
                    
            return StandardResponseDTO[NewsOut](
                data=NewsService._news_to_schema(news),
                status_code=HTTPStatusCode.CREATED,
                message="News created successfully"
            )
            
        except Exception as e:
            return StandardResponseDTO[NewsOut](
                data=None,
                status_code=HTTPStatusCode.BAD_REQUEST,
                success=False,
                message=str(e)
            )

    @staticmethod
    def create_news_with_image(
        title: str,
        news_type: str,
        short_description: str,
        content: str,
        author_id: str,
        category_slugs: List[str] = None,
        is_featured: bool = False,
        event_date: Optional[timezone.datetime] = None,
        event_location: Optional[str] = None,
        featured_image: Optional[Union[InMemoryUploadedFile, TemporaryUploadedFile]] = None,
        image_title: Optional[str] = None,
        image_alt_text: Optional[str] = None,
        image_caption: Optional[str] = None,
    ) -> StandardResponseDTO[NewsOut]:
        """Creates a new news article or event with direct image upload"""
        try:
            # Validate news_type
            allowed_types = ['article', 'NEWS', 'EVENT', 'ANNOUNCEMENT']
            if news_type.upper() not in allowed_types:
                return StandardResponseDTO[NewsOut](
                    data=None,
                    status_code=HTTPStatusCode.BAD_REQUEST,
                    success=False,
                    message=f"Invalid news type. Allowed types are: {', '.join(allowed_types)}"
                )

            # Get the author
            try:
                author = Official.objects.get(official_id=author_id)
            except Official.DoesNotExist:
                return StandardResponseDTO[NewsOut](
                    data=None,
                    status_code=HTTPStatusCode.NOT_FOUND,
                    success=False,
                    message="Author not found"
                )
            
            # Create featured image if provided
            featured_image_instance = None
            if featured_image:
                try:
                    # Create the TYMA image first
                    image = TYMAImage.objects.create(
                        title=image_title or f"Featured image for {title}",
                        image=featured_image,
                        alt_text=image_alt_text or f"Featured image for {title}",
                        caption=image_caption or "",
                        image_type='FEATURED'
                    )
                    featured_image_instance = image
                except Exception as e:
                    return StandardResponseDTO[NewsOut](
                        data=None,
                        status_code=HTTPStatusCode.BAD_REQUEST,
                        success=False,
                        message=f"Error uploading image: {str(e)}"
                    )
            
            # Create the news item
            news = NewsEvent.objects.create(
                title=title,
                news_type=news_type.upper(),
                short_description=short_description,
                content=content,
                author=author,
                featured_image=featured_image_instance,
                is_featured=is_featured,
                event_date=event_date,
                event_location=event_location or "",  # Ensure empty string instead of None
                published_at=timezone.now()
            )
            
            # Link the image to the news item using generic foreign key
            if featured_image_instance:
                news_ct = ContentType.objects.get_for_model(NewsEvent)
                featured_image_instance.content_type = news_ct
                featured_image_instance.object_id = news.id
                featured_image_instance.save()
            
            # Add categories by slug if provided
            if category_slugs:
                categories = NewsCategory.objects.filter(slug__in=category_slugs)
                if categories.exists():
                    news.categories.set(categories)
                    
            return StandardResponseDTO[NewsOut](
                data=NewsService._news_to_schema(news),
                status_code=HTTPStatusCode.CREATED,
                message="News created successfully with image"
            )
            
        except Exception as e:
            error_message = create_detailed_error_response(e, "news creation")
            return StandardResponseDTO[NewsOut](
                data=None,
                status_code=HTTPStatusCode.BAD_REQUEST,
                success=False,
                message=error_message
            )

    @staticmethod
    def get_news_by_slug(slug: str) -> StandardResponseDTO[NewsOut]:
        """Retrieves a single news item by slug"""
        try:
            news = NewsEvent.objects.select_related('author', 'featured_image').prefetch_related('categories').get(slug=slug)
            news.views += 1
            news.save()
            return StandardResponseDTO[NewsOut](
                data=NewsService._news_to_schema(news),
                status_code=HTTPStatusCode.OK,
                message="News retrieved successfully"
            )
        except NewsEvent.DoesNotExist:
            return StandardResponseDTO[NewsOut](
                data=None,
                status_code=HTTPStatusCode.NOT_FOUND,
                success=False,
                message="News not found"
            )
        except Exception as e:
            return StandardResponseDTO[NewsOut](
                data=None,
                status_code=HTTPStatusCode.INTERNAL_SERVER_ERROR,
                success=False,
                message=str(e)
            )

    @staticmethod
    def get_filtered_news(
        search: Optional[str] = None,
        news_type: Optional[str] = None,
        category_slug: Optional[str] = None,
        is_featured: Optional[bool] = None,
        author_id: Optional[str] = None,
        year: Optional[int] = None,
        month: Optional[int] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        latest_news: Optional[bool] = None,
        page: int = 1,
        per_page: int = 10,
        sort_by: str = '-published_at'
    ) -> StandardResponseDTO[PaginatedResponseSchema[NewsOut]]:
        """
        Retrieves news with advanced filters and pagination
        
        Args:
            search: Text search in title and content
            news_type: Filter by 'article' or 'event'
            category_slug: Filter by category slug
            is_featured: Filter by featured status
            author_id: Filter by author's official_id
            year: Filter by year of published date
            month: Filter by month of published date
            start_date: Filter news published after this date
            end_date: Filter news published before this date
            latest_news: Return only latest news (ignores pagination)
            page: Page number
            per_page: Items per page
            sort_by: Field to sort by (prefix with - for descending)
        """
        try:
            queryset = NewsEvent.objects.all().select_related('author', 'featured_image').prefetch_related('categories')
            
            # Text search
            if search:
                queryset = queryset.filter(
                    models.Q(title__icontains=search) |
                    models.Q(content__icontains=search) |
                    models.Q(short_description__icontains=search)
                )
            
            # Exact match filters
            if news_type:
                queryset = queryset.filter(news_type__iexact=news_type)
            if category_slug:
                queryset = queryset.filter(categories__slug=category_slug)
            if is_featured is not None:
                queryset = queryset.filter(is_featured=is_featured)
            if author_id:
                queryset = queryset.filter(author__official_id=author_id)
            
            # Date filters
            if year:
                queryset = queryset.filter(published_at__year=year)
            if month:
                queryset = queryset.filter(published_at__month=month)
            if start_date:
                queryset = queryset.filter(published_at__gte=start_date)
            if end_date:
                queryset = queryset.filter(published_at__lte=end_date)
            
            # Sorting
            queryset = queryset.order_by(sort_by).distinct()
            
            # Latest news (no pagination)
            if latest_news:
                queryset = queryset[:per_page]
                paginated_data = PaginatedResponseSchema[NewsOut](
                    items=[NewsService._news_to_schema(news) for news in queryset],
                    total=queryset.count(),
                    page=1,
                    per_page=per_page
                )
            else:
                paginated_data = NewsService.get_paginated_news(queryset, page, per_page)
                
            return StandardResponseDTO[PaginatedResponseSchema[NewsOut]](
                data=paginated_data,
                status_code=HTTPStatusCode.OK,
                message="News retrieved successfully"
            )
        except Exception as e:
            return StandardResponseDTO[PaginatedResponseSchema[NewsOut]](
                data=None,
                status_code=HTTPStatusCode.INTERNAL_SERVER_ERROR,
                success=False,
                message=str(e)
            )

    @staticmethod
    def update_news(
        slug: str,
        title: Optional[str] = None,
        news_type: Optional[str] = None,
        short_description: Optional[str] = None,
        content: Optional[str] = None,
        author_id: Optional[str] = None,
        category_slugs: Optional[List[str]] = None,
        featured_image_id: Optional[str] = None,
        is_featured: Optional[bool] = None,
        event_date: Optional[timezone.datetime] = None,
        event_location: Optional[str] = None,
    ) -> StandardResponseDTO[NewsOut]:
        """Updates an existing news item by slug"""
        try:
            news = NewsEvent.objects.get(slug=slug)
            
            # Validate and update fields if provided
            if title is not None:
                news.title = title
                
            if news_type is not None:
                allowed_types = ['article', 'event', 'announcement']
                if news_type.lower() not in allowed_types:
                    return StandardResponseDTO[NewsOut](
                        data=None,
                        status_code=HTTPStatusCode.BAD_REQUEST,
                        success=False,
                        message=f"Invalid news type. Allowed types are: {', '.join(allowed_types)}"
                    )
                news.news_type = news_type
                
            if short_description is not None:
                news.short_description = short_description
                
            if content is not None:
                news.content = content
                
            if author_id is not None:
                try:
                    author = Official.objects.get(official_id=author_id)
                    if not author.official_type.lower() == 'admin':
                        return StandardResponseDTO[NewsOut](
                            data=None,
                            status_code=HTTPStatusCode.FORBIDDEN,
                            success=False,
                            message="Only admin users can update news"
                        )
                    news.author = author
                except Official.DoesNotExist:
                    return StandardResponseDTO[NewsOut](
                        data=None,
                        status_code=HTTPStatusCode.NOT_FOUND,
                        success=False,
                        message="Author not found"
                    )
                    
            if featured_image_id is not None:
                if featured_image_id == "":
                    # Clear the featured image if empty string is provided
                    news.featured_image = None
                else:
                    try:
                        featured_image = TYMAImage.objects.get(id=UUID(featured_image_id))
                        news.featured_image = featured_image
                    except (ValueError, TYMAImage.DoesNotExist):
                        return StandardResponseDTO[NewsOut](
                            data=None,
                            status_code=HTTPStatusCode.NOT_FOUND,
                            success=False,
                            message="Featured image not found"
                        )
                        
            if is_featured is not None:
                news.is_featured = is_featured
                
            if event_date is not None:
                news.event_date = event_date
                
            if event_location is not None:
                news.event_location = event_location
                
            news.save()
            
            # Update categories if provided
            if category_slugs is not None:
                categories = NewsCategory.objects.filter(slug__in=category_slugs)
                if categories.exists():
                    news.categories.set(categories)
                    
            return StandardResponseDTO[NewsOut](
                data=NewsService._news_to_schema(news),
                status_code=HTTPStatusCode.OK,
                message="News updated successfully"
            )
        except NewsEvent.DoesNotExist:
            return StandardResponseDTO[NewsOut](
                data=None,
                status_code=HTTPStatusCode.NOT_FOUND,
                success=False,
                message="News not found"
            )
        except Exception as e:
            return StandardResponseDTO[NewsOut](
                data=None,
                status_code=HTTPStatusCode.BAD_REQUEST,
                success=False,
                message=str(e)
            )

    @staticmethod
    def update_news_with_image(
        slug: str,
        title: Optional[str] = None,
        news_type: Optional[str] = None,
        short_description: Optional[str] = None,
        content: Optional[str] = None,
        author_id: Optional[str] = None,
        category_slugs: Optional[List[str]] = None,
        is_featured: Optional[bool] = None,
        event_date: Optional[timezone.datetime] = None,
        event_location: Optional[str] = None,
        featured_image: Optional[Union[InMemoryUploadedFile, TemporaryUploadedFile]] = None,
        remove_image: bool = False,
        image_title: Optional[str] = None,
        image_alt_text: Optional[str] = None,
        image_caption: Optional[str] = None,
    ) -> StandardResponseDTO[NewsOut]:
        """Updates an existing news item with optional image replacement"""
        try:
            news = NewsEvent.objects.get(slug=slug)
            
            # Validate and update fields if provided
            if title is not None:
                news.title = title
                
            if news_type is not None:
                allowed_types = ['article', 'event', 'announcement', 'NEWS', 'EVENT', 'ANNOUNCEMENT']
                if news_type.upper() not in allowed_types:
                    return StandardResponseDTO[NewsOut](
                        data=None,
                        status_code=HTTPStatusCode.BAD_REQUEST,
                        success=False,
                        message=f"Invalid news type. Allowed types are: {', '.join(allowed_types)}"
                    )
                news.news_type = news_type.upper()
            
            if short_description is not None:
                news.short_description = short_description
                
            if content is not None:
                news.content = content
                
            if author_id is not None:
                try:
                    author = Official.objects.get(official_id=author_id)
                    news.author = author
                except Official.DoesNotExist:
                    return StandardResponseDTO[NewsOut](
                        data=None,
                        status_code=HTTPStatusCode.NOT_FOUND,
                        success=False,
                        message="Author not found"
                    )
            
            # Handle image updates
            if remove_image:
                # Remove current image link but don't delete the image itself
                if news.featured_image:
                    news.featured_image.content_type = None
                    news.featured_image.object_id = None
                    news.featured_image.save()
                news.featured_image = None
            elif featured_image:
                # Upload new image and replace current one
                try:
                    # Remove old image link if exists
                    if news.featured_image:
                        news.featured_image.content_type = None
                        news.featured_image.object_id = None
                        news.featured_image.save()
                    
                    # Create new image
                    new_image = TYMAImage.objects.create(
                        title=image_title or f"Featured image for {news.title}",
                        image=featured_image,
                        alt_text=image_alt_text or f"Featured image for {news.title}",
                        caption=image_caption or "",
                        image_type='FEATURED'
                    )
                    
                    # Link to news
                    news_ct = ContentType.objects.get_for_model(NewsEvent)
                    new_image.content_type = news_ct
                    new_image.object_id = news.id
                    new_image.save()
                    
                    news.featured_image = new_image
                except Exception as e:
                    return StandardResponseDTO[NewsOut](
                        data=None,
                        status_code=HTTPStatusCode.BAD_REQUEST,
                        success=False,
                        message=f"Error uploading image: {str(e)}"
                    )
                        
            if is_featured is not None:
                news.is_featured = is_featured
                
            if event_date is not None:
                news.event_date = event_date
                
            if event_location is not None:
                news.event_location = event_location
                
            news.save()
            
            # Update categories if provided
            if category_slugs is not None:
                categories = NewsCategory.objects.filter(slug__in=category_slugs)
                if categories.exists():
                    news.categories.set(categories)
                    
            return StandardResponseDTO[NewsOut](
                data=NewsService._news_to_schema(news),
                status_code=HTTPStatusCode.OK,
                message="News updated successfully with image"
            )
        except NewsEvent.DoesNotExist:
            return StandardResponseDTO[NewsOut](
                data=None,
                status_code=HTTPStatusCode.NOT_FOUND,
                success=False,
                message="News not found"
            )
        except Exception as e:
            return StandardResponseDTO[NewsOut](
                data=None,
                status_code=HTTPStatusCode.BAD_REQUEST,
                success=False,
                message=str(e)
            )

    @staticmethod
    def delete_news(slug: str) -> StandardResponseDTO[None]:
        """Deletes a news item by slug"""
        try:
            news = NewsEvent.objects.get(slug=slug)
            news.delete()
            return StandardResponseDTO[None](
                status_code=HTTPStatusCode.OK,
                message="News deleted successfully"
            )
        except NewsEvent.DoesNotExist:
            return StandardResponseDTO[None](
                status_code=HTTPStatusCode.NOT_FOUND,
                success=False,
                message="News not found"
            )
        except Exception as e:
            return StandardResponseDTO[None](
                status_code=HTTPStatusCode.INTERNAL_SERVER_ERROR,
                success=False,
                message=str(e)
            )