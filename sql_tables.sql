-- Supabase SQL Tables for Resumen Contable

-- Table for historical emitted invoices
CREATE TABLE IF NOT EXISTS emitidos_historico (
    id SERIAL PRIMARY KEY,
    "Fecha" TEXT,
    "Empresa" TEXT,
    "Tipo" TEXT,
    "Número Desde" INTEGER,
    "Neto Gravado" DECIMAL(15,2) DEFAULT 0,
    "Neto No Gravado" DECIMAL(15,2) DEFAULT 0,
    "Op. Exentas" DECIMAL(15,2) DEFAULT 0,
    "IVA" DECIMAL(15,2) DEFAULT 0,
    "Neto" DECIMAL(15,2) DEFAULT 0,
    "Imp. Total" DECIMAL(15,2) DEFAULT 0,
    "Mes" TEXT,
    "Razon Social" TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Table for historical received invoices
CREATE TABLE IF NOT EXISTS recibidos_historico (
    id SERIAL PRIMARY KEY,
    "Fecha" TEXT,
    "Empresa" TEXT,
    "Tipo" TEXT,
    "Número Desde" INTEGER,
    "Neto Gravado" DECIMAL(15,2) DEFAULT 0,
    "Neto No Gravado" DECIMAL(15,2) DEFAULT 0,
    "Op. Exentas" DECIMAL(15,2) DEFAULT 0,
    "IVA" DECIMAL(15,2) DEFAULT 0,
    "Neto" DECIMAL(15,2) DEFAULT 0,
    "Imp. Total" DECIMAL(15,2) DEFAULT 0,
    "Mes" TEXT,
    "Razon Social" TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS emitidos_mes_vencido (
    id SERIAL PRIMARY KEY,
    "Fecha" TEXT,
    "Empresa" TEXT,
    "Tipo" TEXT,
    "Número Desde" INTEGER,
    "Neto Gravado" DECIMAL(15,2) DEFAULT 0,
    "Neto No Gravado" DECIMAL(15,2) DEFAULT 0,
    "Op. Exentas" DECIMAL(15,2) DEFAULT 0,
    "IVA" DECIMAL(15,2) DEFAULT 0,
    "Neto" DECIMAL(15,2) DEFAULT 0,
    "Imp. Total" DECIMAL(15,2) DEFAULT 0,
    "Mes" TEXT,
    "Razon Social" TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Table for historical received invoices
CREATE TABLE IF NOT EXISTS recibidos_mes_vencido (
    id SERIAL PRIMARY KEY,
    "Fecha" TEXT,
    "Empresa" TEXT,
    "Tipo" TEXT,
    "Número Desde" INTEGER,
    "Neto Gravado" DECIMAL(15,2) DEFAULT 0,
    "Neto No Gravado" DECIMAL(15,2) DEFAULT 0,
    "Op. Exentas" DECIMAL(15,2) DEFAULT 0,
    "IVA" DECIMAL(15,2) DEFAULT 0,
    "Neto" DECIMAL(15,2) DEFAULT 0,
    "Imp. Total" DECIMAL(15,2) DEFAULT 0,
    "Mes" TEXT,
    "Razon Social" TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
-- Table for historical invoices summary
CREATE TABLE IF NOT EXISTS comprobantes_historicos (
    id SERIAL PRIMARY KEY,
    "Razon Social" TEXT NOT NULL,
    "Mes" TEXT NOT NULL,
    "Variable" TEXT NOT NULL,
    "Monto" DECIMAL(15,2) DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE("Razon Social", "Mes", "Variable")
);

-- Table for sales by company and month
CREATE TABLE IF NOT EXISTS ventas_historico_mensual (
    id SERIAL PRIMARY KEY,
    "Razon Social" TEXT NOT NULL,
    "Mes" TEXT NOT NULL,
    "Neto Gravado" DECIMAL(15,2) DEFAULT 0,
    "Neto No Gravado" DECIMAL(15,2) DEFAULT 0,
    "Op. Exentas" DECIMAL(15,2) DEFAULT 0,
    "Neto" DECIMAL(15,2) DEFAULT 0,
    "IVA" DECIMAL(15,2) DEFAULT 0,
    "Imp. Total" DECIMAL(15,2) DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE("Razon Social", "Mes")
);

-- Table for purchases by company and month
CREATE TABLE IF NOT EXISTS compras_historico_mensual (
    id SERIAL PRIMARY KEY,
    "Razon Social" TEXT NOT NULL,
    "Mes" TEXT NOT NULL,
    "Neto Gravado" DECIMAL(15,2) DEFAULT 0,
    "Neto No Gravado" DECIMAL(15,2) DEFAULT 0,
    "Op. Exentas" DECIMAL(15,2) DEFAULT 0,
    "Neto" DECIMAL(15,2) DEFAULT 0,
    "IVA" DECIMAL(15,2) DEFAULT 0,
    "Imp. Total" DECIMAL(15,2) DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE("Razon Social", "Mes")
);

-- Table for sales by company and client
CREATE TABLE IF NOT EXISTS ventas_historico_cliente (
    id SERIAL PRIMARY KEY,
    "Razon Social" TEXT NOT NULL,
    "Empresa" TEXT NOT NULL,
    "Mes" TEXT NOT NULL,
    "Neto Gravado" DECIMAL(15,2) DEFAULT 0,
    "Neto No Gravado" DECIMAL(15,2) DEFAULT 0,
    "Op. Exentas" DECIMAL(15,2) DEFAULT 0,
    "Neto" DECIMAL(15,2) DEFAULT 0,
    "IVA" DECIMAL(15,2) DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE("Razon Social", "Empresa", "Mes")
);

-- Table for purchases by company and supplier
CREATE TABLE IF NOT EXISTS compras_historico_proveedor (
    id SERIAL PRIMARY KEY,
    "Razon Social" TEXT NOT NULL,
    "Empresa" TEXT NOT NULL,
    "Mes" TEXT NOT NULL,
    "Neto Gravado" DECIMAL(15,2) DEFAULT 0,
    "Neto No Gravado" DECIMAL(15,2) DEFAULT 0,
    "Op. Exentas" DECIMAL(15,2) DEFAULT 0,
    "Neto" DECIMAL(15,2) DEFAULT 0,
    "IVA" DECIMAL(15,2) DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE("Razon Social", "Empresa", "Mes")
);

-- Table for monthly accounting summary by company (mes vencido)
CREATE TABLE IF NOT EXISTS resumen_contable_mes_vencido (
    id SERIAL PRIMARY KEY,
    "Razon Social" TEXT NOT NULL,
    "Vtas. Netas" DECIMAL(15,2) DEFAULT 0,
    "Compras Netas" DECIMAL(15,2) DEFAULT 0,
    "Saldo IVA" DECIMAL(15,2) DEFAULT 0,
    "II BB" DECIMAL(15,2) DEFAULT 0,
    mes TEXT NOT NULL,
    fecha_generacion DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE("Razon Social", mes)
);

-- Table for total accounting summary (totals across all companies)
CREATE TABLE IF NOT EXISTS resumen_contable_total (
    id SERIAL PRIMARY KEY,
    "Vtas. Netas" DECIMAL(15,2) DEFAULT 0,
    "Compras Netas" DECIMAL(15,2) DEFAULT 0,
    "Saldo IVA" DECIMAL(15,2) DEFAULT 0,
    "II.BB." DECIMAL(15,2) DEFAULT 0,
    mes TEXT NOT NULL,
    fecha_generacion DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(mes)
);


-- Table for emitted invoices by company
CREATE TABLE IF NOT EXISTS emitidos_por_empresa (
    id SERIAL PRIMARY KEY,
    "Razon Social" TEXT NOT NULL,
    "Empresa" TEXT NOT NULL,
    "Neto Gravado" DECIMAL(15,2) DEFAULT 0,
    "Neto No Gravado" DECIMAL(15,2) DEFAULT 0,
    "Op. Exentas" DECIMAL(15,2) DEFAULT 0,
    "Neto" DECIMAL(15,2) DEFAULT 0,
    "IVA" DECIMAL(15,2) DEFAULT 0,
    "Imp. Total" DECIMAL(15,2) DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE("Razon Social", "Empresa")
);

-- Table for received invoices by company
CREATE TABLE IF NOT EXISTS recibidos_por_empresa (
    id SERIAL PRIMARY KEY,
    "Razon Social" TEXT NOT NULL,
    "Empresa" TEXT NOT NULL,
    "Neto Gravado" DECIMAL(15,2) DEFAULT 0,
    "Neto No Gravado" DECIMAL(15,2) DEFAULT 0,
    "Op. Exentas" DECIMAL(15,2) DEFAULT 0,
    "Neto" DECIMAL(15,2) DEFAULT 0,
    "IVA" DECIMAL(15,2) DEFAULT 0,
    "Imp. Total" DECIMAL(15,2) DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE("Razon Social", "Empresa")
);



-- Table for emitted invoices by company
CREATE TABLE IF NOT EXISTS emitidos_por_empresa_mes_vencido (
    id SERIAL PRIMARY KEY,
    "Razon Social" TEXT NOT NULL,
    "Empresa" TEXT NOT NULL,
    "Neto Gravado" DECIMAL(15,2) DEFAULT 0,
    "Neto No Gravado" DECIMAL(15,2) DEFAULT 0,
    "Op. Exentas" DECIMAL(15,2) DEFAULT 0,
    "Neto" DECIMAL(15,2) DEFAULT 0,
    "IVA" DECIMAL(15,2) DEFAULT 0,
    "Imp. Total" DECIMAL(15,2) DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE("Razon Social", "Empresa")
);

-- Table for received invoices by company
CREATE TABLE IF NOT EXISTS recibidos_por_empresa_mes_vencido (
    id SERIAL PRIMARY KEY,
    "Razon Social" TEXT NOT NULL,
    "Empresa" TEXT NOT NULL,
    "Neto Gravado" DECIMAL(15,2) DEFAULT 0,
    "Neto No Gravado" DECIMAL(15,2) DEFAULT 0,
    "Op. Exentas" DECIMAL(15,2) DEFAULT 0,
    "Neto" DECIMAL(15,2) DEFAULT 0,
    "IVA" DECIMAL(15,2) DEFAULT 0,
    "Imp. Total" DECIMAL(15,2) DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE("Razon Social", "Empresa")
);

DROP TABLE IF EXISTS resumen_contable_total;
DROP TABLE IF EXISTS resumen_contable_mes_vencido;
DROP TABLE IF EXISTS compras_historico_proveedor;
DROP TABLE IF EXISTS ventas_historico_cliente;
DROP TABLE IF EXISTS compras_historico_mensual;
DROP TABLE IF EXISTS ventas_historico_mensual;
DROP TABLE IF EXISTS comprobantes_historicos;
DROP TABLE IF EXISTS recibidos_historico;
DROP TABLE IF EXISTS emitidos_historico;
DROP TABLE IF EXISTS emitidos_por_empresa;
DROP TABLE IF EXISTS recibidos_por_empresa;