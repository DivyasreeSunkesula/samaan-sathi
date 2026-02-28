-- Samaan Sathi AI Database Schema (PostgreSQL)

-- Shops table
CREATE TABLE IF NOT EXISTS shops (
    shop_id VARCHAR(50) PRIMARY KEY,
    shop_name VARCHAR(200) NOT NULL,
    owner_name VARCHAR(200) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    email VARCHAR(200),
    address TEXT,
    city VARCHAR(100),
    state VARCHAR(100),
    pincode VARCHAR(10),
    language_preference VARCHAR(10) DEFAULT 'en',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Sales transactions table
CREATE TABLE IF NOT EXISTS sales_transactions (
    transaction_id VARCHAR(50) PRIMARY KEY,
    shop_id VARCHAR(50) NOT NULL REFERENCES shops(shop_id),
    transaction_date TIMESTAMP NOT NULL,
    total_amount DECIMAL(10, 2) NOT NULL,
    payment_method VARCHAR(20),
    customer_id VARCHAR(50),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_shop_date (shop_id, transaction_date)
);

-- Sales items table
CREATE TABLE IF NOT EXISTS sales_items (
    id SERIAL PRIMARY KEY,
    transaction_id VARCHAR(50) NOT NULL REFERENCES sales_transactions(transaction_id),
    item_id VARCHAR(50) NOT NULL,
    item_name VARCHAR(200) NOT NULL,
    quantity DECIMAL(10, 2) NOT NULL,
    unit_price DECIMAL(10, 2) NOT NULL,
    total_price DECIMAL(10, 2) NOT NULL,
    INDEX idx_transaction (transaction_id),
    INDEX idx_item (item_id)
);

-- Forecasts table
CREATE TABLE IF NOT EXISTS forecasts (
    id SERIAL PRIMARY KEY,
    shop_id VARCHAR(50) NOT NULL REFERENCES shops(shop_id),
    item_id VARCHAR(50) NOT NULL,
    forecast_date DATE NOT NULL,
    predicted_quantity DECIMAL(10, 2) NOT NULL,
    lower_bound DECIMAL(10, 2),
    upper_bound DECIMAL(10, 2),
    confidence_score DECIMAL(3, 2),
    model_version VARCHAR(20),
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_shop_item_date (shop_id, item_id, forecast_date)
);

-- Pricing recommendations table
CREATE TABLE IF NOT EXISTS pricing_recommendations (
    id SERIAL PRIMARY KEY,
    shop_id VARCHAR(50) NOT NULL REFERENCES shops(shop_id),
    item_id VARCHAR(50) NOT NULL,
    current_price DECIMAL(10, 2) NOT NULL,
    suggested_price DECIMAL(10, 2) NOT NULL,
    reason TEXT,
    confidence_score DECIMAL(3, 2),
    status VARCHAR(20) DEFAULT 'PENDING',
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    applied_at TIMESTAMP,
    INDEX idx_shop_status (shop_id, status)
);

-- Alerts table
CREATE TABLE IF NOT EXISTS alerts (
    id SERIAL PRIMARY KEY,
    shop_id VARCHAR(50) NOT NULL REFERENCES shops(shop_id),
    alert_type VARCHAR(50) NOT NULL,
    priority VARCHAR(20) NOT NULL,
    title VARCHAR(200) NOT NULL,
    message TEXT NOT NULL,
    action_required TEXT,
    status VARCHAR(20) DEFAULT 'ACTIVE',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    acknowledged_at TIMESTAMP,
    INDEX idx_shop_status (shop_id, status),
    INDEX idx_priority (priority)
);

-- OCR processing logs
CREATE TABLE IF NOT EXISTS ocr_logs (
    id SERIAL PRIMARY KEY,
    shop_id VARCHAR(50) NOT NULL REFERENCES shops(shop_id),
    s3_key VARCHAR(500),
    processing_status VARCHAR(20) NOT NULL,
    extracted_data JSONB,
    confidence_score DECIMAL(3, 2),
    error_message TEXT,
    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_shop_status (shop_id, processing_status)
);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply trigger to shops table
CREATE TRIGGER update_shops_updated_at BEFORE UPDATE ON shops
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_sales_shop_date ON sales_transactions(shop_id, transaction_date DESC);
CREATE INDEX IF NOT EXISTS idx_forecasts_shop_item ON forecasts(shop_id, item_id, forecast_date DESC);
CREATE INDEX IF NOT EXISTS idx_alerts_active ON alerts(shop_id, status) WHERE status = 'ACTIVE';

-- Insert sample shop for testing
INSERT INTO shops (shop_id, shop_name, owner_name, phone, email, city, state)
VALUES ('default-shop', 'Sample Kirana Store', 'Test Owner', '+919876543210', 'test@example.com', 'Mumbai', 'Maharashtra')
ON CONFLICT (shop_id) DO NOTHING;
