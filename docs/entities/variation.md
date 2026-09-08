# Variation LDM

[← Back to LDM Catalog](../index.md)

## Overview

**LDM Name:** `variation`

**Description:** The SKU-level variation entity in the Item Domain. Each record represents one SKU (Stock Keeping Unit) variation of a multi-SKU listing, containing variation-specific pricing, quantity, condition, media, shipping, payment, and policy information.

**Primary Key:** `item_vrtn_id`

**Relationship Type:** Child Entity (belongs to Item via 1:N relationship — `gds.variation.item_id = gds.item.item_id`)

---

## Fields (159)

<!-- BEGIN GENERATED VARIATION FIELDS -->

**`item_vrtn_id`** <span class="field-type">LONG</span>

A unique SKU(stock keeping unit) identifier which stands for each variation of multi-SKU listing. only multi-SKU listing will have item_variation_id.

**`item_id`** <span class="field-type">LONG</span>

A unique identifier for the listing, generated upon successful creation. FK to ITEM.item_id

**`item_vrsn_id`** <span class="field-type">LONG</span>

This column will be populated in the revise process, and will contain a unique identifier for a specific version of an item listing

**`slr_prdct_id_txt`** <span class="field-type">STRING</span>

The SKU (stock-keeping unit) product identifier text defined by a seller.

**`price_amt`** <span class="field-type">DOUBLE</span>

Price for the SKU variation in the listing currency. individual SKUs can have different prices from the listing price in ITEM

**`orgnl_price_amt`** <span class="field-type">DOUBLE</span>

Original Price for the SKU variation when a sale happens. This value will be set by the Mark Down Manager flow.

**`qty`** <span class="field-type">INTEGER</span>

Number of quantity available for this SKU.

**`sold_qty`** <span class="field-type">LONG</span>

Number of sold quantities for this SKU.

**`dlt_sts_yn_ind`** <span class="field-type">STRING</span>

To identify the status of the SKU. The SKU could be soft deleted by the seller. Value of 'Y' would mean the SKU has been soft deleted by the seller.

**`glry_url_txt`** <span class="field-type">STRING</span>

Single gallery image URL for the SKU, usually the first picture URL, shown as extenal picture URL + ";"+ eBay picture URL

**`auct_end_dt`** <span class="field-type">DATE</span>

This is the date that the SKU ended on or is scheduled to end on.

**`mfo_price_lc_amt`** <span class="field-type">DOUBLE</span>

The discount price for "made for outlet" items

**`map_price_lc_amt`** <span class="field-type">DOUBLE</span>

The discount price for "minimum advised price" items

**`stp_price_lc_amt`** <span class="field-type">DOUBLE</span>

The discount price for "strike thru price" items

**`price_trtmnt_cd`** <span class="field-type">INTEGER</span>

the discount price treatment type (1-STP, 2-MAP, 3-MFO, 0-None)

**`upc_num`** <span class="field-type">STRING</span>

UPC(Universal Product Code) code of the SKU

**`isbn_num`** <span class="field-type">STRING</span>

ISBN(International Standard Book Number) number of the SKU.

**`ean_num`** <span class="field-type">STRING</span>

EAN(European Article Number) number of the SKU.

**`gtin_num`** <span class="field-type">STRING</span>

GTIN(Global Trade Item Number) number of the SKU.

**`inc_eby_prdt_dtail`** <span class="field-type">BOOLEAN</span>

Indicates whether eBay product details are included for the SKU. Possible values: True = eBay product details are included, False = eBay product details are not included, Null = no value present / not populated.

**`inc_stk_phto_url`** <span class="field-type">BOOLEAN</span>

Indicates whether the stock photo URL is included for the SKU. Possible values: True = stock photo URL is included, False = stock photo URL is not included, Null = no value present / not populated.

**`bids_fl`** <span class="field-type">BOOLEAN</span>

Indicates whether the SKU BIN activity on the listing has concluded . Possible values: True = SKU BIN activity concluded, False = SKU BIN activity not concluded, Null = no value present / not populated.

**`buyer_rst_dsbld`** <span class="field-type">BOOLEAN</span>

Indicates whether buyer restrictions are disabled for the SKU. Possible values: True = buyer restrictions are disabled, False = buyer restrictions are not disabled, Null = no value present / not populated.

**`cnd_id_num`** <span class="field-type">INTEGER</span>

