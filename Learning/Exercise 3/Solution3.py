import json

file_status = {"file_name": "data.csv", "size_bytes": 0, "is_empty": True}
file_ = json.dumps(file_status)
print(type(file_))

raw_api_payload = '{"response": "Folder organized", "items_moved": 12}'
raw_ = json.loads(raw_api_payload)

print(type(raw_['items_moved']))
print(raw_['items_moved'])