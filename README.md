# Expired Domains

## TODO 
- [ ] Create proper readme. Define basic project readme structure
- [x] Create diagram/design of systems 
- [x] Detemine release and dev cycles
- [x] Define MVP 
- [x] Create proof-of-concept prototype
- [ ] Re-organize files. Define basic project template structure

# Schemas
Data Schema
```
domain name             : str 256 char
top level domain name   : str 64 char
registrar               : str 64 or int Enum   
grace start date        : datetime or UTC 64bit timestamp 
full expire date        : datetime or UTC 64bit timestamp 
creation date           : datetime or UTC 64bit timestamp 
HAS_WIKI                : bool
alexa_score             : int
brandable_score         : int
market_sectors          : string[]
# Local bookkeeping
local update date       : datetime or UTC 64bit timestamp 
local retrieval date    : datetime or UTC 64bit timestamp 
```

```SQL
CREATE TABLE domains (
    id              bigserial       PRIMARY KEY,
    name            VARCHAR (256)   NOT NULL,
    tld             VARCHAR( 63 )   NOT NULL,
    registrar       int             NOT NULL,
    expired         timestamp       NOT NULL,
    created         timestamp       NOT NULL,
    updated         timestamp       NOT NULL DEFAULT CURRENT_TIMESTAMP,
    retrieved       timestamp       NOT NULL DEFAULT CURRENT_TIMESTAMP,
    HAS_WIKI        boolean         NOT NULL DEFAULT FALSE,
    alexa_score     int             NOT NULL DEFAULT 0,
    branding_score  int             NOT NULL DEFAULT 0
);
```

if domain is sold in expire or added to listing time period it is worth more because no expired date on domain which hurts SEO

Expiring in purgatory:
    Expires and sold by vendor
    Expires vendor will not renew

Expiring Domains

Only Need to keep fresh domains: 
    Domains older than 90 days can be purged or archived

domain dates:

added to listing (determines age out)
expire date (starts grace period)
full expire (available to buy)

When can we sell data?
full expire = easy
expire date = godaddy only
added to listing = referral to bid 

Anything else should should use relational mappings to keep the core 


