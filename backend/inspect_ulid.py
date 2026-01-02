import ulid
u = ulid.ULID()
print(f"Type: {type(u)}")
print(dir(u))
try:
    print(f"u.uuid: {u.uuid}")
except Exception as e:
    print(f"u.uuid failed: {e}")

try:
    print(f"u.to_uuid(): {u.to_uuid()}")
except Exception as e:
    print(f"u.to_uuid() failed: {e}")