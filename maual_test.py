from instagrapi import Client

# Zugangsdaten
username = "berndbot2"
password = "DS8QG7UtY@,kD_M"

# Beispiel-Dateipfad + Caption
file_path = "app/static/uploads/20250619212107_testpic.jpeg"
caption = "horse #horse"

# Login
cl = Client()
cl.login(username, password)

# Posten
cl.photo_upload(file_path, 'Dog')

print("[TEST] Post wurde gesendet")
