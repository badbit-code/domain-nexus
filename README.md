# Expired Domains

## TODO 
- [ ] Create proper readme. Define basic project readme structure
- [ ] Create diagram/design of systems 
- [ ] Detemine release and dev cycles
- [ ] Define MVP 
- [ ] Create proof-of-concept prototype
- [ ] Re-organize files. Define basic project template structure

# Schemas
Data Schema
```
domain name             : str 256 char
top level domain name   : str 64 char
registrar               : str 64 or int Enum   
grace start date        : datatime or UTC 64bit timestamp 
full expire date        : datatime or UTC 64bit timestamp 
creation date           : datatime or UTC 64bit timestamp 
HAS_WIKI                : bool
alexa_score             : int
brandable_score         : int
market_sectors          : string[]
# Local bookkeeping
local update date       : datatime or UTC 64bit timestamp 
local retrieval date    : datatime or UTC 64bit timestamp 
```

```SQL
CREATE TABLE domains (
	id 				serial 				PRIMARY KEY,
	name 			VARCHAR (256)	 	NOT NULL,
	tld 				VARCHAR( 63 ) 		NOT NULL,
	registrar 		int 					NOT NULL,
 	expired 			timestamp 			NOT NULL,
	created			timestamp			NOT NULL,
	updated			timestamp			DEFAULT   CURRENT_TIMESTAMP,
	retrieved		timestamp			DEFAULT   CURRENT_TIMESTAMP,
	HAS_WIKI		boolean				DEFAULT FALSE,
	alexa_score		int					DEFAULT 0,
	branding_score	int					DEFAULT 0
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

# IDEAS
