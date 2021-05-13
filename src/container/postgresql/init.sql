CREATE EXTENSION "uuid-ossp";

CREATE
OR REPLACE FUNCTION trigger_set_timestamp() RETURNS TRIGGER AS $$
BEGIN NEW .updated = NOW();

RETURN NEW;

END;

$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION generate_domain_uuid() 
RETURNS trigger AS $$
  declare local_tld_string text;
  BEGIN
    SELECT name INTO local_tld_string
    FROM top_level_domain
    WHERE id = NEW .tld;

    NEW.id := uuid_generate_v3(
      uuid_ns_url(),
      LOWER(NEW .name) || '.' || local_tld_string
    );

    RETURN NEW;

  END;
$$ LANGUAGE plpgsql;

CREATE TABLE IF NOT EXISTS top_level_domain (
  id SERIAL PRIMARY KEY,
  name VARCHAR(63) NOT NULL UNIQUE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS registrar (
  id SERIAL PRIMARY KEY,
  name VARCHAR(63) NOT NULL UNIQUE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS domain (
  id UUID PRIMARY KEY,
  name VARCHAR(256) NOT NULL,
  tld SMALLINT NOT NULL REFERENCES top_level_domain(id),
  registrar SMALLINT NOT NULL REFERENCES registrar(id),
  expired TIMESTAMP DEFAULT NULL,
  registered TIMESTAMP DEFAULT NULL,
  HAS_WIKI BOOLEAN DEFAULT NULL,
  alexa_score INT DEFAULT NULL,
  branding_score INT DEFAULT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS goddady_meta (
  id BIGSERIAL PRIMARY KEY,
  domain_id UUID REFERENCES domain(id),
  auctionType VARCHAR(31),
  auctionEndTime TIMESTAMPTZ,
  price MONEY,
  numberOfBids INT,
  domainAge INT,
  description TEXT,
  pageviews INT,
  valuation MONEY,
  monthlyParkingRevenue MONEY,
  isAdult BOOLEAN,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS sedo_meta (
  id bigserial PRIMARY KEY,
  domain_id UUID REFERENCES domain(id),
  start_time TIMESTAMP,
  end_time TIMESTAMP,
  reserve_price MONEY,
  domain_is_IDN BOOLEAN,
  domain_has_hyphen BOOLEAN,
  domain_has_numbers BOOLEAN,
  domain_length SMALLINT,
  tld VARCHAR(63),
  traffic SMALLINT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS alexa_meta (
  id bigserial PRIMARY KEY,
  domain_id UUID REFERENCES domain(id),
  popularity = INT,
  reach_rank = INT,
  rank_delta = INT,
  country_code = VARCHAR(7),
  country_name = VARCHAR(63),
  country_rank = INT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS web_archive_meta (
  id bigserial PRIMARY KEY,
  domain_id UUID REFERENCES domain(id),
  popularity = INT,
  reach_rank = INT,
  rank_delta = INT,
  country_code = VARCHAR(7),
  country_name = VARCHAR(63),
  country_rank = INT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);


CREATE TRIGGER set_timestamp BEFORE
UPDATE ON domain FOR EACH ROW EXECUTE PROCEDURE trigger_set_timestamp();

CREATE TRIGGER trigger_generate_domain_uuid BEFORE
INSERT
  OR
UPDATE ON domain FOR EACH ROW EXECUTE PROCEDURE generate_domain_uuid();

CREATE TRIGGER set_timestamp BEFORE
UPDATE ON goddady_meta FOR EACH ROW EXECUTE PROCEDURE trigger_set_timestamp();

CREATE TRIGGER set_timestamp BEFORE
UPDATE ON sedo_meta FOR EACH ROW EXECUTE PROCEDURE trigger_set_timestamp();