import json

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

def entry_navigation_json():
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
                }
            ]
        })