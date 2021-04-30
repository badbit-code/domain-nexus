CREATE EXTENSION "uuid-ossp";

CREATE OR REPLACE FUNCTION trigger_set_timestamp()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION generate_domain_uuid()
RETURNS trigger AS $$
     BEGIN
         NEW.id := uuid_generate_v3(uuid_ns_url(), NEW.name || '.' || NEW.tld );
         RETURN NEW;
     END;
 $$ LANGUAGE plpgsql;

CREATE TRIGGER set_timestamp 
BEFORE UPDATE ON domains
FOR EACH ROW 
EXECUTE PROCEDURE trigger_set_timestamp();

CREATE TRIGGER generate_domain_uuid 
BEFORE INSERT OR UPDATE ON domains 
FOR EACH ROW EXECUTE PROCEDURE generate_domain_uuid();

CREATE TRIGGER set_timestamp
BEFORE UPDATE ON goddady_meta
FOR EACH ROW
EXECUTE PROCEDURE trigger_set_timestamp();

CREATE TRIGGER set_timestamp
BEFORE UPDATE ON sedo_meta
FOR EACH ROW
EXECUTE PROCEDURE trigger_set_timestamp();


CREATE TABLE domains (
    id              UUID            PRIMARY KEY,
    name            VARCHAR (256)   NOT NULL,
    tld             VARCHAR( 63 )   NOT NULL,
    registrar       int             NOT NULL, /* TODO map to registrar table*/
    expired         timestamp       DEFAULT NULL,
    registered      timestamp       DEFAULT NULL,
    HAS_WIKI        boolean         DEFAULT NULL,
    alexa_score     int             DEFAULT NULL,
    branding_score  int             DEFAULT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
);

CREATE TABLE IF NOT EXISTS goddady_meta (
    id                      bigserial       PRIMARY KEY, 
    domain_id               UUID            references domains(id),
    auctionType             varchar(31),
    auctionEndTime          timestamptz, 
    price                   money, 
    numberOfBids            int, 
    domainAge               int,
    description             text, 
    pageviews               int, 
    valuation               money, 
    monthlyParkingRevenue   money,
    isAdult                 bool,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
);

CREATE TABLE IF NOT EXISTS sedo_meta (
    id                      bigserial       PRIMARY KEY, 
    domain_id               UUID            references domains(id),
    start_time             TIMESTAMP,
    end_time                TIMESTAMP,
    reserve_price           money,
    domain_is_IDN           bool,
    domain_has_hyphen       bool,
    domain_has_numbers      bool,
    domain_length           INT,
    tld                     VARCHAR(63),
    traffic                 INT,
    link                    VARCHAR(255),       
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
);

