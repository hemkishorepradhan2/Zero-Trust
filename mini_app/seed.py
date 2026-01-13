from passlib.context import CryptContext
pwd_context=CryptContext(schemes=['bcrypt'],depreceted="auto")
fake_users={
    "hem":{
        "username":"hem",
        "password":pwd_context.hash("test1234"),
        "role":"ADMIN"
    }
}