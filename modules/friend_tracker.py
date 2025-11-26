from http.cookiejar import MozillaCookieJar
from typing import Any
import requests
import argparse
import base64
import atexit
import re

parser = argparse.ArgumentParser(
    prog="vrc",
    usage="%(progs)s <command> [args]",
    description="Command-line tool for interacting with the VRChat API.",
    exit_on_error=False,
)

# Global options (apply to all commands)
parser.add_argument(
    "-v", "--verbose",
    action="store_true",
    help="Enable verbose output"
)

# -------------------------
# SUBCOMMANDS
# -------------------------
subparsers = parser.add_subparsers(required=True)

# LOGIN
log_in = subparsers.add_parser("login", help="Authenticate with the VRChat API")
log_in.add_argument("username", help="VRChat username")
log_in.add_argument("password", help="VRChat password")

# GET USER INFO
user = subparsers.add_parser("user", help="Fetch user info")
user.add_argument("user_id", help="VRChat user ID")

# LIST FRIENDS
friends = subparsers.add_parser("friends", help="List your friends")
friends.add_argument(
    "--online", action="store_true",
    help="Show only online friends"
)

# WORLD INFO
world = subparsers.add_parser("world", help="Fetch world info")
world.add_argument("world_id", help="VRChat world ID")

# DOWNLOAD AVATAR / WORLD IMAGE (example)
download = subparsers.add_parser("download", help="Download VRChat resources")
download.add_argument("resource_type", choices=["avatar", "world"])
download.add_argument("resource_id", help="ID of the resource to download")
download.add_argument("--output", "-o", help="Output filename/path")

def make_persistent_session(cookie_file="cookies.txt"):
    session = requests.Session()
    jar = MozillaCookieJar(cookie_file)
    session.cookies = jar

    try:
        jar.load(ignore_discard=True, ignore_expires=True)
    except FileNotFoundError:
        pass

    atexit.register(lambda: jar.save(ignore_discard=True, ignore_expires=True))
    return session

API = "https://api.vrchat.cloud/api/1"

session = make_persistent_session()

session.headers.update({
    "User-Agent": "Losts_funnys/1.0 (LostPlayer; contact: lost.player.game@gmail.com)"
})


def basic_auth_header(username: str, password: str) -> dict[str, str]:
    """Generates basic auth token"""
    token = f"{username}:{password}".encode()
    b64 = base64.b64encode(token).decode()
    return {"Authorization": f"Basic {b64}"}

def check_token(token: str) -> str | None:
    """Checks if a given token is valid"""
    r = session.get(f"{API}/auth", cookies={
        "auth": f"{token}"
    })


    if not r.json()["ok"]:
        return None
    
    print(f"Saved cookie valid? ", r.json()["ok"])
    return token

def login_step1(username: str, password: str) -> Any:
    """
    First login attempt: will succeed immediately if no 2FA is enabled,
    otherwise will respond with {"requiresTwoFactorAuth": [...]}.
    """
    headers = basic_auth_header(username, password)
    print("Attempting initial login...")

    r = session.get(f"{API}/auth/user", headers=headers)

    data = r.json()

    if "requiresTwoFactorAuth" in data:
        print("2FA required:", data["requiresTwoFactorAuth"])
        return data
    
    if r.status_code == 200:
        print("Logged in without 2FA.")
        return data

    raise Exception("Login failed:", data)

def send_2fa_code(code: str, method: str ="totp"):
    """
    method can be: "emailotp" or "totp"
    """
    print(f"Sending 2FA code ({method})...")

    r = session.post(
        f"{API}/auth/twofactorauth/{method}/verify",
        json={"code": code},
        headers={
            "Content-Type": "application/json"
        }
    )

    if r.status_code != 200:
        raise Exception("2FA failed:", r.text)

    print("2FA successful.")
    return r.json()

def get_current_user() -> Any:
    """ Uses active session cookie to fetch authenticated user """
    r = session.get(f"{API}/auth/user")
    return r.json()

def is_session_valid() -> bool:
    """Checks it the current requests session is still valid"""
    r = session.get(f"{API}/auth/user")
    return r.status_code == 200

def login() -> None:
    """Does the whole login sequence (also 2fa if needed)"""
    username = input("Username: ").strip()
    password = input("Password: ").strip()

    step1 = login_step1(username, password)
        
    if "requiresTwoFactorAuth" in step1:
        # VRChat returns a list such as ["emailotp", "totp"]
        methods = step1["requiresTwoFactorAuth"]
        print("Available 2FA methods:", methods)

        # Pick one:
        chosen = "totp" if "totp" in methods else "emailotp"

        code = input(f"Enter your {chosen} 6-digit code: ")
        send_2fa_code(code, chosen)

def get_friends() -> Any:
    """Returns the list of friends"""
    r = session.get(f"{API}/auth/user/friends", params={
        "offset": 0,
        "n": 100,
        "offline": True
    })

    if r.status_code == 200:
        return r.json()
    
def get_world_by_id(id: str) -> Any:
    """Returns the world to the id"""
    if id.startswith("wrld_"):
        id = re.sub(r"^(wrld_.*?)([~:].*)$", r"\1", id)
        r = session.get(f"{API}/worlds/{id}")

        if r.status_code == 200:
            return r.json()["name"]
        else:
            return "Couldn't get name"
    return id

# ---------------------------------------------
#  USAGE
# ---------------------------------------------
def main(args: str) -> None:
    args = parser.parse_args(args)
    
    if not is_session_valid():
        login()
    else:
        print("Found valid auth cookie")

    user = get_current_user()
    print("Logged in as:", user["username"])

    friends = [(f["displayName"], get_world_by_id(f["location"])) for f in get_friends() if f["location"] != "offline"]
    friends.sort(key=lambda x: x[0])

    for friend in friends:
        print(f"{friend[0]} ({friend[1]})")

def do_vrc(self, args):
    """
    A tool to interact with the VRChat API
    """
    main(args)

def help_vrc(self):
    parser.print_help()


if __name__ == "__main__":
    main("")