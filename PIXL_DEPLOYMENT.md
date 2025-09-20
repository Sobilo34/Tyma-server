# TYMA Server - Pixl Space Deployment Guide

This Django project is configured for deployment on Pixl Space. Follow the steps below to deploy successfully.

## Prerequisites

1. A Pixl Space account
2. Git repository with your code
3. Required environment variables configured

## Deployment Files

- `pixl.toml` - Main Pixl Space configuration
- `start.sh` - Application startup script
- `core/pixl_settings.py` - Production Django settings
- `.env.example` - Environment variables template

## Required Environment Variables

Set the following environment variables in your Pixl Space dashboard:

```bash
# Required
SECRET_KEY=your-django-secret-key
DEBUG=False
ALLOWED_HOSTS=your-app-name.pixl.space

# Optional - Admin User
DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_EMAIL=admin@example.com
DJANGO_SUPERUSER_PASSWORD=secure-password

# Optional - CORS Configuration
CORS_ALLOWED_ORIGINS=https://your-frontend-domain.com
```

## Database

Pixl Space will automatically provide a PostgreSQL database via the `DATABASE_URL` environment variable. No additional configuration is needed.

## Static Files

Static files are automatically collected and served using WhiteNoise. The configuration is already set up in the Django settings.

## Deployment Steps

1. **Connect your repository** to Pixl Space
2. **Set environment variables** in the Pixl Space dashboard
3. **Deploy** - Pixl Space will automatically:
   - Install dependencies from `requirements.txt`
   - Run database migrations
   - Collect static files
   - Start the application with Gunicorn

## Health Check

The application includes a health check endpoint configured in `pixl.toml` at `/api/` that Pixl Space will use to monitor application health.

## Troubleshooting

### Common Issues:

1. **Secret Key Error**: Make sure `SECRET_KEY` environment variable is set
2. **Database Connection**: Verify `DATABASE_URL` is automatically provided by Pixl Space
3. **Static Files**: Ensure `whitenoise` is in requirements.txt and properly configured
4. **CORS Issues**: Update `CORS_ALLOWED_ORIGINS` environment variable with your frontend domains

### Logs

Check Pixl Space logs for any deployment issues. The application uses structured logging to help with debugging.

## Local Development

For local development, copy `.env.example` to `.env` and update the values:

```bash
cp .env.example .env
# Edit .env with your local configuration
```

## Support

If you encounter any issues:
1. Check Pixl Space documentation
2. Review the application logs in Pixl Space dashboard
3. Ensure all environment variables are properly set
