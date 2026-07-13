# Item LDM

[← Back to LDM Catalog](../index.md)

## Overview

**LDM Name:** `item`

**Description:** The core listing entity in the Item Domain. Each record represents one eBay listing, containing comprehensive information about title, pricing, category, seller, listing lifecycle, and more.

**Primary Key:** `item_id`

---

## Fields (228)

<!-- BEGIN GENERATED ITEM FIELDS -->

**`item_id`** <span class="field-type">LONG</span>

A unique identifier for the listing, generated upon successful creation.

**`auct_titl`** <span class="field-type">STRING</span>

Listing title shown to buyers in search results and on the item page.

**`subtitle`** <span class="field-type">STRING</span>

The listing’s full subtitle text; it can be null if the seller did not provide one

**`item_desc`** <span class="field-type">STRING</span>

Seller-provided item description content encoded in Base64. Decode before displaying or analyzing the description text.

**`item_desc_lgth_num`** <span class="field-type">INTEGER</span>

Length of the encoded item description content.

**`bin_price_lstg_curncy`** <span class="field-type">DOUBLE</span>

Buy It Now price in listing currency in View Item page.

??? field-context "More context"
    
    **Producer Knowledge**

    - **Producer Ownership** — The team and application that owns and maintains the source data
        - Team Name: SX Inventory Mgmt - Listing Platform Core Services
        - Notification Email: DL-eBay-ListingRedesign@ebay.com
        - OnCall Service: https://ebay-cpt.pagerduty.com/service-directory/$PZMGJDA
        - Service Link: https://cloud.ebay.com/app/detail/crlstngsv/overview
    
    - **Producer Process** — How producer applications write data to the source system.
        - Service Name: Core Listing Service
        - Source Code: https://github.corp.ebay.com/SellingDomain/crlstngsv
        - Processes: 1. new listing 2. modify price [AI Summary]

    - **Source Storage** — Physical storage information of source data, such as NuDoc keyspace, Oracle db.
        - NuDoc Keyspace Name: ItemKeyspace, ItemGroupKeyspace
        - NuDoc Link: https://qa.cloud.ebay.com/cloud-data/databases/nudocument/keyspaces/ItemKeyspace
        - NuDoc Fields: itemkeyspace.ItemQtyPrice.price.fixedPrice
    
    - **Source Model Design** — The data structure written by producer applications, such as source classes.
        - Class: Item.class, ItemGroup.class
        - Field: fixedPrice
    
    - **Change Process** — How producer-side changes are released, such as PRs, release notes, schema changes, or standard CI/CD process.
        - 8 releases: https://cloud.ebay.com/app/detail/crlstngsv/ecd?pipelineId=48317243&count=10&pageSize=10&current=1
        - 10 PRs in last month: https://github.corp.ebay.com/SellingDomain/crlstngsv/pulls?q=is%3Apr+
    
    **Semantic Knowledge**

    - **Schema** — Entities, fields, data types, primary keys
        - Data Type: double

    - **Semantics** — Entity and field business definitions
        - Description: Buy It Now price in listing currency in View Item page.
    
    - **Data Lineage** (from source to LDM process, including Transformation / Cleaning Knowledge) — How data moves across the end-to-end data flow, from source models to landed data, transformed data, and downstream consumption.
        - Extract data from 5 keyspaces, merge, and transform to LDM fields. [ai-summary]
        - ETL Code: [link]
        - Data Flow Diagram: https://lucid.app/lucidchart/73cbffe1-905b-415f-a5ca-39c1ecf8ad6b/edit?invitationId=inv_d08689cb-9ea6-43bc-96d8-ff416c09b61f&page=a1vXV8fI_cE.#

    - **Data Profiling** — Observed data characteristics such as null rate, cardinality, value distribution, sample values.
        - min: 0, max: 100,000, avg: 300
    
    - **Data Quality** — Data quality rules the data must satisfy.
        - not null
        - not negative

    - **Data Availability** — Data freshness and delivery SLA
        - Freshness: daily
        - SLA: P99 - 7:00 AM PST, P90 - 4:00 AM PST
    
    **Consumption Knowledge**

    - **Consumption Patterns** — Common ways users consume and interpret the data.
        - GMV Calculation
        - Attribution (Ads, Marketing, Search, etc)
    
    - **Adoption** — Usage and adoption, along with the business scenarios, decisions, and downstream products that depend on the data.
        - 500 MAU (monthly active users querying this field)
        - Main downstream use cases:
            - Financial report on Quickstrike, value: [to be provided]

**`start_price_lstg_curncy`** <span class="field-type">DOUBLE</span>

Start price in listing currency. For SIF (Store Inventory Format)/FP (Fixed Price) items, this is the BIN (Buy It Now) price. For auctions/Dutch, it's the opening bid price.

**`rsrv_price_list_crncy`** <span class="field-type">DOUBLE</span>

The lowest price at which the seller is willing to sell the item. StartPrice must be lower than ReservePrice. 0 = no reserve set.

**`orgnl_price_amt`** <span class="field-type">DOUBLE</span>

Original price before a promotional/markdown sale discount. NULL if not a promotional sale listing.

**`lstg_curncy_id`** <span class="field-type">INTEGER</span>

