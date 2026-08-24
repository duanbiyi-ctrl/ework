# Review: Created LDMs

## ItemKeyspace

1. **ItemRoot**
   - Entity Name:
   - ESS Logical Data Model Link:
   - Review Comments:

2. **ItemDescription**
   - Entity Name: item_description
   - ESS Logical Data Model Link: https://gdsgovtool.muse.qa.ebay.com/logical-data-models/view/1634
   - Review Comments: primary key missing, should be ItemDescId, "DESC_102250629096", DESC_<itemID>

3. **ItemPriceAndQuantity**
   - Entity Name: item_price_and_quantity
   - ESS Logical Data Model Link: https://gdsgovtool.muse.qa.ebay.com/logical-data-models/view/1640
   - Review Comments: primary key missing, should be ItemQtyPriceID, "QTYPRICE_110298230558", QTYPRICE_<itemId>; but looks like some fields are diverging from https://pages.github.corp.ebay.com/GDS/gds-item-docs/entities/itemkeyspace-item-qty-price/, sample data has ItemQtyPriceID, availQty, price, qtySold

4. **ItemDetails**
   - Entity Name:
   - ESS Logical Data Model Link:
   - Review Comments:

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
   - Entity Name:
   - ESS Logical Data Model Link:
   - Review Comments:

## ItemGroupKeyspace

9. **ItemGroupRoot**
   - Entity Name:
   - ESS Logical Data Model Link:
   - Review Comments:

10. **ItemGroupDescription**
    - Entity Name: item_group_description
    - ESS Logical Data Model Link: https://gdsgovtool.muse.qa.ebay.com/logical-data-models/view/1637
    - Review Comments: missing primary key, should be groupDescId, "GROUPDESC_4371476363820", GROUPDESC_<???>, need to check if ??? is itemId or itemGroupId

11. **ItemGroupBusinessPolicies**
    - Entity Name: item_group_business_policies
    - ESS Logical Data Model Link: https://gdsgovtool.muse.qa.ebay.com/logical-data-models/view/1636
    - Review Comments:  missing primary key, should be "BIZPOL_110446337682", BIZPOL_<???>

## ListingDraftKeyspace

12. **ListingDraftRoot**
    - Entity Name:
    - ESS Logical Data Model Link:
    - Review Comments:

13. **ListingDraftItem**
    - Entity Name:
    - ESS Logical Data Model Link:
    - Review Comments:

14. **ListingDraftItemCompatibility**
    - Entity Name:
    - ESS Logical Data Model Link:
    - Review Comments:

15. **ListingDraftGroup**
    - Entity Name:
    - ESS Logical Data Model Link:
    - Review Comments:

16. **ListingDraftGroupCompatibility**
    - Entity Name:
    - ESS Logical Data Model Link:
    - Review Comments:

17. **ListingDraftGroupDescription**
    - Entity Name:
    - ESS Logical Data Model Link:
    - Review Comments:

18. **UserListingDraftMap**
    - Entity Name:
    - ESS Logical Data Model Link:
    - Review Comments:

## ListingRevisionKeyspace

19. **ListingRevisionRoot**
    - Entity Name:
    - ESS Logical Data Model Link:
    - Review Comments:

20. **ListingRevision**
    - Entity Name:
    - ESS Logical Data Model Link:
    - Review Comments:

21. **ListingVariationRevisionDetail**
    - Entity Name:
    - ESS Logical Data Model Link:
    - Review Comments:

## Other

22. ***(TBD)***
    - Entity Name:
    - ESS Logical Data Model Link:
    - Review Comments:
