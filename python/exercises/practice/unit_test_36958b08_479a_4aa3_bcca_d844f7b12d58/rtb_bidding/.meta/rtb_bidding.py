def process_bid_request(bid_request, targeting_criteria):
    max_bid = 0.0
    
    for criterion in targeting_criteria:
        # Check user ID match
        user_match = (not criterion['target_user_ids'] or 
                     bid_request['user_id'] in criterion['target_user_ids'])
        
        # Check device match
        device_match = (not criterion['target_devices'] or 
                       bid_request['device'] in criterion['target_devices'])
        
        # Check location match
        location_match = False
        for loc_criterion in criterion['target_locations']:
            country_ok = (loc_criterion['country'] == '*' or 
                         loc_criterion['country'] == bid_request['location']['country'])
            region_ok = (loc_criterion['region'] == '*' or 
                         loc_criterion['region'] == bid_request['location']['region'])
            city_ok = (loc_criterion['city'] == '*' or 
                       loc_criterion['city'] == bid_request['location']['city'])
            
            if country_ok and region_ok and city_ok:
                location_match = True
                break
        
        # Check category match
        category_match = False
        if not criterion['target_ad_categories']:
            category_match = True
        else:
            for category in bid_request['ad_categories']:
                if category in criterion['target_ad_categories']:
                    category_match = True
                    break
        
        # If all conditions match, consider this bid
        if user_match and device_match and location_match and category_match:
            if criterion['bid_price'] > max_bid:
                max_bid = criterion['bid_price']
    
    return {
        'request_id': bid_request['request_id'],
        'bid_price': max_bid
    }