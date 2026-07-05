import base64
import json
import random
import string

import requests


def encrypt_payload(payload_dict: dict, key: str) -> str:
	json_str = json.dumps(payload_dict, separators=(",", ":"))

	json_bytes = json_str.encode("utf-8")
	key_bytes = key.encode("utf-8")
	key_len = len(key_bytes)

	xor_bytes = bytearray()

	for i in range(len(json_bytes)):
		xor_byte = json_bytes[i] ^ key_bytes[i % key_len]
		xor_bytes.append(xor_byte)

	hex_list = [f"{b:x}" for b in xor_bytes]
	hex_str = ",".join(hex_list)

	b64_encoded = base64.b64encode(hex_str.encode("utf-8")).decode("utf-8")

	random_char = random.choice(string.ascii_letters)
	return random_char + b64_encoded


session = requests.session()
session.headers.update({
	"sec-ch-ua": "\"Google Chrome\";v=\"149\", \"Chromium\";v=\"149\", \"Not)A;Brand\";v=\"24\"",
	"sec-ch-ua-mobile": "?1",
	"sec-ch-ua-platform": "\"iOS\"",
	"upgrade-insecure-requests": "1",
	"user-agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 18_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.5 Mobile/15E148 Safari/604.1",
	"accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
	"sec-fetch-site": "none",
	"sec-fetch-mode": "navigate",
	"sec-fetch-user": "?1",
	"sec-fetch-dest": "document",
	"accept-encoding": "gzip, deflate, br, zstd",
	"accept-language": "ru-RU,ru;q=0.9",
	"priority": "u=0, i"
})

response = session.get(url="https://www.wildberries.ru")
print(response.status_code, response.text)

session.headers.update({
	"x-wb-antibot-sdk-version": "js-front-mobile/3.0.5",
	"x-wb-antibot-key": response.text.split("data-site-key=\"")[1].split("\"")[0]
})

response = session.post(url="https://www.wildberries.ru/__wbaas/challenges/antibot/api/v1/find-frontend-settings").json()
print(response)

solver_version = response["solverPath"].split("_v")[1].split(".js")[0]
if solver_version != "1.0.7":
	raise ValueError("Working with solver v1.0.7")

response = session.post(url="https://www.wildberries.ru/__wbaas/challenges/antibot/api/v1/create-token", json={}).json()
payload = response["challenge"]["payload"]
payload_raw = base64.b64decode(payload[1:]).decode()

fp = json.loads(base64.b64decode(payload_raw.split(".")[1]).decode())
fp_id = fp["id"]

print(f"{fp_id=}")

fingerprint = json.loads(open(r"fingerprint.json").read())

response = session.post(
	url="https://www.wildberries.ru/__wbaas/challenges/antibot/api/v1/create-token",
	json={
		"challenge": response["challenge"],
		"solution": {
			"payload": encrypt_payload(payload_dict=fingerprint, key=fp_id)
		}
	}
).json()
print(response)

session.cookies.set(name="x_wbaas_token", value=response["secureToken"])

response = session.get("https://www.wildberries.ru")
print(response.status_code)
