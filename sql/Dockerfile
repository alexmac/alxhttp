FROM public.ecr.aws/docker/library/debian:12-slim
ARG POSTGRES_VERSION=16
ENV POSTGRES_VERSION=${POSTGRES_VERSION}

ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=UTC

RUN apt-get update && \
    apt-get upgrade -y  && \
    apt-get install -y --no-install-recommends \
    ca-certificates \
    tini \
    procps \
    tzdata \
    && \
    apt-get clean

RUN echo "UTC" > /etc/timezone && \
    ln -sf /usr/share/zoneinfo/UTC /etc/localtime && \
    dpkg-reconfigure -f noninteractive tzdata

COPY apt.postgresql.org.asc /usr/share/postgresql-common/pgdg/apt.postgresql.org.asc
RUN echo "deb [signed-by=/usr/share/postgresql-common/pgdg/apt.postgresql.org.asc] https://apt.postgresql.org/pub/repos/apt bookworm-pgdg main" \
    > /etc/apt/sources.list.d/pgdg.list

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    postgresql-client-${POSTGRES_VERSION} \
    postgresql-${POSTGRES_VERSION} \
    && \
    apt-get clean

COPY postgresql.conf /etc/postgresql/postgresql.conf

COPY pg_hba.conf /etc/postgresql/${POSTGRES_VERSION}/main/pg_hba.conf
RUN echo "include '/etc/postgresql/postgresql.conf'" >> /etc/postgresql/${POSTGRES_VERSION}/main/postgresql.conf

VOLUME ["/var/lib/postgresql/data"]

COPY schema.sql /tmp/
RUN service postgresql start && \
    psql -U postgres -c "ALTER USER postgres WITH PASSWORD 'test';" && \
    psql -v "ON_ERROR_STOP=1" -U postgres -d postgres -f /tmp/schema.sql && \
    service postgresql stop

EXPOSE 5432
USER postgres
ENTRYPOINT ["/usr/bin/tini", "--"]
CMD ["/usr/lib/postgresql/16/bin/postgres",  "-D", "/var/lib/postgresql/16/main", "-c", "config_file=/etc/postgresql/16/main/postgresql.conf"]
