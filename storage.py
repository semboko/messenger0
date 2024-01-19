from redis import Redis
from datetime import datetime
from pickle import dumps, loads
from time import sleep
from utils import server_get


class LocalStorage(dict):
    def signup(self):
        print("Saving login&password")

        server_get("/signup", {
            "login": self["login"],
            "password1": self["password"],
            "password2": self["password"],
        })

        res = server_get("/login", {
            "login": self["login"],
            "password": self["password"],
        })

        self["token"] = res.text

        token_file = open("token.txt", "w")
        token_file.write(res.text)
        token_file.close()

        res = server_get("/broadcast_url", {
            "session_id": self["token"],
        })

        rhost = res.json()["host"]
        rport = res.json()["port"]
        channel = res.json()["channel_name"]

        self["redis"] = Redis(host=rhost, port=rport)
        self["broadcast_channel"] = channel
        self["is_authorized"] = True

    def send_message(self):
        if self.get("current_message") == "":
            return
        current_dt = datetime.now().strftime("%H:%M %m-%d-%Y")
        # self["messages"].append((self["login"], self["current_message"], datetime.now().strftime("%H:%M %m-%d-%Y")))

        data = (self["login"], self["current_message"], current_dt)
        self["queue"].append(dumps(data))

        # result = redis.publish("broadcast", dumps(data))
        # print(result)
        self["current_message"] = ""

    def get_contacts(self):
        res = server_get("/contacts", {"session_id": self["token"]})
        if res.status_code != 200:
            print(res.text)

        data = res.json()
        print(data)

        self["contacts"] = data

    def validate_token(self) -> bool:
        try:
            server_get("/token/validate", {"token": self["token"]})
            return True
        except Exception:
            return False

    def get_contact_hints(self):
        res = server_get("/search", {
            "session_id": self["token"],
            "login": local_storage["search_input"]
        })
        if res.status_code != 200:
            print(res.text)

        data = res.json()
        print(data)

        self["contact_hints"] = data

    def message_sender(self, app):
        while not app._exit:
            redis = self["redis"]
            if redis is None:
                sleep(1)
                continue
            if len(self["queue"]) > 0:
                data = self["queue"].pop(0)
                redis.publish(self["broadcast_channel"], data)

    def add_friend(self, friend_id: str) -> None:
        server_get("/add_contact", {
            "login": friend_id,
            "session_id": self["token"],
        })
        self.get_contacts()

    def receive_messages(self, app):
        while self["redis"] is None:
            if app._exit:
                return
            sleep(1)
        redis = self["redis"]
        listener = redis.pubsub()
        listener.subscribe(self["broadcast_channel"])
        while not app._exit:
            while msg := listener.get_message(ignore_subscribe_messages=True):
                data = loads(msg["data"])
                self["messages"].append(data)
            sleep(1)

    # def is_authorized(self):
    #     response = redis.get("login_" + self["login"])
    #     print(response)
    #     return response is not None


# For imports
local_storage = LocalStorage()

local_storage["redis"] = None
local_storage["is_authorized"] = False
local_storage["queue"] = []
local_storage["messages"] = []
local_storage["contacts"] = []
local_storage["contact_hints"] = []
