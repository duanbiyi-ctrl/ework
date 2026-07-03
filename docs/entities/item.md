# Item LDM

[← Back to LDM Catalog](../index.md)

## Overview

**LDM Name:** `item`

**Description:** The core listing entity in the Item Domain. Each record represents one eBay listing, containing comprehensive information about title, pricing, category, seller, listing lifecycle, and more.

**Primary Key:** `item_id`

---

## Fields (228)

<!-- BEGIN GENERATED ITEM FIELDS -->

???+ abstract "Item Basics (43)"

    Core attributes that describe what the listed item is, including its identity, title, category, condition, price, quantity, location, and other buyer-facing item facts.


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

    **`slr_prdct_id_txt`** <span class="field-type">STRING</span>

    Stock Keeping Unit. It is an identifier defined by a seller

    **`sku_num`** <span class="field-type">STRING</span>

    Seller&#x27;s custom, application-specific data associated with the item. Data specified here is stored by eBay with the item for seller but it is not used by eBay in any way.

    **`item_site_id`** <span class="field-type">INTEGER</span>

    The eBay site ID where the item was listed. Please see [Site LDM](site.md) for more details.

    Examples:

    - `0` = US
    - `3` = UK
    - `15` = AU
    - `77` = DE

    **`leaf_categ_id`** <span class="field-type">INTEGER</span>

    Primary leaf category ID chosen by the seller for the listing. Use with item_site_id to interpret category hierarchy, SAP category, and higher-level category attributes. Leaf category is the lowest level in eBay's category hierarchy.

    Example:

    - `41931` = Computers & Networking:Software:Education & Reference:Car Repair

    **`leaf_categ_name`** <span class="field-type">STRING</span>

    Name of the leaf category where the item is listed. Leaf category is the lowest level in eBay's category hierarchy.

    Example:

    - Computers & Networking:Software:Education & Reference:Car Repair

    **`leaf_categ_id2`** <span class="field-type">INTEGER</span>

    Secondary leaf category ID chosen by the seller when the listing is posted in two categories; 0 means no secondary category. Please see [Category LDM](category.md) for more details.

    **`meta_categ_id`** <span class="field-type">INTEGER</span>

    Meta category ID. Meta category is the top level in eBay's category hierarchy.

    Example:

    - `58058` = Computers/Tablets & Networking

    **`meta_categ_name`** <span class="field-type">STRING</span>

    Meta category name (top level).

    Example:

    - Computers/Tablets & Networking

    **`categ_lvl2_id`** <span class="field-type">INTEGER</span>

    Level 2 category ID. eBay category hierarchy has up to 7 levels.

    Example:

    - `18793` = Software

    **`categ_lvl2_name`** <span class="field-type">STRING</span>

    Level 2 category name.

    Example:

    - Software

    **`categ_lvl3_id`** <span class="field-type">INTEGER</span>

    Level 3 category ID.

    Example:

    - `3783` = Education, Language, Reference

    **`categ_lvl3_name`** <span class="field-type">STRING</span>

    Level 3 category name.

    Example:

    - Education, Language, Reference

    **`categ_lvl4_id`** <span class="field-type">INTEGER</span>

    Level 4 category ID.

    Example:

    - `3783` = Education, Language, Reference

    **`categ_lvl4_name`** <span class="field-type">STRING</span>

    Level 4 category name.

    Example:

    - Education, Language, Reference

    **`categ_lvl5_id`** <span class="field-type">INTEGER</span>

    Level 5 category ID.

    Example:

    - `3783` = Education, Language, Reference

    **`categ_lvl5_name`** <span class="field-type">STRING</span>

    Level 5 category name.

    Example:

    - Education, Language, Reference

    **`categ_lvl6_id`** <span class="field-type">INTEGER</span>

    Level 6 category ID.

    Example:

    - `3783` = Education, Language, Reference

    **`categ_lvl6_name`** <span class="field-type">STRING</span>

    Level 6 category name.

    Example:

    - Education, Language, Reference

    **`categ_key`** <span class="field-type">LONG</span>

    Surrogate category hierarchy key for the primary leaf category of the listing.

    **`categ_key2`** <span class="field-type">LONG</span>

    Surrogate category hierarchy key for the secondary leaf category of the listing, when a secondary category exists.

    **`categ_move_to_id`** <span class="field-type">INTEGER</span>

    Replacement category ID when the original leaf category has been retired or moved to another category structure. Please see [Category LDM](category.md) for more details.

    **`sap_category_id`** <span class="field-type">INTEGER</span>

    Search Annotation Platform (SAP) category ID assigned to the listing.

    **`lcl_sap_categ_name`** <span class="field-type">STRING</span>

    Local Search Annotation Platform (SAP) category name for the listing category.

    **`glb_sap_categ_name`** <span class="field-type">STRING</span>

    Global Search Annotation Platform (SAP) category name for the listing category.

    **`bsns_vrtcl_name`** <span class="field-type">STRING</span>

    Business Vertical Name (e.g. Electronics, Fashion, Motors).

    **`item_cndtn_id`** <span class="field-type">INTEGER</span>

    Seller-provided item condition code for the listing.

    Values:

    - `1000` = New
    - `1500` = New other
    - `1750` = New with defects
    - `2000` = Certified Refurbished
    - `2500` = Seller refurbished
    - `2750` = Like new
    - `3000` = Used / Pre-owned Good
    - `4000` = Very good
    - `5000` = Good
    - `6000` = Acceptable
    - `7000` = For parts or not working

    **`cndtn_rollup_id`** <span class="field-type">INTEGER</span>

    Higher-level item condition rollup derived from the item condition. Unknown can later resolve when condition attributes are updated.

    Values:

    - `1` = New
    - `2` = Refurbished
    - `3` = Used
    - `4` = Unknown

    **`bin_price_lstg_curncy`** <span class="field-type">DOUBLE</span>

    This is the constant price at which a buyer may purchase the item.

    **`start_price_lstg_curncy`** <span class="field-type">DOUBLE</span>

    Competitive bidding starts at this value. Once at least one bid has been placed, startingBidPrice remains the same but CurrentPrice is incremented to the amount of each succeeding bid.

    **`rsrv_price_list_crncy`** <span class="field-type">DOUBLE</span>

    The lowest price at which the seller is willing to sell the item. (StartPrice must be lower than ReservePrice

    **`orgnl_price_amt`** <span class="field-type">DOUBLE</span>

    It is the price of the item before it was put on SALE.

    **`lstg_curncy_id`** <span class="field-type">INTEGER</span>

    Currency ID used for the listing prices.

    **`qty_avail`** <span class="field-type">INTEGER</span>

    The number of this item that are initially available for sale.

    **`qty_sold`** <span class="field-type">INTEGER</span>

    The number of items sold in the listing.

    **`lot_size`** <span class="field-type">INTEGER</span>

    Indicated the number of items in the lot. A lot is a set of two or more similar items included in a single listing that must be purchased together in a single order line item

    **`item_cntry_id`** <span class="field-type">INTEGER</span>

    Unique identifier of the country where the item is physically located, as declared by the seller. Note: reflects item location, not seller registration country (see slr_cntry_id). Please see [Country LDM](country.md) for more details.

    **`item_loc`** <span class="field-type">STRING</span>

    Seller-provided textual geographical location of the item.

    **`item_zip`** <span class="field-type">STRING</span>

    Postal code of the item location.

???+ abstract "Item Aspects (67)"

    Structured product attributes and eBay-derived catalog/classifier signals, such as brand, MPN, GTIN, aspect values, ePID adoption, and product coverage.


    **`attr_brand_txt`** <span class="field-type">STRING</span>

    Brand value tagged by the seller from seller-input item specifics, using attr_id 3982.

    **`at_cnfdnc`** <span class="field-type">INTEGER</span>

    Auto-tag product reference/ePID adoption method for the item.

    Examples:

    - `1001` = seller adopted
    - `1003` = GTIN match
    - `1004` = Brand + MPN match
    - `5000-5200` = Hydra
    - `9000` = manual adoption
    - `11003` = GTIN match to BEP
    - `11004` = Brand + MPN match to BEP

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

    JSON containing aspect list for the item.

    Examples:

    - sport
    - game
    - language
    - publisher

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

    ID of the browse node this item belongs to?

    **`adptn_visit_ts`** <span class="field-type">TIMESTAMP</span>

    Timestamp when the item last went through the ePID adoption process.

    **`lstg_prod_id`** <span class="field-type">LONG</span>

    Product ID provided by the seller on the listing; use st_prod_ref_id for seller-tagged ePID when available.

    **`adpt_cnfdnc_num`** <span class="field-type">INTEGER</span>

    Confidence number of passive adoption.

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

???+ abstract "Listing Basics (73)"

    Attributes that describe how the listing was created, presented, and managed, including listing status, format, lifecycle dates, seller context, listing tool/channel, media, and operational flags.


    **`application_id`** <span class="field-type">LONG</span>

    Application identifier used by external consumers to identify the application or listing tool associated with listing creation.

    Examples:

    - `219527` = BOLT
    - `290356` = BOLT B2C
    - `384352` = HELIX
    - `2828` = File Exchange
    - `114100` = Auto Relist

    **`bold_title`** <span class="field-type">STRING</span>

    If specified, the seller wants the title for the item&#x27;s listing to be in boldface type. Applicable listing fees apply. Does not affect the item subtitle (Item.SubTitle), if any. Not applicable to eBay Motors.

    **`site_create_date`** <span class="field-type">TIMESTAMP</span>

    Date and time the listing was created. This value is read-only and cannot be updated.

    **`cust_ref_code`** <span class="field-type">STRING</span>

    Universally unique constraint tag. Use UUID to ensure that you only list a particular item once, particularly if you are listing many items at once

    **`auction_end_reason_code`** <span class="field-type">INTEGER</span>

    Reason code for why the listing ended.

    Values:

    - `0` = not ended early/ended naturally
    - `1` = item lost or broken
    - `2` = no longer available
    - `3` = bid/reserve error
    - `4` = listing error
    - `5` = ended early and sold to highest bidder
    - `8` = ended by DBA script
    - `11` = ended due to zero quantity
    - `99` = GTC renewal issue

    **`glry_type_id`** <span class="field-type">INTEGER</span>

    Indicates the type of gallery image for the listing.

    Values:

    - `0` = None
    - `1` = Gallery
    - `2` = Featured
    - `7` = Gallery Plus

    **`gallery_url`** <span class="field-type">STRING</span>

    Single gallery image URL for the listing, usually the first picture URL and used in search or merchandising placements.

    **`item_vrsn_id`** <span class="field-type">LONG</span>

    A generated sequence used to track versions for each revisions makd by seller

    **`last_modfd_dt`** <span class="field-type">DATE</span>

    Date and time the listing was last modified.

    **`photo_count`** <span class="field-type">INTEGER</span>

    Number of photos attached to the listing.

    **`photo_display_type`** <span class="field-type">INTEGER</span>

    Photo display mode code for the listing.

    Values:

    - `0` = Standard Show
    - `1` = Slide Show
    - `2` = Large Photo Show
    - `3` = Picture Pack
    - `4` = EPS Picture Show
    - `5` = Self Hosted Picture Show
    - `6` = SuperSize Picture Show
    - `99999999` = Invalid

    **`picture_url`** <span class="field-type">STRING</span>

    The url of the photos

    **`private_yn`** <span class="field-type">STRING</span>

    If true, designates the listing as private. When you create a private listing, a buyer&#x27;s User ID will not appear in the listing or in the listing&#x27;s bid history

    **`relist_parent_item_id`** <span class="field-type">LONG</span>

    Used by relist, sellSimilar, and bulkRelist to populate the parent item id, relistparentid is only used by DW

    **`relistid`** <span class="field-type">LONG</span>

    Indicates if the listing is ended with a relisted one. If it&#x27;s &gt; 0, it means that the item has been ended and a new relisted one has been created. and the value of this relistId is the same as the value of itemId of the new relisted item

    **`auct_end_dt`** <span class="field-type">DATE</span>

    Date the listing actually ended on eBay.

    **`sale_sched_end_dt`** <span class="field-type">DATE</span>

    Date the listing is scheduled to end.

    **`auct_start_dt`** <span class="field-type">DATE</span>

    Date the listing becomes live.

    **`auct_type_code`** <span class="field-type">INTEGER</span>

    Listing format code.

    Values:

    - `1` = auction
    - `2` = Dutch auction
    - `7` = store fixed price
    - `9` = fixed price
    - `10` = Want It Now
    - `12` = Half.com
    - `13` = classified / lead generation
    - `15` = shopping.com

    **`slr_id`** <span class="field-type">LONG</span>

    Seller&#x27;s Oracle user ID associated with the listing.

    **`sgnfcnt_rvsn_cnt`** <span class="field-type">INTEGER</span>

    An item specific count of the number of times it has been significantly revised.

    **`stor_categ2_id`** <span class="field-type">LONG</span>

    Unique identifier for the secondary custom category in which to list the item. Set this field to a root-level custom category or a custom category that has no child categories (subcategories).

    **`stor_categ_id`** <span class="field-type">LONG</span>

    Unique identifier of a primary custom category in which to list the item. A custom category is a category that the seller created in their eBay Store. eBay Store sellers can create up to three levels of custom categories for their stores, but the API only supports root-level categories.

    **`super_featured`** <span class="field-type">STRING</span>

    Super-featured (top-of-category) listing upgrade. "1" = super featured, "0" = not.

    **`lstg_status_id`** <span class="field-type">INTEGER</span>

    Listing lifecycle status code.

    Values:

    - `0` = Live
    - `1` = Ended
    - `2` = Admin ended
    - `3` = Schedule Deleted
    - `4` = Scheduled

    **`slr_site_id`** <span class="field-type">INTEGER</span>

    The eBay site ID where the seller account is registered; this can differ from the site where the item is listed. Please see [Site LDM](site.md) for more details.

    **`slr_cntry_id`** <span class="field-type">INTEGER</span>

    Country ID where the seller account is registered; this can differ from the physical item location country. Please see [Country LDM](country.md) for more details.

    **`auct_start_exchng_rate`** <span class="field-type">DOUBLE</span>

    The exchange rate on the listing start date

    **`auct_end_exchng_rate`** <span class="field-type">DOUBLE</span>

    The exchange rate on the listing end date

    **`slng_mgr_sbscrbr_flag`** <span class="field-type">INTEGER</span>

    Flag showing the seller was a Selling Manager subscriber for that listing.

    **`slng_mgr_pro_sbscrbr_flag`** <span class="field-type">INTEGER</span>

    Flag showing the seller was a Selling Manager Pro subscriber for that listing

    **`high_bdr_cntry_id`** <span class="field-type">INTEGER</span>

    Country ID of the highest bidder for the listing. Please see [Country LDM](country.md) for more details.

    Values:

    - `-999` = unknown or not applicable

    **`high_bdr_site_id`** <span class="field-type">INTEGER</span>

    Registration site ID of the highest bidder for the listing. Please see [Site LDM](site.md) for more details.

    Values:

    - `-999` = unknown or not applicable

    **`auct_start_date`** <span class="field-type">TIMESTAMP</span>

    The timestamp when the listing becomes live

    **`auct_end_date`** <span class="field-type">TIMESTAMP</span>

    Timestamp the listing actually ended on eBay.

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

    **`device_type_level1`** <span class="field-type">STRING</span>

    High-level device type used to create the listing.

    Values:

    - Mobile
    - PC
    - API
    - Other
    - null

    **`experience_level2`** <span class="field-type">STRING</span>

    More granular listing creation experience.

    Examples:

    - Apps: iPhone
    - Apps: Android
    - Apps: iPad
    - Browser: mWeb
    - Browser: Core site
    - API
    - null

    **`norl_type_cd`** <span class="field-type">INTEGER</span>

    Lister type code.

    Values:

    - `1` = New Lister (seller&#x27;s first listed item; differs from ftl_ind, which excludes first listings that were admin-ended)
    - `2` = Reactivated Lister (seller&#x27;s previous listing was at least 12 months earlier)
    - `3` = Existing Lister

    **`ftl_ind`** <span class="field-type">INTEGER</span>

    First Time Lister indicator. 1 means this listing is identified as the seller first listing, excluding first listings that were admin-ended.

    **`aedl_ind`** <span class="field-type">INTEGER</span>

    Admin Ended Day Lister indicator. 1 means the listing occurred before the seller recorded first listing date, implying a prior admin-ended attempt.

    **`unsccss_lstr_ind`** <span class="field-type">INTEGER</span>

    Unsuccessful Lister indicator. 1 means the seller had listed but had not sold by the listing start date.

    **`mobile_lstg_ind`** <span class="field-type">INTEGER</span>

    Indicates whether the listing was created through a mobile listing flow.

    Values:

    - `1` = mobile listing
    - `0` = not mobile listing

    **`app_party_type_cd`** <span class="field-type">INTEGER</span>

    Application party type code used to identify third-party API listings versus eBay-owned listing flows.

    Values:

    - `0` = third-party application/tool
    - `1` = eBay internal tool

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

???+ abstract "Payment & Shipping (45)"

    Attributes that describe how buyers can pay for and receive the item, including payment methods, shipping costs, package details, tax, shipping programs, and related policies.


    **`package_size`** <span class="field-type">INTEGER</span>

    Shipping package type code that identifies the package format used to ship the item(s).

    Values:

    - `0` = None
    - `1` = Letter
    - `2` = Large Envelope
    - `3` = USPS Flat Rate Envelope
    - `4` = Package / Thick Envelope
    - `5` = Large Package
    - `8` = Roll
    - `18` = USPS Medium Flat Rate Box
    - `31` = FedEx Letter
    - `41` = FedEx Box
    - `45` = Your Packaging
    - `70` = UK Jiffybag
    - `81` = AU Post 500g Satchel
    - `-99999999` = Invalid

    **`payment_cash`** <span class="field-type">STRING</span>

    Indicates whether payment on pickup / cash on pickup is accepted. When used, buyer and seller arrange offline payment and pickup.

    **`payment_cc`** <span class="field-type">STRING</span>

    Indicates whether credit card payment is accepted as a payment method for the listing.

    **`payment_moneyxfer`** <span class="field-type">STRING</span>

    Indicates whether direct money transfer is accepted as a payment method for the listing.

    **`return_policy_yn`** <span class="field-type">STRING</span>

    Indicates whether the listing has a return policy.

    **`shipping_fee`** <span class="field-type">DOUBLE</span>

    Base shipping cost shown for the item using the specified shipping service.

    **`shipping_type`** <span class="field-type">INTEGER</span>

    Shipping cost model selected for the listing.

    Values:

    - `0` = not specified
    - `1` = flat rate
    - `2` = calculated rate
    - `3` = freight
    - `5` = flat domestic/calculated international
    - `6` = calculated domestic/flat international
    - `-999` = null

    **`shipping_xfee`** <span class="field-type">DOUBLE</span>

    Additional shipping cost for each extra unit when the same buyer purchases multiple quantities from the same listing.

    **`tax_new`** <span class="field-type">DOUBLE</span>

    Percent of an item&#x27;s price to be charged as the sales tax for the order.

    **`tax_new_state`** <span class="field-type">STRING</span>

    State or jurisdiction for which the sales tax is being collected.

    **`weight`** <span class="field-type">LONG</span>

    Used to specify the weight of a shipping package.

    **`weight_unit_type`** <span class="field-type">INTEGER</span>

    Unit code for package weight.

    Values:

    - `1` = pounds
    - `2` = kilograms

    **`is_amex_accepted`** <span class="field-type">INTEGER</span>

    Indicates whether American Express is accepted as a payment method for the listing.

    **`is_tax_applied_to_shipping`** <span class="field-type">INTEGER</span>

    Indicates whether sales tax applies to the shipping fee for the listing.

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

    **`is_intl_shipping_promotion`** <span class="field-type">INTEGER</span>

    Indicates whether the item participates in an international shipping promotion.

    **`is_ebay_managed_shipping_eligible`** <span class="field-type">INTEGER</span>

    Indicates whether the item is eligible for eBay managed shipping.

    **`is_gsp_shipping_enabled`** <span class="field-type">INTEGER</span>

    Indicates whether Global Shipping Program (GSP) intermediated shipping is enabled for the listing.

    **`is_immediate_payment_required`** <span class="field-type">INTEGER</span>

    Indicates whether immediate payment is required for the listing.

    **`is_irregular_package`** <span class="field-type">INTEGER</span>

    Indicates whether the shipping package is irregular or odd-shaped.

    **`is_buyer_responsible_for_shipping`** <span class="field-type">INTEGER</span>

    Indicates whether the buyer is responsible for shipping, primarily for Motors listings.

    **`is_loan_check_accepted`** <span class="field-type">INTEGER</span>

    Indicates whether loan check payment is accepted, primarily for Motors listings.

    **`is_merchant_fulfillment_supported`** <span class="field-type">INTEGER</span>

    Indicates whether merchant fulfillment support / default MSKU price-set fulfillment support is enabled for the listing.

    **`is_managed_shipping_opted_in`** <span class="field-type">INTEGER</span>

    Indicates whether the seller/listing opted in to managed shipping.

    **`is_money_order_accepted`** <span class="field-type">INTEGER</span>

    Indicates whether money order or cashier check is accepted as a payment method.

    **`has_free_shipping_pre_promo`** <span class="field-type">INTEGER</span>

    Indicates whether the listing had standard free shipping before a promotional sale.

    **`is_free_shipping_sale`** <span class="field-type">INTEGER</span>

    Indicates whether the item is on a free-shipping sale promotion.

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

    **`is_ebay_plus_supported`** <span class="field-type">INTEGER</span>

    Indicates whether the item supports or requested the eBay Plus program.

    **`is_domestic_shipping_promotion`** <span class="field-type">INTEGER</span>

    Indicates whether the item participates in a domestic shipping promotion.

    **`is_visa_mc_accepted`** <span class="field-type">INTEGER</span>

    Indicates whether Visa or MasterCard is accepted as a payment method for the listing.

    **`eplus_elgbl_ind`** <span class="field-type">INTEGER</span>

    Indicates whether the item is eligible for eBay Plus.

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