Stores the numeric condition ID for the SKU. This is the integer representation of the item condition and is used alongside conditionId and conditionDesc in the listing record.

**`condition_desc`** <span class="field-type">STRING</span>

Stores the condition description for the SKU. This field contains the human-readable description of the item condition when a textual condition description is present.

**`condition_id`** <span class="field-type">STRING</span>

Stores the condition identifier for the SKU. This field contains the condition enum value used for the listing, such as NEW,USED ,LIKE_NEW,GOOD,VERY_GOOD etc..

**`creation_mode`** <span class="field-type">STRING</span>

Stores the creation mode for the SKU. This field identifies how the listing was created, such as Add, Relist, or SellSimilar.

**`ftmt_id`** <span class="field-type">STRING</span>

Stores the fitment ID associated with the SKU. This field is used in the listing’s fitment/compatibility context and relates to parts compatibility or fitment data.

**`gbl_identifiers`** <span class="field-type">ARRAY</span>

Stores the global product identifiers for the SKU. This field is modeled as a list of name/value pairs and can contain identifiers such as UPC, EAN, and ISBN.

**`invntry_trk_mthd`** <span class="field-type">STRING</span>

Specifies the inventory tracking method for the SKU. This field determines whether inventory is tracked by SKU or by ItemID

**`is_buyer_responsible_for_shipping`** <span class="field-type">BOOLEAN</span>

Indicates whether the buyer is responsible for shipping for the SKU. This field is used for Motors shipping scenarios where the buyer pays or arranges shipping. Possible values: True = buyer is responsible for shipping, False = buyer is not responsible for shipping.

**`is_created_by_sell_similar`** <span class="field-type">BOOLEAN</span>

Indicates whether the SKU was created using the Sell Similar flow. Possible values: True = created via Sell Similar, False = not created via Sell Similar.

**`is_listed_with_no_contact_via_email_support`** <span class="field-type">BOOLEAN</span>

Indicates whether the SKU was listed in a format that does not support contacting the seller by email. Possible values: True = no contact-via-email support, False = email contact support is allowed.

**`is_restricted_bidding`** <span class="field-type">BOOLEAN</span>

Indicates whether bidding is restricted for the SKU. This field is used when the item requires pre-approved bidders. Possible values: True = restricted bidding is enabled, False = restricted bidding is not enabled.

**`is_restricted_to_business_user`** <span class="field-type">BOOLEAN</span>

Indicates whether the SKU is restricted to business users only. Possible values: True = restricted to business users, False = not restricted to business users.

**`is_seller_on_vacation`** <span class="field-type">BOOLEAN</span>

Indicates whether seller vacation hold applies to the SKU. This field is used to hide eligible items from buyer discoverability while the seller is on vacation. Possible values: True = seller vacation hold applies, False = seller vacation hold does not apply.

**`itm_on_sale`** <span class="field-type">BOOLEAN</span>

Indicates whether the SKU is on an active promotional sale. Possible values: True = the SKU is on an active promotional sale, False = the SKU is not on an active promotional sale, Null = legacy.

**`itm_revsn_dt`** <span class="field-type">LONG</span>

Stores the item revision date for the SKU. This field is a bigint timestamp stored in epoch milliseconds.

**`mng_by_inv`** <span class="field-type">BOOLEAN</span>

Indicates whether the SKU is managed by inventory. Possible values: True = managed by inventory, False = not managed by inventory.

**`on_hold`** <span class="field-type">BOOLEAN</span>

Indicates whether the SKU is on hold. This field represents the listing’s on-hold status. Possible values: True = on hold, False = not on hold.

**`out_of_stock_dt`** <span class="field-type">LONG</span>

Stores the out-of-stock date for the SKU. This field is a bigint timestamp stored in epoch milliseconds.

**`prg_spprtd`** <span class="field-type">ARRAY</span>

Stores the list of programs supported for the SKU.

**`veh_pkg_id`** <span class="field-type">STRING</span>

Stores the vehicle package ID associated with the SKU. This field is used for Motors listings.

**`videos`** <span class="field-type">ARRAY</span>

Stores the videos attached to the SKU listing. This field is modeled as an array of video structures, not a single value.

**`epr_eco_fee`** <span class="field-type">DOUBLE</span>

Specifies the Extended Producer Responsibility (EPR) eco fee for the SKU variation.

**`epr_prd_doc_id`** <span class="field-type">STRING</span>

