def sort_orders_by_stoploss_priority(orders_df, direction):
    if direction == 'long':
        return orders_df.sort_values(by='order_stop_loss', ascending=False)
    else:
        return orders_df.sort_values(by='order_stop_loss', ascending=True)
