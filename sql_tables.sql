-- Supabase SQL Tables for Resumen Contable

-- Table for historical emitted invoices
CREATE TABLE IF NOT EXISTS emitidos_historico (
    id SERIAL PRIMARY KEY,
    fecha DATE NOT NULL,
    empresa TEXT,
    tipo TEXT,
    nro INTEGER,
    neto_gravado DECIMAL(15,2) DEFAULT 0,
    neto_no_gravado DECIMAL(15,2) DEFAULT 0,
    op_exentas DECIMAL(15,2) DEFAULT 0,
    iva DECIMAL(15,2) DEFAULT 0,
    neto DECIMAL(15,2) DEFAULT 0,
    mes TEXT,
    razon_social TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Table for historical received invoices
CREATE TABLE IF NOT EXISTS recibidos_historico (
    id SERIAL PRIMARY KEY,
    fecha DATE NOT NULL,
    empresa TEXT,
    tipo TEXT,
    nro INTEGER,
    neto_gravado DECIMAL(15,2) DEFAULT 0,
    neto_no_gravado DECIMAL(15,2) DEFAULT 0,
    op_exentas DECIMAL(15,2) DEFAULT 0,
    iva DECIMAL(15,2) DEFAULT 0,
    neto DECIMAL(15,2) DEFAULT 0,
    mes TEXT,
    razon_social TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Table for historical invoices summary
CREATE TABLE IF NOT EXISTS comprobantes_historicos (
    id SERIAL PRIMARY KEY,
    razon_social TEXT NOT NULL,
    mes TEXT NOT NULL,
    variable TEXT NOT NULL,
    monto DECIMAL(15,2) DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(razon_social, mes, variable)
);

-- Table for sales by company and month
CREATE TABLE IF NOT EXISTS ventas_historico_mensual (
    id SERIAL PRIMARY KEY,
    razon_social TEXT NOT NULL,
    mes TEXT NOT NULL,
    neto_gravado DECIMAL(15,2) DEFAULT 0,
    neto_no_gravado DECIMAL(15,2) DEFAULT 0,
    op_exentas DECIMAL(15,2) DEFAULT 0,
    neto DECIMAL(15,2) DEFAULT 0,
    iva DECIMAL(15,2) DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(razon_social, mes)
);

-- Table for purchases by company and month
CREATE TABLE IF NOT EXISTS compras_historico_mensual (
    id SERIAL PRIMARY KEY,
    razon_social TEXT NOT NULL,
    mes TEXT NOT NULL,
    neto_gravado DECIMAL(15,2) DEFAULT 0,
    neto_no_gravado DECIMAL(15,2) DEFAULT 0,
    op_exentas DECIMAL(15,2) DEFAULT 0,
    neto DECIMAL(15,2) DEFAULT 0,
    iva DECIMAL(15,2) DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(razon_social, mes)
);

-- Table for sales by company and client
CREATE TABLE IF NOT EXISTS ventas_historico_cliente (
    id SERIAL PRIMARY KEY,
    razon_social TEXT NOT NULL,
    empresa TEXT NOT NULL,
    mes TEXT NOT NULL,
    neto_gravado DECIMAL(15,2) DEFAULT 0,
    neto_no_gravado DECIMAL(15,2) DEFAULT 0,
    op_exentas DECIMAL(15,2) DEFAULT 0,
    neto DECIMAL(15,2) DEFAULT 0,
    iva DECIMAL(15,2) DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(razon_social, empresa, mes)
);

-- Table for purchases by company and supplier
CREATE TABLE IF NOT EXISTS compras_historico_proveedor (
    id SERIAL PRIMARY KEY,
    razon_social TEXT NOT NULL,
    empresa TEXT NOT NULL,
    mes TEXT NOT NULL,
    neto DECIMAL(15,2) DEFAULT 0,
    iva DECIMAL(15,2) DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(razon_social, empresa, mes)
);

-- Table for monthly accounting summary by company (mes vencido)
CREATE TABLE IF NOT EXISTS resumen_contable_mes_vencido (
    id SERIAL PRIMARY KEY,
    sociedad TEXT NOT NULL,
    vtas_netas DECIMAL(15,2) DEFAULT 0,
    compras_netas DECIMAL(15,2) DEFAULT 0,
    saldo_iva DECIMAL(15,2) DEFAULT 0,
    ii_bb DECIMAL(15,2) DEFAULT 0,
    mes TEXT NOT NULL,
    fecha_generacion DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(sociedad, mes)
);

-- Table for total accounting summary (totals across all companies)
CREATE TABLE IF NOT EXISTS resumen_contable_total (
    id SERIAL PRIMARY KEY,
    vtas_netas DECIMAL(15,2) DEFAULT 0,
    compras_netas DECIMAL(15,2) DEFAULT 0,
    saldo_iva DECIMAL(15,2) DEFAULT 0,
    ii_bb DECIMAL(15,2) DEFAULT 0,
    mes TEXT NOT NULL,
    fecha_generacion DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(mes)
);

-- Indexes for better performance
CREATE INDEX IF NOT EXISTS idx_emitidos_historico_fecha ON emitidos_historico(fecha);
CREATE INDEX IF NOT EXISTS idx_emitidos_historico_razon_social ON emitidos_historico(razon_social);
CREATE INDEX IF NOT EXISTS idx_emitidos_historico_mes ON emitidos_historico(mes);

CREATE INDEX IF NOT EXISTS idx_recibidos_historico_fecha ON recibidos_historico(fecha);
CREATE INDEX IF NOT EXISTS idx_recibidos_historico_razon_social ON recibidos_historico(razon_social);
CREATE INDEX IF NOT EXISTS idx_recibidos_historico_mes ON recibidos_historico(mes);

CREATE INDEX IF NOT EXISTS idx_comprobantes_historicos_razon_social ON comprobantes_historicos(razon_social);
CREATE INDEX IF NOT EXISTS idx_comprobantes_historicos_mes ON comprobantes_historicos(mes);

CREATE INDEX IF NOT EXISTS idx_ventas_historico_mensual_razon_social ON ventas_historico_mensual(razon_social);
CREATE INDEX IF NOT EXISTS idx_ventas_historico_mensual_mes ON ventas_historico_mensual(mes);

CREATE INDEX IF NOT EXISTS idx_compras_historico_mensual_razon_social ON compras_historico_mensual(razon_social);
CREATE INDEX IF NOT EXISTS idx_compras_historico_mensual_mes ON compras_historico_mensual(mes);

CREATE INDEX IF NOT EXISTS idx_ventas_historico_cliente_razon_social ON ventas_historico_cliente(razon_social);
CREATE INDEX IF NOT EXISTS idx_ventas_historico_cliente_mes ON ventas_historico_cliente(mes);

CREATE INDEX IF NOT EXISTS idx_compras_historico_proveedor_razon_social ON compras_historico_proveedor(razon_social);
CREATE INDEX IF NOT EXISTS idx_compras_historico_proveedor_mes ON compras_historico_proveedor(mes);

CREATE INDEX IF NOT EXISTS idx_resumen_contable_mes_vencido_sociedad ON resumen_contable_mes_vencido(sociedad);
CREATE INDEX IF NOT EXISTS idx_resumen_contable_mes_vencido_mes ON resumen_contable_mes_vencido(mes);

CREATE INDEX IF NOT EXISTS idx_resumen_contable_total_mes ON resumen_contable_total(mes);

-- Enable Row Level Security (RLS) for all tables
ALTER TABLE emitidos_historico ENABLE ROW LEVEL SECURITY;
ALTER TABLE recibidos_historico ENABLE ROW LEVEL SECURITY;
ALTER TABLE comprobantes_historicos ENABLE ROW LEVEL SECURITY;
ALTER TABLE ventas_historico_mensual ENABLE ROW LEVEL SECURITY;
ALTER TABLE compras_historico_mensual ENABLE ROW LEVEL SECURITY;
ALTER TABLE ventas_historico_cliente ENABLE ROW LEVEL SECURITY;
ALTER TABLE compras_historico_proveedor ENABLE ROW LEVEL SECURITY;
ALTER TABLE resumen_contable_mes_vencido ENABLE ROW LEVEL SECURITY;
ALTER TABLE resumen_contable_total ENABLE ROW LEVEL SECURITY;

-- Create policies (adjust as needed for your security requirements)
-- Example: Allow all operations for authenticated users
CREATE POLICY "Allow all operations for authenticated users" ON emitidos_historico FOR ALL USING (auth.uid() IS NOT NULL);
CREATE POLICY "Allow all operations for authenticated users" ON recibidos_historico FOR ALL USING (auth.uid() IS NOT NULL);
CREATE POLICY "Allow all operations for authenticated users" ON comprobantes_historicos FOR ALL USING (auth.uid() IS NOT NULL);
CREATE POLICY "Allow all operations for authenticated users" ON ventas_historico_mensual FOR ALL USING (auth.uid() IS NOT NULL);
CREATE POLICY "Allow all operations for authenticated users" ON compras_historico_mensual FOR ALL USING (auth.uid() IS NOT NULL);
CREATE POLICY "Allow all operations for authenticated users" ON ventas_historico_cliente FOR ALL USING (auth.uid() IS NOT NULL);
CREATE POLICY "Allow all operations for authenticated users" ON compras_historico_proveedor FOR ALL USING (auth.uid() IS NOT NULL);
CREATE POLICY "Allow all operations for authenticated users" ON resumen_contable_mes_vencido FOR ALL USING (auth.uid() IS NOT NULL);
CREATE POLICY "Allow all operations for authenticated users" ON resumen_contable_total FOR ALL USING (auth.uid() IS NOT NULL);


