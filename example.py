from pydantic import BaseModel
from IndexedModel import IndexedModel

class User(BaseModel):
    id: int
    username: str
    email: str

users = [
    User(id=1, username="alice", email="alice@example.com"),
    User(id=2, username="bob", email="bob@example.com"),
    User(id=3, username="johnny", email="alice@example.com"), # duplicate email, result: ValueError exception
]

indexer = IndexedModel(
    users,
    key_funcs={
        "id": lambda u: u.id,
        "username": lambda u: u.username,
        "email": lambda u: u.email,
    }
)

print(indexer.get("id", 1))
print(indexer.get("username", "bob"))
print(indexer.get("email", "unknown"))                      # not valid email, result: None