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

