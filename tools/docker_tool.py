import os
import requests

DOCKERHUB_USER  = os.getenv("DOCKERHUB_USERNAME", "")
DOCKERHUB_TOKEN = os.getenv("DOCKERHUB_TOKEN", "")
BASE_URL        = "https://hub.docker.com/v2"


def get_repo_tags(image: str) -> list:
    url      = f"{BASE_URL}/repositories/{image}/tags?page_size=5"
    response = requests.get(url)
    if response.status_code == 200:
        return [{
            "name":       t.get("name"),
            "last_pushed": t.get("tag_last_pushed"),
            "size":       t.get("full_size"),
        } for t in response.json().get("results", [])]
    return []


def get_image_info(image: str) -> dict:
    url      = f"{BASE_URL}/repositories/{image}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return {
            "name":        data.get("name"),
            "description": data.get("description"),
            "pull_count":  data.get("pull_count"),
            "star_count":  data.get("star_count"),
            "last_updated": data.get("last_updated"),
        }
    return {"status": "image not found or private"}


def check_image_exists(image: str, tag: str = "latest") -> bool:
    url      = f"{BASE_URL}/repositories/{image}/tags/{tag}"
    response = requests.get(url)
    return response.status_code == 200


print("**== Docker Tool loaded ==**")
