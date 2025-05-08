def get_rule(price, item_price, item_quantity, distribute,cfg):

    if distribute == 1:
        return price * cfg["distribute_1"]["price_ratio"] >= item_price and \
               price - item_price >= cfg["distribute_1"]["min_profit"]
    elif distribute == 2:
        return price * cfg["distribute_2"]["price_ratio"] >= item_price and \
            (price - item_price) * item_quantity >= cfg["distribute_2"]["min_profit"]
    elif distribute == 3:
        if item_price <= 5000:
            key = "≤5000"
        elif item_price < 20000:
            key = "5000~20000"
        elif item_price < 50000:
            key = "20000~50000"
        else:
            key = "≥50000"

        rule = cfg["distribute_3"][key]

        return price * rule["price_ratio"] >= item_price and (price - item_price) * item_quantity >= rule["min_profit"]
    return False
