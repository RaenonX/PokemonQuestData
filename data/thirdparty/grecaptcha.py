import os
import json
import requests

class google_recaptcha:
    API_URL = "https://www.google.com/recaptcha/api/siteverify"

    def __init__(self):
        self._secret = os.environ.get("GR_SECRET")

        if self._secret is None:
            print("Specify 'GR_SECRET' (Google Recaptcha secret).")

        self._disabled = self._secret is None

    def verify(self, recaptcha_response):
        if self._disabled:
            print("Verification not perform because no reCAPTCHA secret was provided.")
            return True

        r = requests.post(google_recaptcha.API_URL, data={'secret': self._secret, 'response': recaptcha_response})
        return json.loads(r.text)["success"]