Stores the Extended Producer Responsibility (EPR) product document identifier associated with the SKU.

**`epr_prd_pkg_id`** <span class="field-type">STRING</span>

Stores the Extended Producer Responsibility (EPR) product package identifier associated with the SKU.

**`epr_prdcr_id`** <span class="field-type">STRING</span>

Stores the Extended Producer Responsibility (EPR) producer identifier associated with the SKU.

**`epr_shp_pkg_id`** <span class="field-type">STRING</span>

Stores the Extended Producer Responsibility (EPR) shipment package identifier associated with the SKU.

**`lifecycle_duration`** <span class="field-type">STRING</span>

Specifies the listing duration for the SKU, it can be null. and the value 'GTC' means 'GOOD TILL CANCEL'

**`on_free_ship_pr_to_promo`** <span class="field-type">BOOLEAN</span>

Indicates whether the SKU had standard free shipping before it was placed into a promotional free shipping sale. Possible values: True = the SKU was on standard free shipping prior to the promotional free shipping sale, False = it was not.

**`on_free_ship_sale`** <span class="field-type">BOOLEAN</span>

Indicates whether the SKU is on a promotional free shipping sale. Possible values: True = the SKU is on a promotional free shipping sale, False = it is not.

**`aplcbl_to_shp`** <span class="field-type">BOOLEAN</span>

Indicates whether sales tax is applicable to the shipping fee for the SKU/listing. Possible values: True = tax applies to shipping, False = tax does not apply to shipping.

**`tax_rcgnz_bsns_slr_vat`** <span class="field-type">BOOLEAN</span>

Indicates whether the SKU/listing is recognized as a business seller for VAT purposes.It is a boolean field with values true or false.

**`tax_thrd_prt_tx_ctg_cd`** <span class="field-type">STRING</span>

Stores the third-party tax category code for the SKU/listing.

**`tax_vat_pct`** <span class="field-type">DOUBLE</span>

Specifies the VAT percentage for the SKU/listing as a numeric tax rate.

**`trd_scp_intl_st_vsbl`** <span class="field-type">ARRAY</span>

Stores the list of international site visibility targets for the SKU/listing. T

**`aut_accpt_enbld`** <span class="field-type">BOOLEAN</span>

Indicates whether Best Offer auto accept is enabled for the SKU. Possible values: True = auto accept is enabled, False = auto accept is not enabled.

**`best_ofr_trms_aut_acpt_thrsh_prc_currency`** <span class="field-type">STRING</span>

Specifies the currency code for the Best Offer auto-accept threshold price for the SKU.

**`best_ofr_trms_aut_acpt_thrsh_prc_value`** <span class="field-type">DOUBLE</span>

Specifies the Best Offer auto-accept threshold price value for the SKU.

**`aut_dcln_enbld`** <span class="field-type">BOOLEAN</span>

Indicates whether Best Offer auto decline is enabled for the SKU. Possible values: True = auto decline is enabled, False = auto decline is not enabled.

**`best_ofr_trms_aut_dcln_thrsh_prc_currency`** <span class="field-type">STRING</span>

Specifies the currency code for the Best Offer auto-decline threshold price for the SKU.

**`best_ofr_trms_aut_dcln_thrsh_prc_value`** <span class="field-type">DOUBLE</span>

Specifies the Best Offer auto-decline threshold price value for the SKU.

**`buyer_rstrctns_min_fdbk_score`** <span class="field-type">INTEGER</span>

Specifies the minimum feedback score a buyer must have to be eligible to purchase the SKU when buyer restrictions are applied.

**`buyer_rstrctns_prchs_rate_qnty_lmt_per_byr`** <span class="field-type">INTEGER</span>

Specifies the maximum quantity of the SKU that a single buyer is allowed to purchase when buyer purchase-rate restrictions apply.

**`qnty_lmt_per_byr`** <span class="field-type">INTEGER</span>

Specifies the maximum quantity of the SKU that a single buyer is allowed to purchase. This field is used to enforce per-buyer quantity limits for the listing.

**`rstrct_bid`** <span class="field-type">BOOLEAN</span>

Indicates whether bidding is restricted for the SKU.

**`rstrct_to_bsns_usr`** <span class="field-type">BOOLEAN</span>

Indicates whether the SKU is restricted to business users only. When enabled, the listing is intended for business-buyer contexts rather than general consumer purchase.

