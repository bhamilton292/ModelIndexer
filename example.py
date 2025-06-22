from pydantic import BaseModel
from IndexedModel import ModelIndex

class User(BaseModel):
    id: int
    username: str
    email: str

class OtherUser(BaseModel):
    id: int
    username: str
    email: str
    other: str

users = [
    User(id=1, username="alice", email="alice@example.com"),
    User(id=2, username="bob", email="bob@example.com"),
    # User(id=3, username="johnny", email="alice@example.com"), # duplicate email, result: ValueError exception
]

keys = ['id', 'username','email']

index = ModelIndex(
    users,
    keys
)

print(index.get("id", 1))
print(index.get("username", "bob"))
print(index.get("email", "unknown"))                      # not valid email, result: None

print(index.all())
index.remove("username", "bob")
print(index.all())

new_user = User(id=4, username="alice1", email="alice1@example.com")
index.add(new_user)

bad_user = OtherUser(id=4, username="alice2", email="alice2@example.com", other="this won't work")
index.add(bad_user)