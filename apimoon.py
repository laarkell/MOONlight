# https://www.askpython.com/python/examples/pull-data-from-an-api
# https://ipgeolocation.io/documentation/astronomy-api.html

response_API = get('https://api.ipgeolocation.io/astronomy?apiKey=09c8f79c7db149f7ad8d42ffa7a73ce2&lat=35.499&long=-80.848')
data = response_API.text
print(data)

