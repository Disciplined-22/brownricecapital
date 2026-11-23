-- /app/db/init.sql
-- Runs automatically when PostgreSQL initializes an empty data volume.

CREATE TABLE IF NOT EXISTS trades (
    venue           TEXT        NOT NULL,
    trade_id        TEXT        NOT NULL,
    symbol          TEXT        NOT NULL,
    side            TEXT        NOT NULL CHECK (side IN ('BUY', 'SELL')),
    quantity        NUMERIC(30,12) NOT NULL CHECK (quantity > 0),
    price           NUMERIC(30,12) NOT NULL CHECK (price > 0),
    trade_timestamp TIMESTAMPTZ NOT NULL,

    UNIQUE (venue, trade_id)
);


CREATE TABLE IF NOT EXISTS positions_table (
    symbol       TEXT PRIMARY KEY,
    net_quantity NUMERIC(30,12) CHECK (net_quantity >= 0),
    average_cost NUMERIC(30,12) CHECK (average_cost >= 0),
    realized_pnl NUMERIC(30,12)
);


CREATE TABLE IF NOT EXISTS prices_table (
    symbol      TEXT PRIMARY KEY,
    latest_price NUMERIC(30,12) CHECK (latest_price > 0),
    updated_at  TIMESTAMPTZ DEFAULT NOW()
);
