import drest

api = drest.api.TastyPieAPI('http://localhost:8080/bmiconsole/api/v1/')
api.auth('pybootd', 'MyFacnyApiKeyForAuhtorization')

print api.resources

systems = api.systems.get()

print systems.data