import requests

url = 'http://127.0.0.1:5000/remove_background'

# Leer el base64 desde el archivo de texto
with open('image_base64.txt', 'r') as text_file:
    image_base64 = text_file.read().strip()

# Crear el payload JSON
payload = {'image': image_base64}

response = requests.post(url, json=payload)
print(response.json())
