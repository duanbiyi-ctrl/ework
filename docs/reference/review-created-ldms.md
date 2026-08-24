# Review: Created LDMs

## ItemKeyspace

1. **ItemRoot**
   - Entity Name: item_root
   - ESS Logical Data Model Link: https://gdsgovtool.muse.qa.ebay.com/logical-data-models/view/1641
   - Review Comments: PK, listing for one time or variation current-state

2. **ItemDescription**
   - Entity Name: item_description
   - ESS Logical Data Model Link: https://gdsgovtool.muse.qa.ebay.com/logical-data-models/view/1634
   - Review Comments: primary key missing, should be ItemDescId, "DESC_102250629096", DESC_<itemID>

3. **ItemPriceAndQuantity**
   - Entity Name: item_price_and_quantity
   - ESS Logical Data Model Link: https://gdsgovtool.muse.qa.ebay.com/logical-data-models/view/1640
   - Review Comments: primary key missing, should be ItemQtyPriceID, "QTYPRICE_110298230558", QTYPRICE_<itemId>; but looks like some fields are diverging from https://pages.github.corp.ebay.com/GDS/gds-item-docs/entities/itemkeyspace-item-qty-price/, sample data has ItemQtyPriceID, availQty, price, qtySold

4. **ItemDetails**
   - Entity Name: item_details
   - ESS Logical Data Model Link: https://gdsgovtool.muse.qa.ebay.com/logical-data-models/view/1635
   - Review Comments: primary key missing, should be itemDetailsID, "ITEMDET_110311177994", ITEMDET_<itemId>; 

5. **ItemCompatibility**
   - Entity Name: item_compatibility
   - ESS Logical Data Model Link: https://gdsgovtool.muse.qa.ebay.com/logical-data-models/view/1633
   - Review Comments: primary key missing, should be ItemCompID, "COMPAT_110340694412", COMPAT_<itemId>; missing compat field in ess, https://pages.github.corp.ebay.com/GDS/gds-item-docs/entities/itemkeyspace-item-compatibility/

6. **ItemBusinessPolicies**
   - Entity Name: item_business_policies
   - ESS Logical Data Model Link: https://gdsgovtool.muse.qa.ebay.com/logical-data-models/view/1632
   - Review Comments: primary key missing, should be plcsId, "BIZPOL_102250629096", BIZPOL_<itemID> also 3 fields are struct fields, probably can view its structure

7. **ItemUUIDMapping**
   - Entity Name: item_uuid_mapping
   - ESS Logical Data Model Link: https://gdsgovtool.muse.qa.ebay.com/logical-data-models/view/1642
   - Review Comments: primary key missing, should be listingId

8. **ItemLock**
   - Entity Name: item_lock
   - ESS Logical Data Model Link: https://gdsgovtool.muse.qa.ebay.com/logical-data-models/view/1639
   - Review Comments: primary key missing, should be pk (although no business meaning???) 

## ItemGroupKeyspace

9. **ItemGroupRoot**
   - Entity Name: item_group_root
   - ESS Logical Data Model Link: https://gdsgovtool.muse.qa.ebay.com/logical-data-models/view/1638
   - Review Comments: PK, 110497936440, so this should be item group id, in data, it shows 1 group can have several itemIds, can join with ItemKeyspace and its docsets

10. **ItemGroupDescription**
    - Entity Name: item_group_description
    - ESS Logical Data Model Link: https://gdsgovtool.muse.qa.ebay.com/logical-data-models/view/1637
    - Review Comments: missing primary key, should be groupDescId, "GROUPDESC_4371476363820", GROUPDESC_<???>, need to check if ??? is itemId or itemGroupId

11. **ItemGroupBusinessPolicies**
    - Entity Name: item_group_business_policies
    - ESS Logical Data Model Link: https://gdsgovtool.muse.qa.ebay.com/logical-data-models/view/1636
    - Review Comments:  missing primary key plcsId, should be  "BIZPOL_110446337682", BIZPOL_<???>

## ListingDraftKeyspace

12. **ListingDraftRoot**
    - Entity Name: listing_draft_root
    - ESS Logical Data Model Link: https://gdsgovtool.muse.qa.ebay.com/logical-data-models/view/1648
    - Review Comments: PK "3830014352023"

13. **ListingDraftItem**
    - Entity Name: listing_draft_item
    - ESS Logical Data Model Link: https://gdsgovtool.muse.qa.ebay.com/logical-data-models/view/1646
    - Review Comments: missing primary key, should be PK (no biz meaning), "ITEM_3805627097300", ITEM_<??>

14. **ListingDraftItemCompatibility**
    - Entity Name: listing_draft_item_compatibility
    - ESS Logical Data Model Link: https://gdsgovtool.muse.qa.ebay.com/logical-data-models/view/1647
    - Review Comments: missing primary key, should be DraftCompID, "3955961447620"

15. **ListingDraftGroup**
    - Entity Name: listing_draft_group
    - ESS Logical Data Model Link: https://gdsgovtool.muse.qa.ebay.com/logical-data-models/view/1643
    - Review Comments: missing primary key, should be PK (no biz meaning), "GROUP_4371476363820"

16. **ListingDraftGroupCompatibility**
    - Entity Name: listing_draft_group_compatibility
    - ESS Logical Data Model Link: https://gdsgovtool.muse.qa.ebay.com/logical-data-models/view/1644
    - Review Comments: missing primary key, should be DraftCompID, "GROUPCOMPAT_5050516344500", GROUPCOMPAT_{???}, for compat field it is structured so maybe need to map out

17. **ListingDraftGroupDescription**
    - Entity Name: listing_draft_group_description
    - ESS Logical Data Model Link: https://gdsgovtool.muse.qa.ebay.com/logical-data-models/view/1645
    - Review Comments: missing primary key, should be PK (no business meaning), "GROUPDESC_4371476363820", GROUPDESC_<??>

18. **UserListingDraftMap**
    - Entity Name: user_listing_draft_map
    - ESS Logical Data Model Link: https://gdsgovtool.muse.qa.ebay.com/logical-data-models/view/1653
    - Review Comments: userid to draftid mapping, a user can have multiple drafts

## ListingRevisionKeyspace

19. **ListingRevisionRoot**
    - Entity Name: listing_revision_root
    - ESS Logical Data Model Link: https://gdsgovtool.muse.qa.ebay.com/logical-data-models/view/1651
    - Review Comments: missing primary key, should be lstgId, "110519829818", is this listingid, difference between listingId and itemId? https://pages.github.corp.ebay.com/GDS/gds-item-docs/entities/listingrevisionkeyspace-root/ is missing field expiredDate

20. **ListingRevision**
    - Entity Name: listing_revision
    - ESS Logical Data Model Link: https://gdsgovtool.muse.qa.ebay.com/logical-data-models/view/1649
    - Review Comments: need to ask PD how this table listing_revision differ from the other table listing_revision_detail

21. **ListingVariationRevisionDetail**
    - Entity Name: listing_revision_detail
    - ESS Logical Data Model Link: https://gdsgovtool.muse.qa.ebay.com/logical-data-models/view/1650
    - Review Comments: seems no primary key ? only a log table for old vs new value change history

## Other

22. ***(TBD)***
    - Entity Name:
    - ESS Logical Data Model Link:
    - Review Comments:
