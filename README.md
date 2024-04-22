# GeoEDF Portal
The GeoEDF project seeks to develop a resource data management portal that supports the FAIR data principles, particularly for geospatial datasets. 
The portal currently supports customized search and filter operations as part of the resource querying functionality. 

The resource landing page is deveployed to display detailed file metadata and make it indexable and searchable via Google Dataset Search. It displays resource metadata and the spatial coverage bounding box in a Google map. The landing page also contains embedded structured schema.org metadata which can be crawled and indexed by Google. 



## Deploying
### Local Deployment
    docker-compose build
    docker-compose run -it -p 8000:8000 web
Your portal should now be running at http://localhost:8000


### Anvil Development
1. To build the image with `Github Actions`, push code to Github repository and track the status of the workflow. 
2. Github Actions config file is in `.github/workflows/github-actions-demo.yml`. 
3. Images are stored in [Registry Harbor](registry.anvil.rcac.purdue.edu). Registry server and token information can be set in Settings->Environments->{$ENV_NAME}->Environment Secrets
4. Update image tag via Anvil user interface or with `kubectl`


## Testing and Debugging

### API Swagger

http://localhost:8000/swagger/

### API Documentation

http://localhost:8000/redoc/

### Database


### Environment Variables
- `DJANGO_SUPERUSER_USERNAME`, `DJANGO_SUPERUSER_EMAIL`, `DJANGO_SUPERUSER_PASSWORD` are variables for Django admin superuser 
- `SITE_NAME` is the domain name for sitemap


## Features and Tools
### Globus Search Index
- [Globus Index Documentation](https://django-globus-portal-framework.readthedocs.io/en/latest/tutorial/search/search-settings-reference.html#search-indices)
- Globus app credentials
  - Client ID, ...


### Google Search
- Sitemap
  - Auto-update domain name
  - Submit sitemap in Google Search Console

- [Google Search Console](https://search.google.com/search-console)
- [Documentation](https://developers.google.com/search/docs/appearance/structured-data/dataset)
- (waiting for reply) [The post to Google Search Console Help Community](https://support.google.com/webmasters/thread/253986586?hl=en&sjid=5136514339393167681-NC)

### FAIR Evaluation
Refer to `myportal/tests`

### Authorization
The APIs in the portal normally have two ways of identity verification. 
1. CILogon
   - Register callback URLs through CILogon website
   - Use `client identifier` and `client secret` 
2. Jupyter API Token


### Schema.org
- [Structured Data Validator](https://validator.schema.org/)
- [Google Rich Result Test](https://search.google.com/test/rich-results)
