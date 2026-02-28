import os
import subprocess
import requests


class NotebookLMClient:
    def __init__(self, project_number: str, location: str = "global"):
        self.project_number = project_number
        self.location = location
        self.base = (
            f"https://{location}-discoveryengine.googleapis.com/v1alpha/"
            f"projects/{project_number}/locations/{location}"
        )

    @staticmethod
    def _token() -> str:
        return (
            subprocess.check_output(["gcloud", "auth", "print-access-token"], text=True)
            .strip()
        )

    def _headers(self):
        return {
            "Authorization": f"Bearer {self._token()}",
            "Content-Type": "application/json",
        }

    def create_notebook(self, display_name: str):
        url = f"{self.base}/notebooks"
        body = {"displayName": display_name}
        return requests.post(url, headers=self._headers(), json=body, timeout=60)

    def add_source_url(self, notebook_id: str, source_url: str):
        # Endpoint shape follows NotebookLM Enterprise source management docs.
        url = f"{self.base}/notebooks/{notebook_id}/sources"
        body = {
            "webSource": {
                "url": source_url,
            }
        }
        return requests.post(url, headers=self._headers(), json=body, timeout=60)

    def create_audio_overview(self, notebook_id: str, source_ids=None, episode_focus="", language_code="en-US"):
        url = f"{self.base}/notebooks/{notebook_id}/audioOverviews"
        body = {
            "languageCode": language_code,
            "episodeFocus": episode_focus,
        }
        if source_ids:
            body["sourceIds"] = [{"id": s} for s in source_ids]
        return requests.post(url, headers=self._headers(), json=body, timeout=60)

    def get_audio_overview(self, notebook_id: str, audio_overview_id: str):
        url = f"{self.base}/notebooks/{notebook_id}/audioOverviews/{audio_overview_id}"
        return requests.get(url, headers=self._headers(), timeout=60)