**`rstrctn_date`** <span class="field-type">LONG</span>

Specifies the date associated with a restriction for the SKU. This field can be used to capture the effective, recorded, or applicable date of a buyer or listing restriction for downstream processing.

**`unpaid_tran_thrsh_count`** <span class="field-type">INTEGER</span>

Specifies the unpaid-transaction count threshold used for the SKU.

**`byr_rstrct_dsbld`** <span class="field-type">BOOLEAN</span>

Indicates whether buyer restrictions are disabled for the SKU. When enabled, buyer-restriction rules are not enforced for the listing.

**`cash_on_dlvry_fee_currency`** <span class="field-type">STRING</span>

Specifies the currency used for the cash-on-delivery fee applied to the SKU. This field identifies the monetary denomination for the COD fee amount.

**`cash_on_dlvry_fee_value`** <span class="field-type">DOUBLE</span>

Specifies the cash-on-delivery fee amount applied to the SKU. This field stores the fee charged when the buyer selects cash on delivery as the payment method.

**`dgt_dlv_lgs_pl_sprt`** <span class="field-type">BOOLEAN</span>

Flag to determine if the item can be delivered as a digital good

**`ebay_mgd_shpng`** <span class="field-type">BOOLEAN</span>

Indicates whether eBay Managed Shipping is enabled for the SKU.Possible values: True = eBay Managed Shipping is enabled, False = eBay Managed Shipping is not enabled, Null = no value present / not populated.

**`free_ship_avail`** <span class="field-type">BOOLEAN</span>

Indicates whether free shipping is available for the SKU.Possible values: True = free shipping is available, False = free shipping is not available.

**`gsp_lgstc_pln_sprtd`** <span class="field-type">BOOLEAN</span>

Flag to indicate if the item is listed using an Intermediated Shipping enabled business profile

**`ispu_lgstc_pl_sprt`** <span class="field-type">BOOLEAN</span>

Flag to determine if an item is eligible for pickup in store or not

**`m_fulfillment_sprt`** <span class="field-type">BOOLEAN</span>

Indicates whether managed fulfillment is supported for the SKU.Possible values: True = managed fulfillment is supported, False = managed fulfillment is not supported, Null = no value present / not populated.

**`mgd_shpng_cst_pd_by`** <span class="field-type">STRING</span>

Specifies who(Buyer vs Seller) pays the managed shipping cost for the SKU. It can be null. This field is part of the managed shipping or fulfillment terms and is stored as a managed-shipping-cost-paid-by .

**`mgd_shpng_optin`** <span class="field-type">BOOLEAN</span>

Indicates whether managed shipping is opted in for the SKU.Possible values: True = managed shipping is opted in, False = managed shipping is not opted in, Null = no value present / not populated.

**`ovrrid_ship_optn`** <span class="field-type">ARRAY</span>

Stores the list of override shipping options for the SKU. It is used when the seller overrides the flat shipping costs in the Business Policies shipping profile for domestic or international shipping services.

**`pkg_spec_depth`** <span class="field-type">DOUBLE</span>

Specifies the package depth for the SKU. This field stores the depth component of the shipping package dimensions associated with the SKU and is part of the package-dimension structure used to define a shipping package.

**`pkg_spec_length`** <span class="field-type">DOUBLE</span>

Specifies the package length for the SKU. This field stores the length component of the shipping package dimensions associated with the SKU and is used together with width and depth to define the full package size for shipping-related processing.

**`pkg_spec_width`** <span class="field-type">DOUBLE</span>

Specifies the package width for the SKU. This field stores the width component of the shipping package dimensions associated with the SKU and is used together with length and depth as part of the package specification for shipping.

**`irregular_package`** <span class="field-type">BOOLEAN</span>

Indicates whether the shipping package for the SKU has an irregular or non-standard shape. Possible values: True = the package has an irregular shape, False = the package does not have an irregular shape.

**`unit_of_measure`** <span class="field-type">STRING</span>

Specifies the unit of measure associated with the SKU. This field identifies the measurement unit used to interpret related quantity, weight, dimension, or package-specific values stored for the SKU.

**`pkg_spec_major_weight`** <span class="field-type">DOUBLE</span>

Specifies the major weight component of the package specification for the SKU. This field stores the higher-order weight value used in package definition, typically representing the primary weight unit for shipment calculation.

