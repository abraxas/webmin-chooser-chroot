FROM debian:bookworm-slim

LABEL version="2.670" \
      webmin.commit="3a2b2b8671c0669c129f5275b3dd1853106ae02b" \
      lab="WEBMIN-H21-CHOOSER"

ENV DEBIAN_FRONTEND=noninteractive \
    LANG=C \
    WEBMIN_CONFIG=/etc/webmin \
    WEBMIN_VAR=/var/webmin \
    PERLLIB=/usr/share/webmin \
    LIBROOT=/usr/share/webmin

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        ca-certificates \
        hostname \
        openssl \
        perl \
    && ln -sf /usr/bin/perl /usr/local/bin/perl \
    && rm -rf /var/lib/apt/lists/*

COPY webmin-src.tar /tmp/webmin-src.tar

# Shared Webmin 2.670 image. noperlpath is safe: miniserv evals CGI when the
# shebang ends in /perl. nostart keeps PID 1 as the later --nofork miniserv.
RUN mkdir -p /usr/share/webmin \
    && tar -xf /tmp/webmin-src.tar -C /usr/share/webmin \
    && rm -f /tmp/webmin-src.tar \
    && test -s /usr/share/webmin/version \
    && grep -qx '2.670' /usr/share/webmin/version \
    && cd /usr/share/webmin \
    && config_dir=/etc/webmin \
       var_dir=/var/webmin \
       perl=/usr/bin/perl \
       autoos=3 \
       port=10000 \
       login=root \
       password=labroot \
       ssl=0 \
       atboot=0 \
       noperlpath=1 \
       nostart=1 \
       noportcheck=1 \
       nochown=1 \
       nouninstall=1 \
       nopostinstall=1 \
       ./setup.sh \
    && grep -q '^port=10000$' /etc/webmin/miniserv.conf \
    && grep -q '^ssl=0$' /etc/webmin/miniserv.conf \
    && test -s /etc/webmin/miniserv.users \
    && sed -i \
        -e 's/^syslog=.*/syslog=0/' \
        -e 's/^ipv6=.*/ipv6=0/' \
        -e 's/^ssl_enforce=.*/ssl_enforce=0/' \
        /etc/webmin/miniserv.conf \
    && grep -q '^ssl_enforce=0$' /etc/webmin/miniserv.conf \
        || printf '\nssl_enforce=0\n' >> /etc/webmin/miniserv.conf \
    && grep -q '^no_pam=' /etc/webmin/miniserv.conf \
        || printf 'no_pam=1\n' >> /etc/webmin/miniserv.conf \
    && grep -q '^no_testing_cookie=' /etc/webmin/miniserv.conf \
        || printf 'no_testing_cookie=1\n' >> /etc/webmin/miniserv.conf

EXPOSE 10000

CMD ["/usr/bin/perl", "/usr/share/webmin/miniserv.pl", "--nofork", "/etc/webmin/miniserv.conf"]
