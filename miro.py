import requests
from groq_response import groq_response
from open_api import retrival_openai
import json

def update_miro_content(item_id, content):
    url = f"https://api.miro.com/v2/boards/uXjVKHDu73g%3D/shapes/{item_id}"

    payload = { "data": { "content": content } }
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "authorization": "Bearer eyJtaXJvLm9yaWdpbiI6ImV1MDEifQ_PU_VfNPSYOKuqHigGZu7VPscwVE"
    }

    response = requests.patch(url, json=payload, headers=headers)

def get_connector_mappings():
    url = f"https://api.miro.com/v2/boards/uXjVKHDu73g%3D/connectors"

    headers = {
        "accept": "application/json",
        "authorization": "Bearer eyJtaXJvLm9yaWdpbiI6ImV1MDEifQ_PU_VfNPSYOKuqHigGZu7VPscwVE"
    }

    response = requests.get(url, headers=headers)
    data = response.json()

    mappings = {}
    for connector in data["data"]:
        start_item_id = connector["startItem"]["id"]
        end_item_id = connector["endItem"]["id"]
        mappings[start_item_id] = end_item_id

    return mappings

def get_end_item(start_item_id, connector_mappings):
    if start_item_id in connector_mappings:
        return connector_mappings[start_item_id]
    else:
        return None


def add_shape(content):
    url = "https://api.miro.com/v2/boards/uXjVKHDu73g%3D/shapes"

    payload = {
        "data": {
            "content": content,
            "shape": "round_rectangle"
        },
    }
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "authorization": "Bearer eyJtaXJvLm9yaWdpbiI6ImV1MDEifQ_PU_VfNPSYOKuqHigGZu7VPscwVE"
    }

    response = requests.post(url, json=payload, headers=headers)


def get_tags(tag_id):
    url = f"https://api.miro.com/v2/boards/uXjVKHDu73g%3D/items/{tag_id}/tags"

    headers = {
        "accept": "application/json",
        "authorization": "Bearer eyJtaXJvLm9yaWdpbiI6ImV1MDEifQ_PU_VfNPSYOKuqHigGZu7VPscwVE"
    }

    response = requests.get(url, headers=headers)
    # Check if request was successful
    if response.status_code == 200:
        # Parse the JSON response
        json_response = response.json()
        # Extract the tag ID
        tag_id = json_response['tags'][0]['id']
        return tag_id
    else:
        print("Error:", response.status_code)


def update_shape(item_id, content):
    url = f"https://api.miro.com/v2/boards/uXjVKHDu73g%3D/shapes/{item_id}"
    payload = { "data": { "content": content} }
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "authorization": "Bearer eyJtaXJvLm9yaWdpbiI6ImV1MDEifQ_PU_VfNPSYOKuqHigGZu7VPscwVE"
    }

    response = requests.patch(url, json=payload, headers=headers)


def get_frame_items(frame_id):
    url = f"https://api.miro.com/v2/boards/uXjVKHDu73g%3D/items?parent_item_id={frame_id}&limit=50"
    headers = {
    "accept": "application/json",
    "authorization": "Bearer eyJtaXJvLm9yaWdpbiI6ImV1MDEifQ_PU_VfNPSYOKuqHigGZu7VPscwVE"
    }

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        sticky_notes = data.get("data", [])
        results = []
        connector_mappings = get_connector_mappings()
        for note in sticky_notes:
            note_id = note.get("id")
            note_content = note.get("data", {}).get("content")
            tag = get_tags(note_id)
            if tag == "3458764589120136255":
                end_item_id = get_end_item(note_id, connector_mappings)
                response = groq_response(note_content, "get some detailed information about this user prompt")
                if response:
                    update_shape(end_item_id, response)
            elif tag == "3458764589120455244":
                end_item_id = get_end_item(note_id, connector_mappings)
                response = retrival_openai(note_content, "give step by step hints to solve teh question in the prompt")
                if response:
                    update_shape(end_item_id, response)    
        return None
    else:
        print("Error:", response.status_code)
        return None

#get_frame_items(3458764589119443158)   # 