**`pkg_spec_minor_weight`** <span class="field-type">DOUBLE</span>

Specifies the minor weight component of the package specification for the SKU. This field stores the lower-order weight value used along with the major weight component to represent the complete package weight for the SKU.

**`pymt_plcy_id_plcy_vrsn`** <span class="field-type">STRING</span>

Stores the version of the payment business policy used for the SKU. This helps identify which version of the payment policy was associated with the listing record.

**`pymt_plcy_id_policy_id`** <span class="field-type">STRING</span>

Stores the identifier of the payment business policy associated with the SKU.

**`rtrns_plcy_id_plcy_vrsn`** <span class="field-type">STRING</span>

Stores the version of the returns business policy used for the SKU. This helps identify which version of the returns policy was associated with the listing record.

**`rtrns_plcy_id_policy_id`** <span class="field-type">STRING</span>

Stores the identifier of the returns business policy associated with the SKU.

**`ship_plcy_id_plcy_vrsn`** <span class="field-type">STRING</span>

Stores the version of the shipping business policy used for the SKU. This helps identify which version of the shipping policy was associated with the listing record.

**`ship_plcy_id_policy_id`** <span class="field-type">STRING</span>

Stores the identifier of the shipping business policy associated with the SKU.

**`gall_durtn`** <span class="field-type">STRING</span>

Specifies the gallery duration for the SKU listing. This captures how long the gallery enhancement is applied; example values may include Days_7,Lifetime etc..

**`application_id`** <span class="field-type">INTEGER</span>

Application identifier used by external consumers for the SKU. It identifies the application or listing tool associated with creation of the original listing and can be used to derive the application name from application metadata. Common examples include 219527 = BOLT, 290356 = BOLT B2C, 384352 = HELIX, 2828 = File Exchange, 114100 = Auto Relist, 161592 = Webinterpret (3rd-party international listing/repricing tool), this is the FK to DW_APPLICATIONS

**`bold_title`** <span class="field-type">STRING</span>

Indicates whether the SKU variation item title is displayed in boldface. Valid values are 0 = not bold, 1 = bold, and blank = legacy historical records not tracked. Does not affect the item subtitle. Not applicable to eBay Motors.

**`category_prmry`** <span class="field-type">LONG</span>

Primary category ID for the SKU listing.

**`category2_scndry`** <span class="field-type">LONG</span>

Secondary category ID for the SKU listing.

**`country_id`** <span class="field-type">INTEGER</span>

Unique identifier of the country where the SKU is physically located, as declared by the seller. This reflects the item location country, not the seller registration country.

**`created_ts`** <span class="field-type">TIMESTAMP</span>

Date and time the SKU variation row was created.

**`customer_reference_code`** <span class="field-type">STRING</span>

Universally unique constraint tag for the SKU. Use UUID to ensure that you only list a particular SKU once, particularly if you are listing many SKUs at once.

**`end_code`** <span class="field-type">INTEGER</span>

The code that identifies why the SKU ended. Potential values are 0 = NONE, 1 = LOST, 2 = NOT_AVAILABLE, 3 = ERROR_IN_PRICE, 4 = ERROR_IN_LISTING, 5 = END_AUCTION_AND_SELL, 9 = SOLD_ON_PROSTORE, 10 = SOLD_VEHICLE, 11 = END_ITEM_ON_ZERO_QUANTITY, 12 = PRODUCT_DELETED, and 99 = GTC_ENDED.

**`gallery_type_id`** <span class="field-type">INTEGER</span>

Indicates the type of gallery image for the SKU. Potential values are 0 = NONE, 1 = GALLERY, 2 = FEATURED, 3 = UNGALLERY, 4 = UNFEATURED, 5 = HOMEPAGE_FEATURE, 6 = STOCK_PHOTO, 7 = PLUS, 8 = UNPLUS, and -99999999 = INVALID.

**`item_title`** <span class="field-type">STRING</span>

Name of the SKU as it appears in the search results.

**`last_modified_ts`** <span class="field-type">TIMESTAMP</span>

Date and time the SKU was last modified.

**`location`** <span class="field-type">STRING</span>

Seller-provided textual geographical location of the SKU item.

**`lot_size`** <span class="field-type">LONG</span>

Indicates the number of items in the lot for the SKU. A lot is a set of two or more similar items included in a single listing that must be purchased together in a single order line item.

**`owner`** <span class="field-type">LONG</span>

