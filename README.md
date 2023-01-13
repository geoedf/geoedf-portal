# GeoEDF Portal

### Environment Variables
- `DJANGO_SUPERUSER_USERNAME`, `DJANGO_SUPERUSER_EMAIL`, `DJANGO_SUPERUSER_PASSWORD` are variables for Django admin superuser 
- `SITE_NAME` is the domain name for sitemap

### Running the Portal
    docker-compose build
    docker-compose run -it -p 8000:8000 web

Your portal should now be running at http://localhost:8000
