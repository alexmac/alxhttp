FROM public.ecr.aws/docker/library/debian:13-slim
ARG POSTGRES_VERSION=18
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

ENTRYPOINT ["/usr/bin/tini", "--"]

COPY apt.postgresql.org.asc /usr/share/postgresql-common/pgdg/apt.postgresql.org.asc
RUN echo "deb [signed-by=/usr/share/postgresql-common/pgdg/apt.postgresql.org.asc] https://apt.postgresql.org/pub/repos/apt trixie-pgdg main" \
    > /etc/apt/sources.list.d/pgdg.list

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    postgresql-client-${POSTGRES_VERSION} \
    postgresql-${POSTGRES_VERSION} \
    postgresql-${POSTGRES_VERSION}-pgvector \
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
CMD ["/usr/lib/postgresql/18/bin/postgres",  "-D", "/var/lib/postgresql/18/main", "-c", "config_file=/etc/postgresql/18/main/postgresql.conf"]
