import json

pages = [
    json.dumps({
        "text": "",
        "extra": [
            {
                "text": "Missing Role\n\n",
                "bold": True,
                "underlined": True
            },
            {
                "text": "Hi Virtual Lego Gamer.\n\n",
            },
            {
                "text": "Your Discord account is missing the ",
            },
            {
                "text": "Twitch subscriber",
                "color": "#1987ff"
            },
            {
                "text": " role, which is required to play on this server\n\n"
            },
            {
                "text": "To solve this, please follow the steps listed in this book."
            }
        ]
    }),
    json.dumps({
        "text": "",
        "extra": [
            {
                "text": "Solution 1\n\n",
                "bold": True,
                "underlined": True
            },
            {
                "text": "Check your RTGame ",
            },
            {
                "text": "Twitch",
                "color": "#9147ff"
            },
            {
                "text": " subscription.\n\n",
            },
            {
                "text": "twitch.tv/subscriptions\n",
                "color": "#1987ff",
                "underlined": True,
                "clickEvent": {
                    "action": "open_url",
                    "value": "https://www.twitch.tv/subscriptions"
                },
                "hoverEvent": {
                    "action": "show_text",
                    "value": "Click to open this URL in your browser"
                },
            },
            {
                "text": "[Open in browser]\n",
                "color": "#bc23c2",
                "bold": True,
                "clickEvent": {
                    "action": "open_url",
                    "value": "https://www.twitch.tv/subscriptions"
                },
                "hoverEvent": {
                    "action": "show_text",
                    "value": "Click to open this URL in your browser"
                },
            },
            {
                "text": "[Copy link]\n\n",
                "color": "#bc23c2",
                "bold": True,
                "clickEvent": {
                    "action": "copy_to_clipboard",
                    "value": "https://www.twitch.tv/subscriptions"
                },
                "hoverEvent": {
                    "action": "show_text",
                    "value": "Click to copy this URL to your clipboard"
                },
            },
            {
                "text": "Your subscription may have expired. Please renew it if this is the case.",
            }
        ]
    }),
    json.dumps({
        "text": "",
        "extra": [
            {
                "text": "Solution 2\n\n",
                "bold": True,
                "underlined": True
            },
            {
                "text": "Re-join the RTGame",
            },
            {
                "text": " Discord Server.\n\n",
                "color": "#7289da"
            },
            {
                "text": "discord.gg/rtgame\n",
                "color": "#1987ff",
                "underlined": True,
                "clickEvent": {
                    "action": "open_url",
                    "value": "https://discord.gg/rtgame"
                },
                "hoverEvent": {
                    "action": "show_text",
                    "value": "Click to open this URL in your browser"
                },
            },
            {
                "text": "[Open in browser]\n",
                "color": "#bc23c2",
                "bold": True,
                "clickEvent": {
                    "action": "open_url",
                    "value": "https://discord.gg/rtgame"
                },
                "hoverEvent": {
                    "action": "show_text",
                    "value": "Click to open this URL in your browser"
                },
            },
            {
                "text": "[Copy link]\n\n",
                "color": "#bc23c2",
                "bold": True,
                "clickEvent": {
                    "action": "copy_to_clipboard",
                    "value": "https://discord.gg/rtgame"
                },
                "hoverEvent": {
                    "action": "show_text",
                    "value": "Click to copy this URL to your clipboard"
                },
            },
            {
                "text": "You must remain in the Discord server after linking, otherwise we cannot verify your subscription status",
            }
        ]
    }),
    json.dumps({
        "text": "",
        "extra": [
            {
                "text": "Solution 3\n\n",
                "bold": True,
                "underlined": True
            },
            {
                "text": "Check your ",
            },
            {
                "text": "Twitch ",
                "color": "#9147ff"
            },
            {
                "text": "connection in ",
            },
            {
                "text": "Discord\n\n",
                "color": "#7289da"
            },
            {
                "text": "Quick tutorial:\n"
            },
            {
                "text": "youtu.be/sQnhk2JIeGs\n",
                "color": "#1987ff",
                "underlined": True,
                "clickEvent": {
                    "action": "open_url",
                    "value": "https://youtu.be/sQnhk2JIeGs"
                },
                "hoverEvent": {
                    "action": "show_text",
                    "value": "Click to open this URL in your browser"
                },
            },
            {
                "text": "[Open in browser]\n",
                "color": "#bc23c2",
                "bold": True,
                "clickEvent": {
                    "action": "open_url",
                    "value": "https://youtu.be/sQnhk2JIeGs"
                },
                "hoverEvent": {
                    "action": "show_text",
                    "value": "Click to open this URL in your browser"
                },
            },
            {
                "text": "[Copy link]\n\n",
                "color": "#bc23c2",
                "bold": True,
                "clickEvent": {
                    "action": "copy_to_clipboard",
                    "value": "https://youtu.be/sQnhk2JIeGs"
                },
                "hoverEvent": {
                    "action": "show_text",
                    "value": "Click to copy this URL to your clipboard"
                },
            },
            {
                "text": "Check your ",
            },
            {
                "text": "Twitch",
                "color": "#9147ff"
            },
            {
                "text": " connection still exists in discord, or try deleting it and reconnecting.",
            }
        ]
    }),
    json.dumps({
        "text": "",
        "extra": [
            {
                "text": "Solution 4\n\n",
                "bold": True,
                "underlined": True
            },
            {
                "text": "Wait\n\n",
            },
            {
                "text": "Discord syncs Twitch Subscriptions "
            },
            {
                "text": "once an hour",
                "underlined": True,
            },
            {
                "text": ".\n\nYou may need to wait ",
            },
            {
                "text": "up to an hour",
                "underlined": True,
            },
            {
                "text": " after connecting your Twitch account or subscribing, to receive the ",
            },
            {
                "text": "Twitch Subscriber",
                "color": "#1987ff",
            },
            {
                "text": " role.",
            }
        ]
    }),
    json.dumps({
        "text": "",
        "extra": [
            {
                "text": "Still stuck?\n\n",
                "bold": True,
                "underlined": True
            },
            {
                "text": "Having trouble? Feel free to ask a "
            },
            {
                "text": "@Minecraft Server Mod",
                "color": "#bc23c2",
            },
            {
                "text": " or someone in "
            },
            {
                "text": "#minecraft_server ",
                "color": "#7289da",
                "clickEvent": {
                    "action": "open_url",
                    "value": "https://discordapp.com/channels/176364445797318656/352478300695953408"
                },
                "hoverEvent": {
                    "action": "show_text",
                    "value": "Click to open #minecraft_server in your browser"
                },
            },
            {
                "text": "for help.",
            },
        ]
    })
]
