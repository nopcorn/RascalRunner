import requests
import logging

class GitlabWrapper:
    def __init__(self, token, mode, base_url):
        self._token = token
        self.mode = mode
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.session.headers.update({"PRIVATE-TOKEN": self._token})

    def api_call(self, method, endpoint, **kwargs):
        if endpoint.startswith("http"):
            url = endpoint
        else:
            url = f"{self.base_url}{endpoint}"
        logging.debug(f"API {method} {url}")
        resp = self.session.request(method, url, **kwargs)
        if resp.status_code not in [200, 201, 204]:
            logging.warning(f"API call {method} {url}: {resp.status_code} {resp.text}")
        resp.raise_for_status()
        return resp

    def get_current_user(self):
        return self.api_call("GET", "/user").json()

    def list_projects(self):
        resp = self.api_call("GET", "/projects?membership=true&simple=true&per_page=100")
        return resp.json()
