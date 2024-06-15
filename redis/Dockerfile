FROM public.ecr.aws/docker/library/debian:12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=UTC

RUN apt-get update && \
    apt-get upgrade -y  && \
    apt-get install -y --no-install-recommends \
    ca-certificates \
    redis \
    tini \
    procps \
    tzdata \
    && \
    apt-get clean

RUN echo "UTC" > /etc/timezone && \
    ln -sf /usr/share/zoneinfo/UTC /etc/localtime && \
    dpkg-reconfigure -f noninteractive tzdata

COPY test.conf /etc/redis/test.conf

WORKDIR /var/lib/redis
ENTRYPOINT ["/usr/bin/tini", "--"]
EXPOSE 6379
USER redis
CMD ["redis-server", "/etc/redis/test.conf"]
