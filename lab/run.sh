#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
export COMPOSE_PROJECT_NAME="${COMPOSE_PROJECT_NAME:-webminh21}"
export PYTHONUNBUFFERED=1
export WEBMIN_URL="${WEBMIN_URL:-http://127.0.0.1:18510}"

LABEL="WEBMIN-H21-CHOOSER"
WITNESS="WEBMIN-H21-CHOOSER"
IMAGE="webmin-lab:2.670"
LOCK="/tmp/webmin-lab-image.lock"
PIN_COMMIT="3a2b2b8671c0669c129f5275b3dd1853106ae02b"
PIN_TAG="2.670"
REPO_URL="${WEBMIN_SRC_URL:-https://github.com/webmin/webmin.git}"
WEBMIN_SRC="${WEBMIN_SRC:-$(pwd)/src}"

chmod +x poc.py entrypoint.sh

down() {
  echo "== docker compose down -v =="
  docker compose -p "${COMPOSE_PROJECT_NAME}" down -v --remove-orphans || true
}

fail_setup() {
  local reason="$1"
  echo "FAIL ${LABEL} ${reason} ${WITNESS}" | tee poc-last-run.txt
  docker compose -p "${COMPOSE_PROJECT_NAME}" logs --no-color --tail=80 webmin || true
  exit 1
}

ensure_pin() {
  if [[ ! -f "${WEBMIN_SRC}/setup.sh" || ! -f "${WEBMIN_SRC}/chooser.cgi" ]]; then
    echo "== git clone ${REPO_URL} ${PIN_TAG} =="
    rm -rf "${WEBMIN_SRC}"
    git clone --branch "${PIN_TAG}" --depth 1 "${REPO_URL}" "${WEBMIN_SRC}" \
      || fail_setup "clone-failed"
  fi
  if [[ -d "${WEBMIN_SRC}/.git" ]]; then
    local got
    got="$(git -C "${WEBMIN_SRC}" rev-parse HEAD)"
    if [[ "${got}" != "${PIN_COMMIT}" ]]; then
      echo "webmin-pin-mismatch got=${got} want=${PIN_COMMIT}"
      fail_setup "pin-mismatch"
    fi
  fi
  local version
  version="$(tr -d '[:space:]' < "${WEBMIN_SRC}/version")"
  if [[ "${version}" != "${PIN_TAG}" ]]; then
    echo "webmin-version-mismatch ${version}"
    fail_setup "webmin-pin-mismatch"
  fi
  echo "IOC pin=${PIN_TAG} commit=${PIN_COMMIT} src=${WEBMIN_SRC}"
}

ensure_image() {
  python3 - "${LOCK}" "${IMAGE}" "${WEBMIN_SRC}" "$(pwd)/Dockerfile" <<'PY'
import fcntl
import os
import subprocess
import sys
import tempfile

lock_path, image, src, dockerfile = sys.argv[1:5]
os.makedirs(os.path.dirname(lock_path) or ".", exist_ok=True)
fd = os.open(lock_path, os.O_CREAT | os.O_RDWR, 0o666)
fcntl.flock(fd, fcntl.LOCK_EX)
try:
    inspect = subprocess.run(
        ["docker", "image", "inspect", image],
        capture_output=True,
        check=False,
    )
    if inspect.returncode == 0:
        print(f"image-present {image}", flush=True)
        raise SystemExit(0)
    if not os.path.isfile(os.path.join(src, "setup.sh")) or not os.path.isfile(
        os.path.join(src, "chooser.cgi")
    ):
        print(f"webmin-src-missing {src}", flush=True)
        raise SystemExit(1)
    version_path = os.path.join(src, "version")
    with open(version_path, encoding="utf-8") as fh:
        version = fh.read().strip()
    if version != "2.670":
        print(f"webmin-pin-mismatch {src}", flush=True)
        raise SystemExit(1)
    print(f"== docker build {image} (src={src}) ==", flush=True)
    work = tempfile.mkdtemp()
    try:
        tar = os.path.join(work, "webmin-src.tar")
        subprocess.check_call(
            ["tar", "-C", src, "--exclude", ".git", "-cf", tar, "."]
        )
        subprocess.check_call(["cp", dockerfile, os.path.join(work, "Dockerfile")])
        raise SystemExit(subprocess.call(["docker", "build", "-t", image, work]))
    finally:
        subprocess.call(["rm", "-rf", work])
finally:
    fcntl.flock(fd, fcntl.LOCK_UN)
    os.close(fd)
PY
}

trap down EXIT

echo "== py_compile poc.py =="
python3 -m py_compile poc.py

echo "== docker compose down (clean) =="
down

echo "== pin ${PIN_TAG} ${PIN_COMMIT} =="
ensure_pin

echo "== flock ${LOCK} image ${IMAGE} =="
if ! ensure_image; then
  fail_setup "image-build-failed"
fi

echo "== docker compose up =="
up_ok=0
for attempt in $(seq 1 5); do
  if docker compose -p "${COMPOSE_PROJECT_NAME}" up -d --no-build; then
    up_ok=1
    break
  fi
  echo "compose-up-retry attempt=${attempt}"
  sleep 8
  down
done
if [[ "${up_ok}" != 1 ]]; then
  fail_setup "compose-up-failed"
fi

echo "== wait ${WEBMIN_URL}/session_login.cgi =="
ok=0
for i in $(seq 1 90); do
  if python3 - <<'PY'
import urllib.error
import urllib.request

url = "http://127.0.0.1:18510/session_login.cgi"
req = urllib.request.Request(url, method="GET")
try:
    with urllib.request.urlopen(req, timeout=5) as resp:
        body = resp.read().decode("utf-8", "replace")
        raise SystemExit(0 if 'name="user"' in body else 1)
except urllib.error.HTTPError as exc:
    body = exc.read().decode("utf-8", "replace")
    raise SystemExit(0 if 'name="user"' in body else 1)
except (urllib.error.URLError, TimeoutError, OSError):
    raise SystemExit(1)
PY
  then
    ok=1
    echo "webmin-ready attempt=${i}"
    break
  fi
  echo "webmin-wait attempt=${i}"
  sleep 2
done
if [[ "${ok}" != 1 ]]; then
  echo "== compose logs (not ready) =="
  docker compose -p "${COMPOSE_PROJECT_NAME}" logs --no-color --tail=80 || true
  fail_setup "webmin-not-ready"
fi

echo "== poc.py =="
set +e
python3 ./poc.py | tee poc-last-run.txt
rc=${PIPESTATUS[0]}
set -e

if ! tail -n1 poc-last-run.txt 2>/dev/null | grep -qE '^(SUCCESS|FAIL) '; then
  echo "FAIL ${LABEL} poc-exit=${rc} ${WITNESS}" >> poc-last-run.txt
  rc=1
fi

if [[ "${rc}" != 0 ]]; then
  docker compose -p "${COMPOSE_PROJECT_NAME}" logs --no-color --tail=80 webmin || true
fi

exit "${rc}"
