import json
import hmac

from quarry.types.uuid import UUID


def entry_json(current, total):
    return json.dumps({
            "text": '\n\n\nEntry ',
            "bold": True,
            "color": "gold",
            "extra": [
                {
                    "text": "#",
                    "bold": False,
                },
                {
                    "text": '{}/{}'.format(current, total),
                    "bold": True,
                }
            ]
        })

def entry_navigation_json(uuid: UUID, secret):
    token = hmac.new(key=str.encode(secret), msg=uuid.to_bytes(), digestmod="sha256")
    url ='https://minecraft.rtgame.co.uk/detailing/?uuid={}&token={}'.format(uuid.to_hex(False), token.hexdigest())
    print(url)

    return json.dumps({
            "text": "\n",
            "color": "gold",
            "extra": [
                {
                    "text": "[Prev Entry]",
                    "bold": True,
                    "clickEvent": {
                        "action": "run_command",
                        "value": "/prev"
                    },
                },
                {
                    "text": " ",
                },
                {
                    "text": "[Next Entry]",
                    "bold": True,
                    "clickEvent": {
                        "action": "run_command",
                        "value": "/next"
                    }
                },
                {
                    "text": "\n\n"
                },
                {
                    "text": "[Cast your Votes]",
                    "bold": True,
                    "color": "aqua",
                    "clickEvent": {
                        "action": "open_url",
                        "value": url
                    }
                },
                {
                    "text": "\n\n"
                }
            ]
        })