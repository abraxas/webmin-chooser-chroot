#!/usr/bin/env bash
# H21 lab overlay on the shared webmin-lab:2.670 image.
# Limited chooser root is /lab/jail. The witness is a filename outside that jail.
set -euo pipefail

JAIL="/lab/jail"
WITNESS="WEBMIN-H21-CHOOSER"
LIMITED_USER="limited"
LIMITED_PASS="limitedpass"
CONF="/etc/webmin/miniserv.conf"
USERS_FILE="/etc/webmin/miniserv.users"
ACL_FILE="/etc/webmin/webmin.acl"
USER_ACL="/etc/webmin/${LIMITED_USER}.acl"

mkdir -p "${JAIL}"
printf 'inside-jail\n' > "${JAIL}/allowed.txt"
# Filename-only plant: chooser lists names, sizes, mtimes, not bodies.
: > "/lab/${WITNESS}"
chmod 755 /lab "${JAIL}"
chmod 644 "${JAIL}/allowed.txt" "/lab/${WITNESS}"

if ! grep -q "^${LIMITED_USER}:" "${USERS_FILE}"; then
  hash="$(perl -e 'print crypt($ARGV[0], q{$6$webminh21salt$})' "${LIMITED_PASS}")"
  if [[ -z "${hash}" || "${hash}" == *'*'* ]]; then
    echo "limited-crypt-failed" >&2
    exit 1
  fi
  printf '%s:%s:0\n' "${LIMITED_USER}" "${hash}" >> "${USERS_FILE}"
fi

if ! grep -q "^${LIMITED_USER}:" "${ACL_FILE}"; then
  printf '%s:\n' "${LIMITED_USER}" >> "${ACL_FILE}"
fi

cat > "${USER_ACL}" <<'EOF'
root=/lab/jail
fileunix=root
uedit_mode=0
gedit_mode=0
rpc=0
feedback=0
readonly=0
nodot=0
webminsearch=0
download_address_mode=public
EOF

chmod 600 "${USERS_FILE}" "${ACL_FILE}" "${USER_ACL}"

grep -q '^ssl_enforce=0$' "${CONF}" || printf '\nssl_enforce=0\n' >> "${CONF}"
grep -q '^no_pam=' "${CONF}" || printf 'no_pam=1\n' >> "${CONF}"
grep -q '^no_testing_cookie=' "${CONF}" || printf 'no_testing_cookie=1\n' >> "${CONF}"
grep -q '^ipv6=0$' "${CONF}" || sed -i 's/^ipv6=.*/ipv6=0/' "${CONF}"

exec /usr/bin/perl /usr/share/webmin/miniserv.pl --nofork /etc/webmin/miniserv.conf
