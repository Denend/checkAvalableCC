import requests

headers = {
    'authority': 'api.cyberconnect.dev',
    'accept': '*/*',
    'accept-language': 'uk-UA,uk;q=0.9,en-US;q=0.8,en;q=0.7',
    'authorization': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiZjI1ZTlhYjQtYmU3OS00ZWY1LTgzODItYzkwZTZjYmNkZDc4IiwidGVtcF91c2VyIjpmYWxzZSwiZXhwIjoxNjkwMzAyOTgzLCJpYXQiOjE2ODk2OTgxODMsImlzcyI6ImxpbmszLnRvIn0.8D0jb_2uCSz3vHT6xmWDHg5Pkh2f4uJqiTUrSItn81Y',
    'content-type': 'application/json',
    'origin': 'https://link3.to',
    'referer': 'https://link3.to/',
    'sec-ch-ua': '"Chromium";v="110", "Not A(Brand";v="24", "Google Chrome";v="110"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'cross-site',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36',
}

open(f"result.txt", "w").close()
result = open(f"result_{headers['authorization'][:-10]}.txt", "a")

def get_past_events(after: int = None):

    json_data = {
        'query': '\n    query getPastEvents($first: Int, $after: String, $hasRecap: Boolean) {\n  pastEvents(first: $first, after: $after, hasRecap: $hasRecap) {\n    pageInfo {\n      ...PageInfo\n    }\n    list {\n      id\n      info\n      title\n      posterUrl\n      startTimestamp\n      endTimestamp\n      registrantsCount\n      registerStatus\n      status\n      recap\n      organizer {\n        ...Organizer\n      }\n      lightInfo {\n        hasRaffle\n        hasW3ST\n      }\n    }\n  }\n}\n    \n    fragment PageInfo on PageInfo {\n  startCursor\n  endCursor\n  hasNextPage\n  hasPreviousPage\n}\n    \n\n    fragment Organizer on Organization {\n  twitterId\n  id\n  followersCount\n  verification\n  currentAccess\n  lightInfo {\n    isFollowing\n    displayName\n    profilePicture\n    profileHandle\n  }\n}\n    ',
        'variables': {
            'after': '',
        },
        'operationName': 'getPastEvents',
    }

    json_data['variables']['after'] = after
    response = requests.post('https://api.cyberconnect.dev/profile/', headers=headers, json=json_data)
    
    return response.json()['data']['pastEvents']

def get_claim_w3st_status(id: str):

    json_data = {
        'query': '\n    query getClaimW3stStatus($id: ID!) {\n  event(id: $id) {\n    organizer {\n      ...Organizer\n    }\n    w3st {\n      eligible {\n        unclaimed\n        claiming\n        claimed\n        stayTime\n        readyToClaim\n        claimedByOther\n        firstClaim\n        requirements {\n          eligible\n          requirement {\n            type\n            value\n          }\n        }\n      }\n    }\n  }\n}\n    \n    fragment Organizer on Organization {\n  twitterId\n  id\n  followersCount\n  verification\n  currentAccess\n  lightInfo {\n    isFollowing\n    displayName\n    profilePicture\n    profileHandle\n  }\n}\n    ',
        'variables': {
            'id': '',
        },
        'operationName': 'getClaimW3stStatus',
    }

    json_data['variables']['id'] = id
    response = requests.post('https://api.cyberconnect.dev/profile/', headers=headers, json=json_data)
    if not response.json()['data']['event']['w3st']:
        return None
    return response.json()['data']['event']['w3st']['eligible']


past_events = []
after = None
x = 0

while True:
    x += 1
    data = get_past_events(after)

    if data['list'][-1]['endTimestamp'] < 1686963601:
        past_events += data['list']
        print("End of events", data['list'][-1]['endTimestamp'])
        break

    print(data['pageInfo']['hasNextPage'])

    if not data['pageInfo']['hasNextPage']:
        break
    past_events += data['list']
    after = data['pageInfo']['endCursor']

    if x == 10:
        break
try:
    for event in past_events:

        w3st = get_claim_w3st_status(event['id'])

        if not w3st:
            continue
        for requirement in w3st['requirements']:
            requirement = requirement['requirement']
            if not requirement.get("type"):
                print(w3st)
                continue
            if requirement["type"] == "STAY":
                if w3st['stayTime'] >= requirement['value']:
                    print(f"Stay time is enough for this w3st [{event['id']} - {event['title']}]")
                    result.write(f"https://link3.to/e/{event['id']}\n")
                    continue

except KeyboardInterrupt:
    print("KeyboardInterrupt")
    result.close()
    exit(0)
except Exception as e:
    print(e)
    result.close()
    exit(0)