Seller’s Oracle user ID associated with the SKU. This is the internal user identifier for the seller and can be used as a foreign key to user LDM.

**`package_size_package_type_id`** <span class="field-type">INTEGER</span>

Shipping package type code for the SKU. It identifies the package format used to ship the item(s). Values are 0 = None/not specified, 4 = Package/Thick Envelope, 1 = Letter, 26 =PaddedBags, 5 = USPSLargePack, 2 = Large Envelope, 19 = ParcelOrPaddedEnvelope, 29 = MailingBoxes, 27 = ToughBags, 21 = MediumCanadaPostBox, 22 = LargeCanadaPostBox, 24 = MediumCanadaPostBubbleMailer, 17 = ExtraLargePack 30 = Winepak, and 7 = UPS Letter.

**`photo_display_type`** <span class="field-type">INTEGER</span>

Photo display mode code for the SKU variation. Valid values are -99999999 = invalid, 1 = Slide Show, 2 = Large Photo Show, 3 = Picture Pack, 4 = EPS Picture Show, 5 = Self Hosted Picture Show, and 6 = SuperSize Picture Show.

**`picture_url`** <span class="field-type">STRING</span>

URL(s) of the View Item pictures for the SKU. Multiple URLs may appear semicolon-delimited.

**`private_sale_ind`** <span class="field-type">STRING</span>

Indicates whether the SKU is a private listing where bidder identities are hidden. Values are 0 = not private and 1 = private.

**`sale_end_ts`** <span class="field-type">TIMESTAMP</span>

Timestamp when the SKU actually becomes ended on eBay.

**`sale_sched_end_ts`** <span class="field-type">TIMESTAMP</span>

Timestamp when the SKU is scheduled to end on eBay.

**`sale_start_ts`** <span class="field-type">TIMESTAMP</span>

Timestamp when the SKU becomes active on eBay.

**`seller_product_id`** <span class="field-type">STRING</span>

Seller-defined product identifier text for the SKU.

**`site_id`** <span class="field-type">INTEGER</span>

Site ID where the SKU is listed.

**`sku_num`** <span class="field-type">STRING</span>

Seller's custom, application-specific data associated with the SKU. This data is stored by eBay for the seller and is not used by eBay in any way.

**`storefront_category2`** <span class="field-type">LONG</span>

Unique identifier for the secondary custom Store category for the SKU. Set this field to a root-level custom category or a custom category that has no child categories (subcategories).

**`storefront_flags`** <span class="field-type">LONG</span>

Unique identifier of the primary custom Store category for the SKU. This represents the primary custom category associated with the store listing; sellers can associate each listing with up to two custom Store categories.

**`subtitle`** <span class="field-type">STRING</span>

Contains the full text of the subtitle for the SKU. This value can be null if not supplied by the seller.

**`super_featured`** <span class="field-type">STRING</span>

Indicates whether the SKU is a super-featured (top-of-category) listing upgrade. Values are 0 = not super-featured, 1 = super-featured, and empty string = legacy records.

**`tax_new`** <span class="field-type">DOUBLE</span>

Seller-provided sales tax percentage for the SKU.

**`tax_new_state`** <span class="field-type">STRING</span>

State or jurisdiction for which sales tax is collected for the SKU.

**`gtc`** <span class="field-type">BOOLEAN</span>

Indicates whether the SKU is a Good ’Til Cancelled (GTC) listing.Possible values: True = GTC listing, False = not a GTC listing.

**`relist`** <span class="field-type">BOOLEAN</span>

Indicates whether the SKU was created using the Relist flow.Possible values: True = created via Relist, False = not created via Relist.

**`weight`** <span class="field-type">LONG</span>

Item weight for the SKU in the unit specified by WEIGHT_UNIT_TYPE.

**`weight_unit_type`** <span class="field-type">INTEGER</span>

Indicates the unit of weight for the SKU. Valid values are 1 = Ounces and 2 = Grams.

**`sale_type`** <span class="field-type">LONG</span>

Appropriate SaleTypeEnum code for the SKU. Only fixed_price listings can have SKU variations

**`prc_guarantee`** <span class="field-type">BOOLEAN</span>

Indicates whether the SKU has a price guarantee. This boolean field identifies whether the SKU is enrolled in a price-guarantee or price-protection condition. Possible Values True , False .

**`item_qty_price_id`** <span class="field-type">STRING</span>

