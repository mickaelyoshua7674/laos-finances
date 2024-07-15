import uuid

o = {
    "name": "Unknown",
    "parent": "Uncategorized",
    "uuid": "06335e84-2872-4914-8c5d-3ed07d2a2f16"
}
print(str(uuid.UUID(o["uuid"])))
print(uuid.UUID(o['uuid']).hex)