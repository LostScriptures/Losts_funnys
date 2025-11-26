from http.cookiejar import MozillaCookieJar, Cookie
from requests.cookies import RequestsCookieJar, create_cookie
from typing import Any
import requests
import argparse
import base64
import atexit
import re

parser = argparse.ArgumentParser(
    prog="vrc",
    usage="%(prog)s [options] <command> [args]",
    description="Command-line tool for interacting with the VRChat API.",
    exit_on_error=False,
    add_help=False
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
subparsers = parser.add_subparsers(
    title="Available commands",
    help="Use '%(prog)s <command> --help' for more information on a command.",
    dest="command"
)

# HELP
help = subparsers.add_parser("help", help="Show this help message", exit_on_error=False)

# LOGIN
log_in = subparsers.add_parser("login", help="Authenticate with the VRChat API", exit_on_error=False)
log_in.add_argument("username", help="VRChat username")
log_in.add_argument("password", help="VRChat password")

# GET USER INFO
user = subparsers.add_parser("user", help="Fetch user info", exit_on_error=False)
user.add_argument("user_id", help="VRChat user ID")

# LIST FRIENDS
friends = subparsers.add_parser("friends", help="List your friends", exit_on_error=False)
friends.add_argument(
    "--online", action="store_true",
    help="Show only online friends"
)

# WORLD INFO
world = subparsers.add_parser("world", help="Fetch world info", exit_on_error=False)
world.add_argument("world_id", help="VRChat world ID")

# DOWNLOAD AVATAR / WORLD IMAGE (example)
download = subparsers.add_parser("download", help="Download VRChat resources", exit_on_error=False)
download.add_argument("resource_type", choices=["avatar", "world"])
download.add_argument("resource_id", help="ID of the resource to download")
download.add_argument("--output", "-o", help="Output filename/path")

# Make sure parsed_args always has the common attributes (so callers can safely
# access them even if a different subcommand was chosen).
parser.set_defaults(
    command=None,
    username=None,
    password=None,
    user_id=None,
    online=False,
    world_id=None,
    resource_type=None,
    resource_id=None,
    output=None,
)

def at_exit(mozilla: MozillaCookieJar, session: requests.Session):
    """Saves cookies on exit"""
    for c in session.cookies:
        # http.cookiejar.Cookie expects many positional arguments:
        # (version, name, value, port, port_specified, domain, domain_specified,
        #  domain_initial_dot, path, path_specified, secure, expires, discard,
        #  comment, comment_url, rest, rfc2109)
        mozilla.set_cookie(
            Cookie(
                0,
                c.name,
                c.value,
                None,
                False,
                c.domain or "",
                bool(c.domain),
                bool(c.domain and c.domain.startswith(".")),
                c.path or "/",
                bool(c.path),
                bool(getattr(c, "secure", False)),
                getattr(c, "expires", None),
                False,
                None,
                None,
                getattr(c, "rest", {}) or {},
                False
            )
        )

    try:
        mozilla.save(ignore_discard=True, ignore_expires=True)
    except Exception as e:
        # Best-effort: if saving fails, print a warning but don't crash at exit
        print("Warning: failed to save cookies:", e)

def make_persistent_session(cookie_file="cookies.txt"):
    """Creates a requests session that persists cookies to a file"""
    session = requests.Session()
    mozilla = MozillaCookieJar(cookie_file)

    try:
        mozilla.load(ignore_discard=True, ignore_expires=True)
    except FileNotFoundError:
        pass

    requests_jar = RequestsCookieJar()
    for c in mozilla:
        requests_jar.set_cookie(create_cookie(
            name=c.name,
            value=c.value,
            domain=c.domain,
            path=c.path,
            expires=c.expires
        ))

    session.cookies = requests_jar

    atexit.register(lambda: at_exit(mozilla, session))
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

def login(username: str | None = None, password: str | None = None) -> None:
    """Does the whole login sequence (also 2fa if needed)"""
    if username is None:
        username = input("Username: ").strip()
    if password is None:
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

def display_friends(only_online: bool = False) -> None:
    if only_online:
        friends = [(f["displayName"], get_world_by_id(f["location"])) for f in get_friends() if f["location"] != "offline"]
    else:
        friends = [(f["displayName"], get_world_by_id(f["location"])) for f in get_friends()]

    friends.sort(key=lambda x: x[0])

    for friend in friends:
        print(f"{friend[0]} ({friend[1]})")

def get_user_by_id(user_id: str) -> Any:
    """Returns user info by user ID"""
    r = session.get(f"{API}/users/{user_id}")

    if r.status_code == 200:
        return r.json()

# ---------------------------------------------
#  USAGE
# ---------------------------------------------
def main(args: str) -> None:
    try:
        parsed_args = parser.parse_args(args.split())
    except argparse.ArgumentError as e:
        print(e.message)
        return
    
    # Ensure we have an active session. If not, try using provided
    # credentials (for `login` command), otherwise prompt for login.
    valid = is_session_valid()
    if not valid and parsed_args.command not in ["help", None]:
        if parsed_args.command == "login":
            # login() will prompt if username/password are None
            login(parsed_args.username, parsed_args.password)
        else:
            # For commands that require auth, prompt the user to login
            print("No valid session found — please login first.")
            login()

    elif valid:
        print("Found valid auth cookie")
        user = get_current_user()
        print("Logged in as:", user["username"])

    # Dispatch based on selected subcommand
    cmd = parsed_args.command
    if cmd == "friends":
        display_friends(only_online=bool(parsed_args.online))

    elif cmd == "user":
        user_info = get_user_by_id(parsed_args.user_id)
        print("User info:", user_info)

    elif cmd == "login":
        # login() already performed above if necessary — just confirm
        print("Login flow complete")

    elif cmd == "world":
        name = get_world_by_id(parsed_args.world_id)
        print("World name:", name)

    elif cmd == "download":
        # Currently a minimal example implementation — expand if necessary
        print(
            f"Requested download: type={parsed_args.resource_type}, id={parsed_args.resource_id}, output={parsed_args.output}"
        )

    if cmd == "help" or cmd is None:
        parser.print_help()


def do_vrc(self, args):
    """
    A tool to interact with the VRChat API
    """
    main(args)

def help_vrc(self):
    parser.print_usage()


if __name__ == "__main__":
    import sys
    main(" ".join(sys.argv[1:]))