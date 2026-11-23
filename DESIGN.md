# DESIGN.md

**Cost-basis method: Average cost**

## Trade Ingestion Flow (ASCII Diagram)

Stream of trades from trades.json:

```
trades.json
   |
   v
+-------------------+
|  RECEIVE TRADE    |  <-- trade fields: venue, trade_id, symbol, side,
+-------------------+      quantity, price, timestamp
   |
   v
+-------------------+
|  VALIDATE INPUT   |
+-------------------+
   |
   v
+-------------------+
| START TRANSACTION |
|      (BEGIN)      |
+-------------------+
   |
   v
+---------------------------------------------+
|          INSERT TRADE                       |
|   ON CONFLICT (venue, trade_id) DO NOTHING  |  <-- idempotency
+---------------------------------------------+
   |
   v
+-------------------+
| WAS TRADE         |
| INSERTED?         |
+-------+-----------+
        |
   +----+----+
   |         |
   NO        YES
   |         |
   v         v
COMMIT    INITIALIZE POSITION
RETURN    IF NOT EXISTS
DUPLICATE   (create position record if absent)
   |         |
   v         v
      LOCK POSITION ROW
      SELECT ... FOR UPDATE
            |
            v
      CHECK OVERSELL
            |
      +-----+-----+
      |           |
     YES          NO
      |           |
      v           v
   ROLLBACK   CALCULATE UPDATES
RETURN       |
HTTP 400     +------------------+
             |                  |
             v                  v
       BUY CALCULATIONS   SELL CALCULATIONS
       - New quantity     - New quantity
       - New avg cost     - Average cost unchanged
                            - Realized PnL
             |                  |
             +--------+---------+
                      |
                      v
             UPDATE positions_table
                      |
                      v
                   COMMIT
                      |
                      v
              RETURN SUCCESS
```

## Key Guarantees

| Feature | Implementation |
|---------|---------------|
| Idempotency | `ON CONFLICT (venue, trade_id) DO NOTHING` � re-ingesting the same trade is safe |
| Oversell check | Rejects SELL trades exceeding net_quantity |
| Transaction safety | Each trade wrapped in its own DB transaction |
| Average cost | Position average cost updated using weighted-average formula |


We have used database constraints with Python logics to ensure proper design implementation of the assessment.