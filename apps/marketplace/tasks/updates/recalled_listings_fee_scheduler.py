# This script runs a schedule to:
# 1. Check if there are any listings that have been recalled from the RecallListings table.
# 2. If there are any recalled listings, it checks whether a fee needs to be charged to the seller.
# 3. If a fee needs to be charged, it applies the flat fee and charges it to the seller.
# 4. It then updates the RecallListings table to reflect that the fee has been charged.
    # info to update in the RecallListings table so to know how many times and when its been charged:
    # - fee_charged_count: number of times the fee has been charged
    # - fee_charged_at: timestamp of when the fee was last charged
    # - fee_charged_amount: amount of the fee charged
# 5. It then updated the seller via email that the fee has been charged.