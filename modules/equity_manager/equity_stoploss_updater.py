from modules.positions_data_fetcher import positions_data_fetcher
from integrations.bybit_api_client import client

def update_equity_stoploss(equity_stoploss_margin):

    print("\n🔁 Checking for positions without trailing stop for equity stop loss update")

    result = positions_data_fetcher.position_data_fetcher()

    # Koska result on lista, ei dict
    all_positions = [p for p in result if isinstance(p, dict) and "symbol" in p]

    if not all_positions:
        print("⚪ No valid positions found for equity stop loss update.")
        return

    print(f"📋 Found {len(all_positions)} positions")

    for pos in all_positions:

        try:
            symbol = pos.get("symbol")
            trailing_stop = float(pos.get("trailingStop", "0") or 0)

            if trailing_stop == 0:
                
                market_price = float(pos.get("markPrice", "0") or 0)
                side = pos.get("side", "Buy")

                # Lasketaan stop loss -hinta
                if side.lower() == "buy":
                    stop_loss_price = market_price * (1 - equity_stoploss_margin / 100)
                elif side.lower() == "sell":
                    stop_loss_price = market_price * (1 + equity_stoploss_margin / 100)
                else:
                    print(f"❓ Unknown side '{side}' for {symbol}, skipping.")
                    continue

                # Selvitetään market_pricen tarkkuus
                market_price_str = pos.get("markPrice", "0")
                decimal_places = len(market_price_str.split('.')[-1]) if '.' in market_price_str else 0
                stop_loss_price = round(stop_loss_price, decimal_places)

                print(f"📉 Calculated stop loss price for {symbol}: {stop_loss_price} (rounded to {decimal_places} decimals)")

                # 🔒 Tarkistetaan ettei nykyinen SL ole parempi
                existing_sl_str = pos.get("stopLoss", "0")
                existing_sl = float(existing_sl_str or 0)

                if existing_sl > 0:
                    if side.lower() == "buy" and existing_sl > stop_loss_price:
                        print(f"❌ Existing SL {existing_sl} for {symbol} is tighter than proposed {stop_loss_price}, skipping update.")
                        continue
                    elif side.lower() == "sell" and existing_sl < stop_loss_price:
                        print(f"❌ Existing SL {existing_sl} for {symbol} is tighter than proposed {stop_loss_price}, skipping update.")
                        continue

                # ✅ SL:n päivitys
                print(f"⚙️  Setting stop loss for {symbol} at {stop_loss_price} ({side})")

                position_idx = 1 if side.lower() == "buy" else 2
            
                try:
                    client.set_trading_stop(
                        category="linear",
                        symbol=symbol,
                        stopLoss=str(stop_loss_price),
                        slTriggerBy="MarkPrice",
                        tpslMode="Full",
                        slOrderType="Market",
                        positionIdx=position_idx
                    )
                    print(f"✅ Stop loss set for {symbol} at {stop_loss_price}")

                except Exception as e:
                    print(f"❌ Failed to set stop loss for {symbol}: {e}")

            else:
                print(f"⏭️  Skipping {symbol}: Trailing stop is active.")

        except Exception as e:
            print(f"❌ Error processing position {pos.get('symbol', '?')}: {e}")

    return
