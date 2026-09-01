# Oracle Caty Item Tables Migration Guide

## Summary

The Selling team is phasing out / decommissioning the Oracle UserItemHost (CatyHost) item family due to scalability challenges, high Oracle licensing costs, performance bottlenecks, and complex maintenance requirements.

The migration to a NuDocument-based solution will be executed in phases.

In the initial phase, the primary data reads/writes for **all selling listing applications** from the following [Oracle tables](https://docs.google.com/spreadsheets/d/1FkEFBrqDFMNY2EHeOTDUkn69pNT9pAzNmTWlWUtN8d4/edit#gid=0) will be migrated to NuDocument. This includes migrating Selling View Listing Service(SVLS) to read data from NuDocument instead of Oracle.

- **EBAY_ITEMS**
- **EBAY_SECONDARY_DATA**
- **ITEM_ATTR_INFO**
- **ITEM_VARIATION**
- **EBAY_ITEM_DESC**
- **EBAY_ITEM_SHIPPING**
- **EBAY_ITEM_REV_DETAIL**
- **EBAY_ITEM_REVISIONS**
- **ITEM_VARIATION_REV**
- **ITEM_ATTR_INFO_VERSION**
- **ITEM_DESC_VERSION**
- **ITEM_DESC_VERSION_NEW**
- **ITEM_FEATURES_VERSION**
- **ITEM_SECONDARY_DATA_VERSION**
- **ITEM_SHIPPING_VERSION**
- **ITEM_VARIATION_VERSION**
- **ITEM_VERSION**
- **ITEM_SHIPPING_VERSION**
- **ITEM_VARIATION_VERSION**
- **ITEM_VERSION**
- **EBAY_SCHEDULED_ITEM**
- **ITEM_LOCK**
- **ENTITY_PROFILE_LOCK**

In the initial phase, Domain teams have been asked to identify their usage of data from these tables. [This sheet](https://docs.google.com/spreadsheets/u/3/d/1RBsEJWmwUX72ejx9RM110RyEETy3faucgDNeeAVnVjc/edit) gives insights into how different applications are using data in these tables.

In the next phase, domain teams will need to migrate their data reads and writes out of these Oracle tables completely. They can leverage ULP to phase out these Oracle tables. Also, consumers of the item life cycle BES1 events needs to be migrated

## Background

Historically, these item tables were established long ago, and over time, numerous fields have been added without clear data ownership.

The Selling team conducted a thorough analysis of all data stored within these tables and devised a strategy to segregate seller-provided data as part of the listing flow (**Core Selling data**) from derived or computed data or data provided post Listing(**Domain Data**), which is managed by various domain teams such as Shipping, Trust, and Seller standards. A summary of the various fields and classifications of core selling and computed data can be found in [this sheet](https://docs.google.com/spreadsheets/d/1h_fS7jZM61xCHyrI7UKVluDelTB_-ZGwBkx_R2KD8FQ/edit?gid=1664882354#gid=1664882354)

The earlier strategy for this Oracle migration involves the Selling Team owning only over core selling data or seller-provided data in listing flows, while domain teams take responsibility for domain data (derived or computed or post listing data).

The core selling data, identified and modeled as Listing documents in NuData, are concurrently dual written into both NuData and Oracle. This core selling data is then made accessible through SVLS for client applications, with over 200 clients currently retrieving core selling data via SVLS.

Domain teams were similarly tasked with establishing their own data stores to manage their respective data and transitioning client applications away from Oracle.

Despite these efforts, the transition has not significantly reduced Oracle data access. Applications such as Search and View Item (VI), Search, Checkout require access to more than just core selling data. They have adopted a model that involves accessing core selling data via SVLS and directly accessing the database for all other domain or derived data.

Key learnings from this initial migration strategy include:

- Many applications require access to more than just Core Selling data.
- Domain teams need a simplified method to manage their data with minimal effort.
- It is challenging for each domain team to coordinate with every consumer of their data, especially large consumers like Search and View Item, to access data from different sources.

To address these challenges, the Selling team has developed a new platform, [Unified Listing Platform (ULP)](https://pages.github.corp.ebay.com/unified-listing-platform/ulp-docs/).

Unified Listing Platform (ULP) is designed to serve all consumers of buyer-context independent listing data, including both core listing data as well as extended listing information. ULP provides data with low latency, high throughput, supporting both single and bulk listing data retrieval, single and multi-sku via GraphQL endpoint. ULP also broadcasts different kinds of listing change events, including CDC event stream for caller convenience. For more information about ULP, visit [https://go/ulp](https://go/ulp)

In H1 2024, the Selling Listing team did an exercise with all the domain teams to find the data usage of different applications from these tables. [This sheet](https://docs.google.com/spreadsheets/u/3/d/1RBsEJWmwUX72ejx9RM110RyEETy3faucgDNeeAVnVjc/edit) gives insights into how different applications are using data in these tables.

## What is the current migration strategy for the Selling Listing Platform team?

The Selling team is currently dual-writing core selling data into both NuData and Oracle, with Oracle still serving as the primary data source for read and write operations. Our goal is to make NuData the primary source for all selling read use cases. Currently, SVLS, our service for data retrieval, reads data from Oracle, but we are transitioning all data reads from Oracle to NuData, making NuData the primary source for all SVLS use cases. This change will alleviate significant pressure on Oracle..

We have identified certain domains, such as checkout, that still directly write data to Oracle (e.g., quantity updates during checkout) for the Core Selling data. We are collaborating with these teams to migrate their data writing to use our service, CAS (Central Availability Service). This migration is a prerequisite for making NuData the primary source for SVLS for Core Selling data.

The Selling team will continue dual-writing until all domains have fully migrated away from Oracle. Additionally, we are actively enhancing the ULP to provide the necessary support for readers and writers to easily transition their use cases to ULP.

## What is the current migration strategy for domain teams?

Domain teams responsible for writing data to Oracle should manage their data and make it accessible through services. These teams can integrate with ULP as data providers, allowing their data to be available to all ULP clients. ULP also provides support for Domain teams that store few data points like flags, counts etc for easier migration.

Domain teams that retrieve data directly from Oracle should transition away from using Oracle. They can integrate with ULP to meet most of their data requirements. If their data has not yet been migrated to ULP, temporary adapters may be available to retrieve data from Oracle(Only flags from ebay_items and variation_item are targeted). These adapters will be phased out once the domain teams have migrated their data and registered with ULP as providers. Please refer to ULP documentation for more information.

## How can I determine which tables/columns my application is using?

**Option 1:** Visit the Sherlock Pool page (of your production pool) under the DAL tab to find the list of oracle queries used in your application. You can refer to the following sample link: [Sherlock Pool Page - DAL Tab](https://appmon.vip.ebay.com/reports/environment/prod/pool/r1api5io/DAL?startTime=2024/09/03%2000:00&endTime=2024/09/04%2000:00&colo=ALL).

**Option 2:** Use the DBinaBox tool to retrieve the list of queries used in your application or pool. You can refer to the following link: [DBinaBox Tool](https://dbinabox.vip.ebay.com/cal_db_pool_sql.html?pool=r1api5io&db=apiusagehost&day=2023-06-06).

## How can I migrate my application that is using SaleBOF / SaleAggregator to fetch item information?

The V3 DAL libraries, such as **SaleAggregator and SaleBOF**, consolidate data from multiple tables, including those beyond item tables, and retrieve most columns entirely from these sources. For instance, over 400 item attributes are consolidated into a single XML CLOB within the item item attributes table, requiring applications to fetch and parse this column to read/write specific attributes. Additionally, a single flag column in these item tables may contain up to 32 flags, with more than 500 such flags in total.

The existing DAL libraries, like SaleBOF, load all these columns completely, which complicates pinpointing the precise data needed for specific applications. Out of approximately 1200 data points stored in these 6 tables, only about 300 are provided by the seller, with the remainder often going unused. Our goal is to migrate only the necessary data and phase out what is not used.

Given these complexities, updating these libraries to automatically fetch the required data is not feasible. To facilitate a smoother transition for applications, we have introduced the [Unified Listing Platform (ULP)](https://pages.github.corp.ebay.com/unified-listing-platform/ulp-docs/). This service provides centralized access to all Listing/Item-related information, streamlining the data retrieval process for applications transitioning from older DAL libraries.

## Mapping of SaleBo fields to ULP/SVLS fields

We are currently working on this mapping. In the meantime, you can refer to the following wiki for more information: [Mapping Wiki](https://wiki.corp.ebay.com/pages/viewpage.action?pageId=1382773750).

## How to Integrate with ULP as a Data Reader?

To learn more about integrating with the Unified Listing Platform (ULP) as a data reader, please refer to the [ULP documentation](https://pages.github.corp.ebay.com/unified-listing-platform/ulp-docs/docs/category/query-listing-data).

For quick integration assistance, you can also check out the available [sample implementations](https://pages.github.corp.ebay.com/unified-listing-platform/ulp-docs/docs/Client/Samples).

[https://pages.github.corp.ebay.com/unified-listing-platform/ulp-docs/docs/Client/Samples](https://pages.github.corp.ebay.com/unified-listing-platform/ulp-docs/docs/Client/Samples)

## How to Integrate with ULP as a Data Provider?

To integrate with the Unified Listing Platform (ULP) as a data provider, please see the [ULP documentation](https://pages.github.corp.ebay.com/unified-listing-platform/ulp-docs/docs/category/listing-providers) for detailed instructions.

[Reference application](https://github.corp.ebay.com/unified-listing-platform/Reference-Applications/tree/main/DealItem-reference-provider)

## My application needs item data in realtime. How can I get the real time data ?

ULP currently uses cached data and is eventually consistent. We are working on enabling real-time retrieval of item data based on specific needs. Please share your use case with us so we can assess how ULP can support it.

## My Application listens to Item BES events and fetches item data, can I get the data from ULP?

We recommend migrating to the ULP events from the legacy BES item events. For more details, please refer to this [link.](https://pages.github.corp.ebay.com/unified-listing-platform/ulp-docs/docs/ExternalEvents)

Please note that ULP currently uses cached data and is eventually consistent.

## We currently use Oracle GoldenGate events to capture item changes. How can I migrate this process??

ULP generates NuData CDC streams(WIP/POC), which are equivalent to Oracle GoldenGate events and can be utilized in your application.

## We use item DW tables to access the item data, what is the migration plan for DW?

We are working on creating DW tables, will be available soon

## What are recommended migration paths for consumers of legacy listing BES 1 events?

**List of all Caty BES events:** [https://docs.google.com/spreadsheets/d/1FrvVsiH2D_3JV7zguvEqdxPiWz0q9BUcnMgi2_5sIcI/edit?gid=0#gid=0](https://docs.google.com/spreadsheets/d/1FrvVsiH2D_3JV7zguvEqdxPiWz0q9BUcnMgi2_5sIcI/edit?gid=0#gid=0) ( **For non ULP BES, if you have more questions reach out to** [Souhaila Moalla](mailto:smoalla@ebay.com)**- NuData**)

### The Listing Platform currently generates the following events using the legacy BES 1 framework, which relies on Oracle transactional PL/SQL

- [ITEM](https://wiki.corp.ebay.com/display/LS/BES+Events+generated+by+CLS#BESEventsgeneratedbyCLS-ITEM)
  - [ITEM.NEW](https://wiki.corp.ebay.com/display/LS/BES+Events+generated+by+CLS#BESEventsgeneratedbyCLS-ITEM.NEW)
  - [ITEM.REVISED](https://wiki.corp.ebay.com/display/LS/BES+Events+generated+by+CLS#BESEventsgeneratedbyCLS-ITEM.REVISED)
  - [ITEM.EXTENDED](https://wiki.corp.ebay.com/display/LS/BES+Events+generated+by+CLS#BESEventsgeneratedbyCLS-ITEM.EXTENDED)
  - [ITEM.CLOSURE](https://wiki.corp.ebay.com/display/LS/BES+Events+generated+by+CLS#BESEventsgeneratedbyCLS-ITEM.CLOSURE)
  - [ITEM.SOLD](https://wiki.corp.ebay.com/display/LS/BES+Events+generated+by+CLS#BESEventsgeneratedbyCLS-ITEM.SOLD)
  - [ITEM.SCHED.TOACTIVE](https://wiki.corp.ebay.com/display/LS/BES+Events+generated+by+CLS#BESEventsgeneratedbyCLS-ITEM.SCHED.TOACTIVE)
  - [ITEM.CATEGORY.UPDATED](https://wiki.corp.ebay.com/display/LS/BES+Events+generated+by+CLS#BESEventsgeneratedbyCLS-ITEM.CATEGORY.UPDATED)
  - [ITEM.HOLDSTATUS.UPDATED](https://wiki.corp.ebay.com/display/LS/BES+Events+generated+by+CLS#BESEventsgeneratedbyCLS-ITEM.HOLDSTATUS.UPDATED)
- [DRAFT](https://wiki.corp.ebay.com/display/LS/BES+Events+generated+by+CLS#BESEventsgeneratedbyCLS-DRAFT)
  - [DRAFT.CREATE](https://wiki.corp.ebay.com/display/LS/BES+Events+generated+by+CLS#BESEventsgeneratedbyCLS-DRAFT.CREATE)
  - [DRAFT.UPDATE](https://wiki.corp.ebay.com/display/LS/BES+Events+generated+by+CLS#BESEventsgeneratedbyCLS-DRAFT.UPDATE)

**These events are accessible to BES 2 consumers through the BES 2 event bridge or** [Event Type BES2 Replication](https://pages.github.corp.ebay.com/Near-Real-Time/rheos-documentation/docs/bes2/EventType-BES2-Replication/)

### Unified listing platform is generating following [BES 2 events](https://pages.github.corp.ebay.com/unified-listing-platform/ulp-docs/docs/ExternalEvents)

- **ULP.LISTING.NEW**
- **ULP.LISTING.UPDATED**
- **ULP.LISTING.ENDED**
- **ULP.LISTING.HOLDSTATUS.UPDATED**
- **ULP.LISTING.CATEGORY.UPDATED**

With the ongoing deprecation of the corresponding Oracle tables, it is necessary for consumers of these BES 1 events to transition to alternative solutions.

There are three options:

### Option 1( Recommended )

**Consumers of the legacy Listing BES1 events are advised to migrate to the corresponding ULP BES2 events. This migration requires integrating with the ULP to access item details as needed, involving changes to the consumer to accommodate the new BES2 event format. Please note that while Listing BES1 and ULP BES2 are distinct events with different payloads, they are generated for the same use cases.** **Consumers must manage the transition carefully to ensure a smooth switch and avoid any data duplication or loss during the process.**

### Option 2

For consumers where the transition demands minimal changes, the BES platform offers support that facilitates a straightforward [migration](https://pages.github.corp.ebay.com/Near-Real-Time/rheos-documentation/docs/bes2/Consumer-Migration/) to BES 2. However, once the underlying Oracle tables and BES 1 events are phased out, our application will generate these events in a non-transactional manner, which may lead to potential availability issues. This option should be chosen only if your application can tolerate such availability concerns.

### Option 3

For consumers requiring more real-time event handling of item updates where no direct BES 2 equivalent exists, the Listing Platform will create new events leveraging NuData's Transactional BES capabilities. These will be new BES 2 events, and consumers will need to migrate to consume these new events.