Stores the identifier for the item quantity pricing associated with the SKU.

**`currency_id`** <span class="field-type">INTEGER</span>

Specifies the currency identifier for the SKU. It indicates the currency in which the SKU value is expressed and maps to supported currency codes such as 1 = USD, 2 = CAD, 3 = GBP, 5 = AUD, 6 = JPY, and 7 = EUR. FK to dw_currencies.

**`bin_price_lstg_currency`** <span class="field-type">DOUBLE</span>

Specifies the Buy It Now price of the SKU variation in the listing currency. This field stores the fixed-price amount associated with the variation in the currency used for the listing.

**`original_price`** <span class="field-type">DOUBLE</span>

Specifies the original price of the SKU variation before any promotional or markdown sale discount is applied. This field stores the pre-discount price used as the reference value for comparison against the discounted selling price.

**`reserve_price_lstg_currency`** <span class="field-type">DOUBLE</span>

Lowest price at which the seller is willing to sell the SKU in an auction listing. START_PRICE must be lower than RESERVE_PRICE. Value 0 indicates that no reserve price is set.

**`start_price_lstg_currency`** <span class="field-type">DOUBLE</span>

Start price for the SKU in listing currency. For fixed-price SKU, this is the Buy It Now price; for auction or Dutch listing, it is the opening bid price.

**`days_to_ful_pmt`** <span class="field-type">STRING</span>

Specifies the number of days allowed for full payment for the SKU. This field defines the payment window within which the buyer is expected to complete the full payment after the purchase or commitment. It is used to enforce or track payment timing requirements for the listing.

**`pmt_trms_dep_amt_currency`** <span class="field-type">STRING</span>

Specifies the currency code for the deposit amount required for the SKU. This field identifies the currency in which the deposit amount is defined, ensuring that the deposit value is interpreted correctly in the payment terms. It should align with the currency used for the related payment or listing context.

**`pmt_trms_dep_amt_value`** <span class="field-type">DOUBLE</span>

Specifies the deposit amount required for the SKU as part of its payment terms. This field stores the monetary amount that must be paid upfront as a deposit. It is used together with the deposit currency and deposit timing fields to define the complete deposit requirement.

**`dep_rqd`** <span class="field-type">BOOLEAN</span>

Indicates whether a deposit is required for the SKU. This boolean flag identifies whether the listing requires the buyer to pay an upfront deposit as part of the payment terms. A value of true means a deposit applies, while false means no deposit is required.

**`hrs_to_dep`** <span class="field-type">INTEGER</span>

Specifies the number of hours allowed to make the deposit for the SKU. This field defines the deadline for the buyer to submit the required deposit after purchase or commitment. It is used along with the deposit amount and deposit-required flag to control deposit payment terms.

**`pmt_mthd`** <span class="field-type">ARRAY</span>

Stores the list of payment methods accepted for the SKU. This field is part of the payment terms in the business policy and is modeled as an array of PaymentMethod values, so it can contain multiple accepted payment methods for the same SKU rather than a single flag. Downstream boolean payment fields such as COD, CashInPerson, Discover, LoanCheck, MOCC, OtherOnlinePayments, PaymentSeeDescription, PersonalCheck, and VisaMC are derived by checking whether those values are present in pmtMthd.

**`am_ex`** <span class="field-type">BOOLEAN</span>

Indicates whether American Express is accepted as a payment option for the SKU. Possible values: True = American Express is accepted, False = American Express is not accepted.

**`cod`** <span class="field-type">BOOLEAN</span>

Indicates whether Cash on Delivery is accepted as a payment option for the SKU. When this option is enabled, the buyer pays for the item at the time of delivery instead of paying in advance through an online payment flow. This field is used to identify whether the SKU supports COD as one of its available payment methods. Possible values: True = COD is accepted, False = COD is not accepted.

**`codpre_pay_delivery`** <span class="field-type">BOOLEAN</span>

Indicates whether COD pre-pay delivery is enabled for the SKU. This field identifies whether the SKU supports the CODPrePayDelivery payment method as part of its listing payment terms. Possible values: True = COD pre-pay delivery is enabled, False = COD pre-pay delivery is not enabled.

**`discover`** <span class="field-type">BOOLEAN</span>

Indicates whether Discover is accepted as a payment option for the SKU. Possible values: True = Discover is accepted, False = Discover is not accepted.

