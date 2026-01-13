def validate_access(user,requesy):
    return True

allow=False
user={
    "id":1,
    "role":"user"
}

if(user['role']=='admin'):
    allow=True

    