from werkzeug.security import generate_password_hash

user_pass = generate_password_hash('user@123')
admin_pass = generate_password_hash('admin@123')

print("User hash:")
print(user_pass)
print("\nAdmin hash:")
print(admin_pass)