**`loan_check`** <span class="field-type">BOOLEAN</span>

ndicates whether Loan Check is accepted as a payment option for the SKU. Possible values: True = Loan Check is accepted, False = Loan Check is not accepted.

**`mocc`** <span class="field-type">BOOLEAN</span>

Indicates whether Money Order or Cashier’s/Bank Check is accepted as a payment option for the SKU. Possible values: True = MOCC is accepted, False = MOCC is not accepted.

**`other`** <span class="field-type">BOOLEAN</span>

Indicates whether other forms of payment are accepted as a payment option for the SKU. Possible values: True = other forms of payment are accepted, False = they are not accepted.

**`other_online_payments`** <span class="field-type">BOOLEAN</span>

Indicates whether other online payments are accepted as a payment option for the SKU. Possible values: True = other online payments are accepted, False = they are not accepted.

**`payment_see_description`** <span class="field-type">BOOLEAN</span>

Indicates whether PaymentSeeDescription is accepted as a payment option for the SKU. Possible values: True = PaymentSeeDescription is accepted, False = PaymentSeeDescription is not accepted.

**`pay_pal`** <span class="field-type">BOOLEAN</span>

Indicates whether PayPal is accepted as a payment option for the SKU. Possible values: True = PayPal is accepted, False = PayPal is not accepted.

**`postal_transfer`** <span class="field-type">BOOLEAN</span>

Indicates whether Postal Transfer is accepted as a payment option for the SKU. Possible values: True = Postal Transfer is accepted, False = Postal Transfer is not accepted.

**`pre_pay_delivery`** <span class="field-type">BOOLEAN</span>

Indicates whether PrePayDelivery is accepted as a payment option for the SKU.Possible values: True = PrePayDelivery is accepted, False = PrePayDelivery is not accepted.

**`visa_mc`** <span class="field-type">BOOLEAN</span>

Indicates whether Visa or MasterCard is accepted as a payment option for the SKU. This field maps to the VisaMC payment method in listing/payment policy terms, and internal payment method definitions describe VisaMC as “Visa/Mastercard.” Possible values: True = Visa or MasterCard is accepted, False = Visa or MasterCard is not accepted.

**`payment_cc`** <span class="field-type">STRING</span>

Indicates whether credit card payment is accepted as a payment method for the SKU. Values: "0"=no, "1"=yes, empty string=legacy records.

**`payment_moneyxfer`** <span class="field-type">STRING</span>

Indicates whether direct money transfer is accepted as a payment method for the SKU. Values: "0"=no, "1"=yes, empty string=legacy records.
<!-- END GENERATED VARIATION FIELDS -->

---

## Sample Queries

### Get Active SKUs for a Listing

```sql
SELECT
    item_vrtn_id,
    item_id,
    price_amt,
    qty,
    sold_qty,
    item_title
FROM gds.variation
WHERE item_id = 123456789
  AND dlt_sts_yn_ind <> 'Y'  -- exclude soft-deleted SKUs
ORDER BY item_vrtn_id;
```

### Aggregate SKU Inventory for Multi-SKU Listings

```sql
SELECT
    item_id,
    COUNT(item_vrtn_id)    AS sku_count,
    SUM(qty)               AS total_qty,
    SUM(sold_qty)          AS total_sold,
    MIN(price_amt)         AS min_price,
    MAX(price_amt)         AS max_price
FROM gds.variation
WHERE dlt_sts_yn_ind <> 'Y'
GROUP BY item_id
HAVING COUNT(item_vrtn_id) > 1;
```

[More query examples →](../guides/query-examples.md)

---

## Relationships

| Target LDM | Type | How to Join |
|------------|------|-------------|
| `item` | N:1 | `gds.variation.item_id = gds.item.item_id` |
| `site` | N:1 | `gds.site.site_id = gds.variation.site_id` |
| `country` | N:1 | `gds.country.country_id = gds.variation.country_id` |
| `currency` | N:1 | `gds.currency.currency_id = gds.variation.currency_id` |
| `application` | N:1 | `gds.application.application_id = gds.variation.application_id` |

[View full entity relationship diagram →](../index.md#entity-relationships)

---

!!! tip "Useful Links"
    - :material-swap-horizontal: [Migrating from legacy tables (DW_LSTG_ITEM, etc.)?](../guides/migration-guide.md)
    - :material-magnify: [More query examples](../guides/query-examples.md)