Currency ID used for the listing prices. This ID is a foreign key to the [Currency LDM](#).

**`qty_avail`** <span class="field-type">INTEGER</span>

The number of this item that are initially available for sale.

**`qty_sold`** <span class="field-type">INTEGER</span>

The number of items sold in the listing.

**`lot_size`** <span class="field-type">INTEGER</span>

Number of individual physical items per sale unit.

**`slr_id`** <span class="field-type">LONG</span>

Seller's Oracle user ID associated with the listing. Foreign key to [User LDM](user.md).

**`slr_prdct_id_txt`** <span class="field-type">STRING</span>

Seller-defined product identifier text (e.g. manufacturer part number/ISBN/UPC). Empty if not provided.

**`sku_num`** <span class="field-type">STRING</span>

Seller&#x27;s custom, application-specific data associated with the item. Data specified here is stored by eBay with the item for seller but it is not used by eBay in any way.

**`application_id`** <span class="field-type">LONG</span>

Application identifier used by external consumers to identify the application or listing tool associated with listing creation. This ID is a foreign key/code to the application logical data model; join to the [Application LDM](#) to get the application name. Common examples include 219527 = BOLT, 290356 = BOLT B2C, 384352 = HELIX, 2828 = File Exchange, 114100 = Auto Relist.

**`lstg_status_id`** <span class="field-type">INTEGER</span>

Listing lifecycle status code. Values: 0 = Live, 1 = Ended, 2 = Admin ended, 3 = Schedule Deleted, 4 = Scheduled.

**`auct_type_code`** <span class="field-type">INTEGER</span>

Listing format code. Values: 0=Unknown Auction, 1=Chinese Auction/Auction-with-BIN, 2=Dutch Auction, 4=Auction Yankee never implemented, 5=Old Live Auctions deprecated, 6=AdFormat, 7=Store Fixed Price, 8=Second Chance Offer, 9=Fixed Price/GTC, 12=Half.com, 13=Classified Ads/Lead Gen, 14=eBay Express Only, 15=Shopping.com/SDC stopped 2008/8/15

**`auct_start_dt`** <span class="field-type">DATE</span>

Date the listing became (or is scheduled to become) live.

**`auct_end_dt`** <span class="field-type">DATE</span>

Date the listing ended or is scheduled to end.

**`sale_sched_end_dt`** <span class="field-type">DATE</span>

Scheduled end date set at listing creation (start + duration). It is only updated when the seller changes listing duration or sale start date in RYI (Revise Your Item) and there has been no sale.

**`auct_start_date`** <span class="field-type">TIMESTAMP</span>

The timestamp when the listing becomes live

**`auct_end_date`** <span class="field-type">TIMESTAMP</span>

Timestamp the listing ended or is scheduled to end.

**`site_create_date`** <span class="field-type">TIMESTAMP</span>

Date and time the listing was created. This value is read-only and cannot be updated.

**`last_modfd_dt`** <span class="field-type">DATE</span>

Date the listing was last modified on the site.

**`auction_end_reason_code`** <span class="field-type">INTEGER</span>

Reason code for why the listing ended. Values: 0=Natural end/not ended early, 1=Seller-ended: lost or broken, 2=Seller-ended: no longer available, 3=Seller-ended: error in bid/reserve, 4=Seller-ended: listing error, 5=Sold to highest bidder early, 6=EndReasonAVSTickets, 7=SIF Bulk End, 8=Ended by DBA script, 9=SoldOnProStores deprecated, 10=SoldVehicle variant, 11=Ended on zero quantity, 12=SoldVehicle Motors FSBO, 99=GTC renewal failure, -1=invalid, -88=invalid sentinel, -99=pre-2008 unknown.

**`relist_parent_item_id`** <span class="field-type">LONG</span>

Item ID of the parent listing this item was relisted from (via relist or sell-similar). -999=no parent (original listing).

**`relistid`** <span class="field-type">LONG</span>

Indicates if the listing is ended with a relisted one. If it&#x27;s &gt; 0, it means that the item has been ended and a new relisted one has been created. and the value of this relistId is the same as the value of itemId of the new relisted item

**`item_vrsn_id`** <span class="field-type">LONG</span>

A generated sequence used to track versions for each revision made by the seller

**`sgnfcnt_rvsn_cnt`** <span class="field-type">INTEGER</span>

An item specific count of the number of times it has been significantly revised.

**`item_site_id`** <span class="field-type">INTEGER</span>

eBay site ID where the item was listed. FK to Site LDM.

**`slr_site_id`** <span class="field-type">INTEGER</span>

eBay site ID where the seller account is registered; this can differ from the site where the item is listed.

**`high_bdr_site_id`** <span class="field-type">INTEGER</span>

Registration site ID of the highest bidder for the listing; -999=no bidder.

**`leaf_categ_id`** <span class="field-type">INTEGER</span>

Primary leaf category ID chosen by the seller for the listing. Use with item_site_id to interpret category hierarchy, SAP category, and higher-level category attributes. See [Category LDM](category.md).

Example:

- `41931` = Computers & Networking:Software:Education & Reference:Car Repair

**`leaf_categ_name`** <span class="field-type">STRING</span>

Name of the leaf category where the item is listed.

Example:

- Computers & Networking:Software:Education & Reference:Car Repair

**`leaf_categ_id2`** <span class="field-type">INTEGER</span>

Secondary leaf category ID chosen by the seller when the listing is posted in two categories; 0 means no secondary category.

**`meta_categ_id`** <span class="field-type">INTEGER</span>

Meta category ID

Example:

- `58058` = Computers/Tablets & Networking

**`meta_categ_name`** <span class="field-type">STRING</span>

Meta category name (top level)

Example:

- Computers/Tablets & Networking

**`categ_lvl2_id`** <span class="field-type">INTEGER</span>

Level 2 category ID

Example:

- `18793` = Software

**`categ_lvl2_name`** <span class="field-type">STRING</span>

Level 2 category name

Example:

- Software

**`categ_lvl3_id`** <span class="field-type">INTEGER</span>

Level 3 category ID

Example:

- `3783` = Education, Language, Reference

**`categ_lvl3_name`** <span class="field-type">STRING</span>

Level 3 category name

Example:

- Education, Language, Reference

**`categ_lvl4_id`** <span class="field-type">INTEGER</span>

Level 4 category ID

Example:

- `3783` = Education, Language, Reference

**`categ_lvl4_name`** <span class="field-type">STRING</span>

Level 4 category name

Example:

- Education, Language, Reference

**`categ_lvl5_id`** <span class="field-type">INTEGER</span>

Level 5 category ID

Example:

- `3783` = Education, Language, Reference

**`categ_lvl5_name`** <span class="field-type">STRING</span>

Level 5 category name

Example:

- Education, Language, Reference

**`categ_lvl6_id`** <span class="field-type">INTEGER</span>

Level 6 category ID

Example:

- `3783` = Education, Language, Reference

**`categ_lvl6_name`** <span class="field-type">STRING</span>

Level 6 category name

Example:

- Education, Language, Reference

**`categ_key`** <span class="field-type">LONG</span>

Surrogate category hierarchy key for the primary leaf category of the listing.

**`categ_key2`** <span class="field-type">LONG</span>

Surrogate category hierarchy key for the secondary leaf category of the listing, when a secondary category exists.

**`categ_move_to_id`** <span class="field-type">INTEGER</span>

Replacement category ID when the original leaf category has been retired or moved to another category structure.

**`stor_categ_id`** <span class="field-type">LONG</span>

Primary store category ID under which this listing appears in the seller's eBay Store. 0 = no store category assigned.

**`stor_categ2_id`** <span class="field-type">LONG</span>

Secondary store category ID. 0 = no secondary store category.

**`sap_category_id`** <span class="field-type">INTEGER</span>

Search Annotation Platform (SAP) category ID assigned to the listing.

**`lcl_sap_categ_name`** <span class="field-type">STRING</span>

Local Search Annotation Platform (SAP) category name for the listing category.

**`glb_sap_categ_name`** <span class="field-type">STRING</span>

Global Search Annotation Platform (SAP) category name for the listing category.

**`bsns_vrtcl_name`** <span class="field-type">STRING</span>

Business Vertical Name (e.g. Electronics, Fashion, Motors).

**`item_cntry_id`** <span class="field-type">INTEGER</span>

Unique identifier of the country where the item is physically located, as declared by the seller. Note: reflects item location, not seller registration country (see slr_cntry_id).

**`slr_cntry_id`** <span class="field-type">INTEGER</span>

Country ID where the seller account is registered; this can differ from the physical item location country.

**`high_bdr_cntry_id`** <span class="field-type">INTEGER</span>

Country ID of the highest bidder for the listing; -999=no bidder.

**`item_loc`** <span class="field-type">STRING</span>

Seller-provided textual geographical location of the item.

**`item_zip`** <span class="field-type">STRING</span>

Zip/postal code of item location.


Structured product attributes and eBay-derived catalog/classifier signals, such as brand, MPN, GTIN, aspect values, ePID adoption, and product coverage.

**`item_cndtn_id`** <span class="field-type">INTEGER</span>

Seller-provided item condition code for the listing. Common values include 1000 = New, 1500 = New other, 1750 = New with defects, 2000 = Certified Refurbished, 2500 = Seller refurbished, 2750 = Like new, 3000 = Used / Pre-owned Good, 4000 = Very good, 5000 = Good, 6000 = Acceptable, 7000 = For parts or not working.

**`cndtn_rollup_id`** <span class="field-type">INTEGER</span>

Higher-level item condition rollup derived from the item condition. Values: 1 = New, 2 = Refurbished, 3 = Used, 4 = Unknown; unknown can later resolve when condition attributes are updated.

**`bold_title`** <span class="field-type">STRING</span>

If specified, the seller wants the title for the item's listing to be in boldface type. Applicable listing fees apply. Does not affect the item subtitle (Item.SubTitle), if any. Not applicable to eBay Motors. Values: "0"=not bold, "1"=bold, empty string=legacy historical records not tracked

**`glry_type_id`** <span class="field-type">INTEGER</span>

Indicates the type of gallery image for the listing. Potential values: 0 = no gallery, 1 = standard gallery, 2 = featured gallery, 6 = gallery variant, 7 = super gallery/gallery plus,  NULL = not set.

**`gallery_url`** <span class="field-type">STRING</span>

Single gallery image URL for the listing, usually the first picture URL and used in search or merchandising placements.

**`photo_count`** <span class="field-type">INTEGER</span>

Number of photos attached to the listing.

**`photo_display_type`** <span class="field-type">INTEGER</span>

Photo display mode code for the listing. Values: 0=Standard Show, 1=Slide Show, 2=Large Photo Show, 3=Picture Pack, 4=EPS Picture Show, 5=Self Hosted Picture Show, 6=SuperSize Picture Show.

**`picture_url`** <span class="field-type">STRING</span>

URL(s) of the listing's View Item pictures. Multiple URLs may appear semicolon-delimited.

**`private_yn`** <span class="field-type">STRING</span>

Indicates a private listing where bidder identities are hidden. Values: "0" = not private, "1" = private.

**`super_featured`** <span class="field-type">STRING</span>

Super-featured (top-of-category) listing upgrade. Values: "0"=not super-featured, "1"=super-featured, empty string=legacy records.

**`shipping_fee`** <span class="field-type">DOUBLE</span>

First domestic shipping service cost in listing currency as shown on listing. 0 if seller used the shipping calculator. Does not necessarily reflect actual fees paid.

**`shipping_xfee`** <span class="field-type">DOUBLE</span>

Per-additional-item shipping fee shown on listing. Does not necessarily reflect actual fees paid.

**`shipping_type`** <span class="field-type">INTEGER</span>

Shipping cost model selected for the listing. Values include 0 = not specified, 1 = flat rate, 2 = calculated rate, 3 = freight, 5 = flat domestic/calculated international, 6 = calculated domestic/flat international, -999 = null.

**`package_size`** <span class="field-type">INTEGER</span>

Shipping package type code that identifies the package format used to ship the item(s). Values: 0=None/not specified, 4=Package/Thick Envelope, 1=Letter, 26=FedEx Envelope, 5=Large Package, 2=Large Envelope , 19=USPS Large Flat Rate Box, 29=DHL Flyer, 27=FedEx Pak, 21=USPS Flat Rate Envelope, 22=USPS Padded Flat Rate Envelope, 24=USPS Legal Flat Rate Envelope, 17=Irregularly Shaped, 30=DHL Box, 7=UPS Letter.

**`weight`** <span class="field-type">LONG</span>

Item weight in the unit specified by weight_unit_type. 0 = not specified.

**`weight_unit_type`** <span class="field-type">INTEGER</span>

Unit of weight for the item. Values: 1=Pounds, 2=KiloGrams

**`payment_cash`** <span class="field-type">STRING</span>

Indicates whether payment on pickup / cash on pickup is accepted. When used, buyer and seller arrange offline payment and pickup. Values: "0"=no, "1"=yes, empty string=legacy records.

**`payment_cc`** <span class="field-type">STRING</span>

Indicates whether credit card payment is accepted as a payment method for the listing. Values: "0"=no, "1"=yes, empty string=legacy records

**`payment_moneyxfer`** <span class="field-type">STRING</span>

Indicates whether direct money transfer is accepted as a payment method for the listing. Values: "0"=no, "1"=yes, empty string=legacy records.

**`return_policy_yn`** <span class="field-type">STRING</span>

Y/N flag indicating whether the seller entered text in the Payment Instructions field. Values: "N", "Y", empty string(legacy records)

**`tax_new`** <span class="field-type">DOUBLE</span>

Sales tax percentage specified by the seller (e.g. 6.500 = 6.5%). 0 = no seller-specified tax.

**`tax_new_state`** <span class="field-type">STRING</span>

State/region code to which the seller-specified sales tax rate (tax_new) applies. -999=null/not specified.

**`is_immediate_payment_required`** <span class="field-type">INTEGER</span>

Indicates whether immediate payment is required for the listing.

**`is_buyer_responsible_for_shipping`** <span class="field-type">INTEGER</span>

Indicates whether the buyer is responsible for shipping, primarily for Motors listings.

**`is_tax_applied_to_shipping`** <span class="field-type">INTEGER</span>

Indicates whether sales tax applies to the shipping fee for the listing.

**`has_free_shipping_pre_promo`** <span class="field-type">INTEGER</span>

Indicates whether the listing had standard free shipping before a promotional sale.

**`is_free_shipping_sale`** <span class="field-type">INTEGER</span>

Indicates whether the item is on a free-shipping sale promotion.

**`is_intl_shipping_promotion`** <span class="field-type">INTEGER</span>

Indicates whether the item participates in an international shipping promotion.

**`is_domestic_shipping_promotion`** <span class="field-type">INTEGER</span>

Indicates whether the item participates in a domestic shipping promotion.

**`is_gsp_shipping_enabled`** <span class="field-type">INTEGER</span>

Indicates whether Global Shipping Program (GSP) intermediated shipping is enabled for the listing.

**`is_ebay_managed_shipping_eligible`** <span class="field-type">INTEGER</span>

Indicates whether the item is eligible for eBay managed shipping.

**`is_irregular_package`** <span class="field-type">INTEGER</span>

Indicates whether the shipping package is irregular or odd-shaped.

**`is_managed_shipping_opted_in`** <span class="field-type">INTEGER</span>

Indicates whether the seller/listing opted in to managed shipping.

**`is_merchant_fulfillment_supported`** <span class="field-type">INTEGER</span>

Indicates whether merchant fulfillment support / default MSKU price-set fulfillment support is enabled for the listing.

**`is_amex_accepted`** <span class="field-type">INTEGER</span>

Indicates whether American Express is accepted as a payment method for the listing.

**`is_cash_in_person_accepted`** <span class="field-type">INTEGER</span>

Indicates whether cash-in-person payment is accepted, primarily for Motors listings.

**`is_cod_accepted`** <span class="field-type">INTEGER</span>

Indicates whether cash on delivery (COD) is accepted as a payment method.

**`is_cod_prepay_delivery_accepted`** <span class="field-type">INTEGER</span>

Indicates whether China-site COD prepay delivery is accepted for the listing.

**`is_digital_delivery_supported`** <span class="field-type">INTEGER</span>

Indicates whether the item supports digital delivery.

**`is_discover_accepted`** <span class="field-type">INTEGER</span>

Indicates whether Discover card is accepted as a payment method for the listing.

**`is_loan_check_accepted`** <span class="field-type">INTEGER</span>

Indicates whether loan check payment is accepted, primarily for Motors listings.

**`is_money_order_accepted`** <span class="field-type">INTEGER</span>

Indicates whether money order or cashier check is accepted as a payment method.

**`is_other_payment_accepted`** <span class="field-type">INTEGER</span>

Indicates whether another offline/other payment method is accepted.

**`is_other_online_payment_accepted`** <span class="field-type">INTEGER</span>

Indicates whether another online payment method is accepted.

**`is_paisapay_accepted`** <span class="field-type">INTEGER</span>

Indicates whether PaisaPay credit card payment is accepted, primarily for eBay India.

**`is_paisapay_escrow_enabled`** <span class="field-type">INTEGER</span>

Indicates whether PaisaPay escrow is enabled.

**`is_paisapay_escrow_emi_enabled`** <span class="field-type">INTEGER</span>

Indicates whether PaisaPay escrow EMI is enabled.

**`is_payment_in_description`** <span class="field-type">INTEGER</span>

Indicates whether payment details are provided in the listing description.

**`is_paypal_accepted`** <span class="field-type">INTEGER</span>

Indicates whether PayPal is accepted as a payment method for the listing.

**`is_personal_check_accepted`** <span class="field-type">INTEGER</span>

Indicates whether personal check is accepted as a payment method.

**`is_postal_transfer_accepted`** <span class="field-type">INTEGER</span>

Indicates whether postal transfer is accepted as a payment method, primarily for China-site listings.

**`is_prepay_delivery_accepted`** <span class="field-type">INTEGER</span>

Indicates whether pre-pay delivery is accepted as a payment method, primarily for China-site listings.

**`is_visa_mc_accepted`** <span class="field-type">INTEGER</span>

Indicates whether Visa or MasterCard is accepted as a payment method for the listing.

**`is_ebay_plus_supported`** <span class="field-type">INTEGER</span>

Indicates whether the item supports or requested the eBay Plus program.

**`eplus_elgbl_ind`** <span class="field-type">INTEGER</span>

Indicates whether the item is eligible for the eBay Plus business program.

**`attr_brand_txt`** <span class="field-type">STRING</span>

Brand value tagged by the seller from seller-input item specifics, using attr_id 3982.

**`at_cnfdnc`** <span class="field-type">INTEGER</span>

Auto-tag product reference/ePID adoption method for the item. Examples: 1001 = seller adopted, 1003 = GTIN match, 1004 = Brand + MPN match, 5000-5200 = Hydra, 9000 = manual adoption, 11003 = GTIN match to BEP, 11004 = Brand + MPN match to BEP.

**`msct_score_num`** <span class="field-type">STRING</span>

Miscategorization score for the item; scores &gt;= 70 are treated as miscategorized cases.

**`mpn_txt`** <span class="field-type">STRING</span>

Manufacturer Part Number (MPN) for the item, deduplicated across classification, product information, and seller-provided sources.

**`upc_txt`** <span class="field-type">STRING</span>

Universal Product Code (UPC) for the item, deduplicated across classification, product information, and seller-provided sources.

**`isbn_txt`** <span class="field-type">STRING</span>

International Standard Book Number (ISBN) for the item, deduplicated across classification, product information, and seller-provided sources.

**`ean_txt`** <span class="field-type">STRING</span>

European Article Number (EAN) for the item, deduplicated across classification, product information, and seller-provided sources.

**`gtin_txt`** <span class="field-type">STRING</span>

Global Trade Item Number (GTIN) for the item, deduplicated across classification, product information, and seller-provided sources.

**`st_brand_txt`** <span class="field-type">STRING</span>

Brand value from seller input, using the Dynamic Finding (df) namespace aspect value first and falling back to the Non-indexed Finding (nf) namespace aspect value when no df value is available.

**`st_mpn_txt`** <span class="field-type">STRING</span>

Manufacturer Part Number (MPN) from seller input or catalog inheritance, preferring seller-provided value when available.

**`st_upc_txt`** <span class="field-type">STRING</span>

Universal Product Code (UPC) from seller input or catalog inheritance, preferring seller-provided value when available.

**`st_ean_txt`** <span class="field-type">STRING</span>

European Article Number (EAN) from seller input or catalog inheritance, preferring seller-provided value when available.

**`st_isbn_txt`** <span class="field-type">STRING</span>

International Standard Book Number (ISBN) from seller input or catalog inheritance, preferring seller-provided value when available.

**`st_actv_brand_txt`** <span class="field-type">STRING</span>

Active seller-provided brand value currently associated with the item.

**`st_actv_mpn_txt`** <span class="field-type">STRING</span>

Active seller-provided Manufacturer Part Number (MPN) currently associated with the item.

**`st_actv_upc_txt`** <span class="field-type">STRING</span>

Active seller-provided Universal Product Code (UPC) currently associated with the item.

**`st_actv_ean_txt`** <span class="field-type">STRING</span>

Active seller-provided European Article Number (EAN) currently associated with the item.

**`st_actv_isbn_txt`** <span class="field-type">STRING</span>

Active seller-provided International Standard Book Number (ISBN) currently associated with the item.

**`st_ctlg_brand_txt`** <span class="field-type">STRING</span>

Catalog-inherited brand value associated with the item.

**`st_ctlg_mpn_txt`** <span class="field-type">STRING</span>

Catalog-inherited Manufacturer Part Number (MPN) associated with the item.

**`st_ctlg_upc_txt`** <span class="field-type">STRING</span>

Catalog-inherited Universal Product Code (UPC) associated with the item.

**`st_ctlg_ean_txt`** <span class="field-type">STRING</span>

Catalog-inherited European Article Number (EAN) associated with the item.

**`st_ctlg_isbn_txt`** <span class="field-type">STRING</span>

Catalog-inherited International Standard Book Number (ISBN) associated with the item.

**`pi_brand_txt`** <span class="field-type">STRING</span>

Brand value from FCDE (First Class Data Element), using the Dynamic Finding (df) namespace aspect value first and falling back to the Non-indexed Finding (nf) namespace aspect value

**`pi_mpn_txt`** <span class="field-type">STRING</span>

Manufacturer Part Number (MPN) from FCDE (First Class Data Element)

**`pi_upc_txt`** <span class="field-type">STRING</span>

Universal Product Code (UPC) from FCDE (First Class Data Element)

**`pi_ean_txt`** <span class="field-type">STRING</span>

European Article Number (EAN) from FCDE (First Class Data Element)

**`pi_isbn_txt`** <span class="field-type">STRING</span>

International Standard Book Number (ISBN) from FCDE (First Class Data Element)

**`cls_brand_txt`** <span class="field-type">STRING</span>

Brand value from NGC classification source, using the Dynamic Finding (df) namespace aspect value first and falling back to the Non-indexed Finding (nf) namespace aspect value

**`cls_mpn_txt`** <span class="field-type">STRING</span>

Manufacturer Part Number (MPN) from NGC classification source

**`cls_upc_txt`** <span class="field-type">STRING</span>

Universal Product Code (UPC) from NGC classification source

**`cls_ean_txt`** <span class="field-type">STRING</span>

European Article Number (EAN) from NGC classification source

**`cls_isbn_txt`** <span class="field-type">STRING</span>

International Standard Book Number (ISBN) from NGC classification source

**`st_df_brand_txt`** <span class="field-type">STRING</span>

DF brand from seller input.

**`cls_df_brand_txt`** <span class="field-type">STRING</span>

DF brand from NGC classification source.

**`pi_df_brand_txt`** <span class="field-type">STRING</span>

DF brand from FCDE (First Class Data Element).

**`st_nf_brand_txt`** <span class="field-type">STRING</span>

NF brand from seller input.

**`cls_nf_brand_txt`** <span class="field-type">STRING</span>

NF brand from NGC classification source.

**`pi_nf_brand_txt`** <span class="field-type">STRING</span>

NF brand from FCDE (First Class Data Element).

**`trnsltd_df_brand_txt`** <span class="field-type">STRING</span>

DF brand from Translation Classifier.

**`fc_aspct_json`** <span class="field-type">STRING</span>

JSON containing aspect list for the item, such as sport, game, language, and publisher.

**`sport_value_flag`** <span class="field-type">INTEGER</span>

Indicates whether the item has a sport aspect value.

**`sport_value_list_txt`** <span class="field-type">STRING</span>

Text list of sport aspect values associated with the item.

**`game_value_flag`** <span class="field-type">INTEGER</span>

Indicates whether the item has a game aspect value.

**`game_value_list_txt`** <span class="field-type">STRING</span>

Text list of game aspect values associated with the item.

**`language_value_flag`** <span class="field-type">INTEGER</span>

Indicates whether the item has a language aspect value.

**`language_value_list_txt`** <span class="field-type">STRING</span>

Text list of language aspect values associated with the item.

**`publisher_value_flag`** <span class="field-type">INTEGER</span>

Indicates whether the item has a publisher aspect value.

**`publisher_value_list_txt`** <span class="field-type">STRING</span>

Text list of publisher aspect values associated with the item.

**`brws_node_id`** <span class="field-type">LONG</span>

The best matched BrowseNode for each item; the "best" means the browse node has the highest number of aspects.

**`adptn_visit_ts`** <span class="field-type">TIMESTAMP</span>

Timestamp when the item last went through the ePID adoption process.

**`lstg_prod_id`** <span class="field-type">LONG</span>

Product ID provided by the seller on the listing; use st_prod_ref_id for seller-tagged ePID when available.

**`adpt_cnfdnc_num`** <span class="field-type">INTEGER</span>

The confidence score of Auto-Tagged ePID. It's a number from 0 to 100. 100 means the most confidence.

**`mdl_ref_id`** <span class="field-type">LONG</span>

Auto-tag model reference ID. 0 means no model reference but a product reference exists; null means non-cataloged.

**`at_mdl_cnfdnc`** <span class="field-type">INTEGER</span>

Auto-tag model confidence

**`st_prod_ref_id`** <span class="field-type">LONG</span>

Seller-tagged ePID (eBay Product ID) associated with the item.

**`self_tag_yn_ind`** <span class="field-type">INTEGER</span>

Indicates whether the listing was actively adopted/tagged by the seller.

**`prod_cvrg`** <span class="field-type">DOUBLE</span>

Product coverage ratio from variation level to item level. 0 means no product reference coverage, 1 means full coverage, and fractional values indicate partial variation coverage for MSKU items.

**`dmi_mlg_prod_ref_id`** <span class="field-type">LONG</span>

DMI mileage product reference ID associated with the item.

**`dmi_epid_prod_ref_id`** <span class="field-type">LONG</span>

DMI ePID (eBay Product ID) product reference ID associated with the item.

**`dmi_epid1_prod_ref_id`** <span class="field-type">LONG</span>

DMI ePID1 product reference ID associated with the item.

**`dmi_epid2_prod_ref_id`** <span class="field-type">LONG</span>

DMI ePID2 product reference ID associated with the item.

**`dmi_epid3_prod_ref_id`** <span class="field-type">LONG</span>

DMI ePID3 product reference ID associated with the item.

**`dmi_epid4_prod_ref_id`** <span class="field-type">LONG</span>

DMI ePID4 product reference ID associated with the item.

**`dmi_clstr1_prod_ref_id`** <span class="field-type">LONG</span>

DMI cluster1 product reference ID associated with the item.

**`dmi_pbr_prod_ref_id`** <span class="field-type">STRING</span>

DMI PBR product reference ID associated with the item.

**`dmi_epid_json`** <span class="field-type">STRING</span>

JSON containing all DMI ePIDs associated with the item.


Attributes that describe how the listing was created, presented, and managed, including listing status, format, lifecycle dates, seller context, listing tool/channel, media, and operational flags.

**`device_type_level1`** <span class="field-type">STRING</span>

High-level device type used to create the listing. Typical values include Mobile, PC, API, Other, or null.

**`experience_level2`** <span class="field-type">STRING</span>

More granular listing creation experience, such as Apps: iPhone, Apps: Android, Apps: iPad, Browser: mWeb, Browser: Core site, API, or null.

**`mobile_lstg_ind`** <span class="field-type">INTEGER</span>

Indicates whether the listing was created through a mobile listing flow. Values: 1 = mobile listing, 0 = not mobile listing.

**`app_party_type_cd`** <span class="field-type">INTEGER</span>

Application party type code used to identify third-party API listings versus eBay-owned listing flows. Values: 0 = third-party application/tool, 1 = eBay internal tool

**`norl_type_cd`** <span class="field-type">INTEGER</span>

Lister type code. Values: 1 = New Lister (seller's first listed item; differs from `ftl_ind`, which excludes first listings that were admin-ended), 2 = Reactivated Lister (seller's previous listing was at least 12 months earlier), 3 = Existing Lister.

**`ftl_ind`** <span class="field-type">INTEGER</span>

First Time Lister indicator. 1 means this listing is identified as the seller first listing, excluding first listings that were admin-ended.

**`aedl_ind`** <span class="field-type">INTEGER</span>

Admin Ended Day Lister indicator. 1 means the listing occurred before the seller recorded first listing date, implying a prior admin-ended attempt.

**`unsccss_lstr_ind`** <span class="field-type">INTEGER</span>

Unsuccessful Lister indicator. 1 means the seller had listed but had not sold by the listing start date.

**`slng_mgr_sbscrbr_flag`** <span class="field-type">INTEGER</span>

Indicates the seller was a Selling Manager subscriber at listing time. Values: 0 = no, 1 = yes.

**`slng_mgr_pro_sbscrbr_flag`** <span class="field-type">INTEGER</span>

Indicates the seller was a Selling Manager Pro subscriber at listing time. Values: 0 = no, 1 = yes.

**`cust_ref_code`** <span class="field-type">STRING</span>

Universally unique constraint tag. Use UUID to ensure that you only list a particular item once, particularly if you are listing many items at once

**`auct_start_exchng_rate`** <span class="field-type">DOUBLE</span>

Exchange rate to USD at listing start time.

**`auct_end_exchng_rate`** <span class="field-type">DOUBLE</span>

Exchange rate to USD at listing end time.

**`lstg_guid`** <span class="field-type">STRING</span>

Sojourner GUID of the event most closely matching the listing success event. NULL if no match found

**`lstg_session_skey`** <span class="field-type">LONG</span>

Sojourner session key of the listing success event

**`lstg_session_start_dt`** <span class="field-type">DATE</span>

Session start date of the listing success event

**`lstg_event_timestamp`** <span class="field-type">TIMESTAMP</span>

Sojourner event timestamp of the listing success event

**`lstg_seq_num`** <span class="field-type">INTEGER</span>

Sojourner sequence number of the listing success event.


Attributes that describe how buyers can pay for and receive the item, including payment methods, shipping costs, package details, tax, shipping programs, and related policies.

**`is_best_offer_auto_accept_enabled`** <span class="field-type">INTEGER</span>

Indicates whether Best Offer 3.0 auto-accept is enabled for the listing.

**`is_best_offer_auto_decline_enabled`** <span class="field-type">INTEGER</span>

Indicates whether Best Offer auto-decline is enabled for the listing.

**`is_auto_relist_enabled`** <span class="field-type">INTEGER</span>

Indicates whether automatic relisting is enabled for the item.

**`is_best_offer_enabled`** <span class="field-type">INTEGER</span>

Indicates whether Best Offer is enabled for the item.

**`is_bids_finalized`** <span class="field-type">INTEGER</span>

Indicates whether bidding has been finalized for the listing.

**`is_duplicate_auction`** <span class="field-type">INTEGER</span>

Indicates whether the item is identified as a duplicate pure-auction listing.

**`is_ebay_vault_listing`** <span class="field-type">INTEGER</span>

Indicates whether the listing is an eBay Vault listing.

**`is_gtc`** <span class="field-type">INTEGER</span>

Indicates whether the listing is Good Till Cancelled (GTC).

**`is_business_policy_item`** <span class="field-type">INTEGER</span>

Indicates whether the item was listed using a business/selling policy profile.

**`is_no_email_contact_supported`** <span class="field-type">INTEGER</span>

Indicates whether the listing format does not support email contact.

**`is_instore_pickup_eligible`** <span class="field-type">INTEGER</span>

Indicates whether the item is eligible for in-store pickup.

**`is_restricted_bidding`** <span class="field-type">INTEGER</span>

Indicates whether bidding is restricted to pre-approved bidders.

**`is_restricted_to_business_user`** <span class="field-type">INTEGER</span>

Indicates whether the item is restricted to business users.

**`is_seller_on_vacation`** <span class="field-type">INTEGER</span>

Indicates whether the store is on vacation and the listing may be hidden from search.

**`is_variation`** <span class="field-type">INTEGER</span>

Indicates whether the listing is a multi-SKU variation item.

**`is_on_promotional_sale`** <span class="field-type">INTEGER</span>

Indicates whether the item is on an active promotional sale.

**`is_marketplace_visible`** <span class="field-type">INTEGER</span>

Indicates whether the item is visible in marketplace experiences.

**`is_managed_by_inventory`** <span class="field-type">INTEGER</span>

Indicates whether the listing is managed by an inventory/SKUBI system.

**`is_on_hold`** <span class="field-type">INTEGER</span>

Indicates whether the item is on hold and may not be visible or purchasable even if otherwise live.

**`is_price_guarantee`** <span class="field-type">INTEGER</span>

Indicates whether price guarantee applies to the listing; this flag is generally expected to be false.

**`is_partner_dealer_auto_listing`** <span class="field-type">INTEGER</span>

Indicates whether the listing is a partner dealer auto listing.

**`is_relisted`** <span class="field-type">INTEGER</span>

Indicates whether the item was created via a relist flow.

**`is_scheduled_listing`** <span class="field-type">INTEGER</span>

Indicates whether the listing is scheduled and not live yet.

**`is_seller_policy_overridden`** <span class="field-type">INTEGER</span>

Indicates whether seller policy/profile values were overridden for the listing.

**`is_sell_similar`** <span class="field-type">INTEGER</span>

Indicates whether the item was created via a Sell Similar flow.

<!-- END GENERATED ITEM FIELDS -->

---

## Sample Queries

### Get US Listings in a Category

```sql
SELECT
    item_id,
    auct_titl             AS title,
    bin_price_lstg_curncy AS price,
    qty_avail,
    item_cndtn_id         AS condition_id,
    slr_id
FROM gds.item
WHERE item_site_id = 0          -- US site
  AND leaf_categ_id = 9355      -- Cell Phones & Accessories
  AND lstg_status_id = 0        -- Live listings
LIMIT 100;
```

### Filter by Condition and Price Range

```sql
-- New items within a price range
SELECT
    item_id,
    auct_titl             AS title,
    bin_price_lstg_curncy AS price,
    item_cndtn_id         AS condition_id
FROM gds.item
WHERE item_site_id = 0          -- US site
  AND item_cndtn_id = 1000      -- 1000 = New
  AND bin_price_lstg_curncy BETWEEN 100 AND 500
  AND lstg_status_id = 0        -- Live listings
ORDER BY bin_price_lstg_curncy ASC
LIMIT 100;
```

[More query examples →](../guides/query-examples.md)

---

## Relationships

| Target LDM | Type | How to Join |
|------------|------|-------------|
| `variation` | 1:N | `gds.variation.item_id = gds.item.item_id` |
| `product` | N:1 | `gds.product.prod_ref_id = gds.item.st_prod_ref_id` |
| `site` | N:1 | `gds.site.site_id = gds.item.item_site_id` |
| `category` | N:1 | `gds.category.site_id = gds.item.item_site_id` and `gds.category.leaf_categ_id = gds.item.leaf_categ_id` |
| `country` | N:1 | `gds.country.country_id = gds.item.item_cntry_id` |
| `msku` | 1:1 | `gds.msku.item_id = gds.item.item_id` |
| `ssku` | 1:1 | `gds.ssku.item_id = gds.item.item_id` |

[View full entity relationship diagram →](../index.md#entity-relationships)

---

!!! tip "Useful Links"
    - :material-swap-horizontal: [Migrating from legacy tables (DW_LSTG_ITEM, etc.)?](../guides/migration-guide.md)
    - :material-magnify: [More query examples](../guides/query-examples.md)
