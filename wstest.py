import requests
response=requests.get("https://www.cpge.ac.ma/")
print(response.text)