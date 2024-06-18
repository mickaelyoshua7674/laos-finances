DROP TABLE IF EXISTS fato_income;
DROP TABLE IF EXISTS fato_expense;
DROP TABLE IF EXISTS "dim_expenseSubCategory";
DROP TABLE IF EXISTS "dim_expenseCategory";
DROP TABLE IF EXISTS "dim_incomeCategory";
DROP TABLE IF EXISTS "dim_frequencyType";

-----------------------------------------------------------------------------------------------------------------------------------------
-- DIM Frequency Type
CREATE TABLE "dim_frequencyType" (
	"idFrequencyType" INT GENERATED ALWAYS AS IDENTITY,
	description VARCHAR(50) NOT NULL,
	CONSTRAINT "pk_frequencyType" PRIMARY KEY("idFrequencyType")
);
INSERT INTO "dim_frequencyType" (description) VALUES
	('diário'), ('mensal'), ('anual'), ('aleatório');

-----------------------------------------------------------------------------------------------------------------------------------------
-- DIM Expense Category
CREATE TABLE "dim_expenseCategory" (
	"idExpenseCategory" INT GENERATED ALWAYS AS IDENTITY,
	description VARCHAR(50) NOT NULL,
	CONSTRAINT "pk_expenseCategory" PRIMARY KEY("idExpenseCategory")
);
INSERT INTO "dim_expenseCategory" (description) VALUES 
	('habitação'), --1
	('transporte'), --2
	('saúde'), --3
	('educação'), --4
	('alimentação'), --5
	('vestuário'), --6
	('cuidado pessoal'), --7
	('lazer'), --8
	('dívida'), --9
	('doação'), --10
	('investimento'), --11
	('poupança'), --12
	('outros'); --13

-----------------------------------------------------------------------------------------------------------------------------------------
-- DIM Expense SubCategory
CREATE TABLE "dim_expenseSubCategory" (
	"idExpenseSubCategory" INT GENERATED ALWAYS AS IDENTITY,
	"idExpenseCategory" INT NOT NULL,
	description VARCHAR(50) NOT NULL,
	CONSTRAINT "pk_expenseSubCategory" PRIMARY KEY ("idExpenseSubCategory"),
	CONSTRAINT "fk_expenseCategory" FOREIGN KEY ("idExpenseCategory") REFERENCES "dim_expenseCategory"("idExpenseCategory")
);
INSERT INTO "dim_expenseSubCategory" ("idExpenseCategory", description) VALUES
	-- Habitação
	(1,'aluguel'), (1,'condomínio'), (1,'prestação'), (1,'diarista'), (1,'secretária'),
	(1,'luz'), (1,'água'), (1,'gás'), (1,'internet'), (1,'iptu'), (1,'utensílios'),
	(1,'seguro'), (1,'consertos'), (1,'tv'), (1,'celular'),

	-- Transporte
	(2,'prestação carro'), (2,'seguro'), (2,'multas'), (2,'licenciamento'), (2,'combustível'), 
	(2,'estacionamento'), (2,'ipva'), (2,'pneus'), (2,'manutação'), (2,'transporte coletivo'), 
	(2,'uber'), (2,'99'), (2,'óleo'),

	-- Saúde
	(3,'plano de saúde'), (3,'seguro'), (3,'medicamentos'), (3,'médico'), (3,'dentista'), (3,'academia'),

	-- Educação
	(4,'escola'), (4,'faculdade'), (4,'curso'), (4,'transporte escolar'), (4,'material escolar'), 
	(4,'fardamento'), (4,'passeios'),

	-- Alimentação
	(5,'supermercado'), (5,'padaria'), (5,'feira'), (5,'açougue'), (5,'fora de casa'), 

	-- Vestuário
	(6,'roupa'), (6,'calçado'), (6,'acessório'),

	-- Cuidado Pessoal
	(7,'higiene pessoal'), (7,'cabelereiro'), (7,'depilação'), (7,'esteticista'), (7,'manicure'), 

	-- Lazer
	(8,'cinema'), (8,'teatro'), (8,'passeio'), (8,'jantar'), (8,'viagem'), (8,'bar'),

	-- Dívida
	(9,'compra parcelada boleto'), (9,'compra parcelada cartão'), (9,'cheque'),
	(9,'empréstimo'), (9,'financiamento'),

	-- Doação
	(10,'dízimo'), (10,'oferta'), (10,'ongs'), (10,'família'), (10,'cesta básica'), 

	-- Investimento
	(11,'ações'), (11,'fundos'), (11,'previdência'), (11,'compra ativos'), (11,'criptomoeda'), 

	-- Poupança
	(12,'ações'), (12,'fundos'), (12,'previdência'), (12,'compra ativos'), (12,'criptomoeda'),

	-- Outros
	(13,'taxa conta corrente'), (13,'taxa cheque especial'), (13,'anuidade cartão de crédito'),
	(13,'animal doméstico'), (13,'plano funerário'), (13,'presente'), (13,'mesada');

-----------------------------------------------------------------------------------------------------------------------------------------
-- FATO Expenses
CREATE TABLE fato_expense (
	"idFrequencyType" INT NOT NULL,
	"idExpenseSubCategory" INT NOT NULL,
	value FLOAT NOT NULL,
	"expenseDate" DATE,
	CONSTRAINT "fk_expense_frequencyType" FOREIGN KEY ("idFrequencyType") REFERENCES "dim_frequencyType"("idFrequencyType"),
	CONSTRAINT "fk_expenseSubCategory" FOREIGN KEY ("idExpenseSubCategory") REFERENCES "dim_expenseSubCategory"("idExpenseSubCategory")
);

-----------------------------------------------------------------------------------------------------------------------------------------
-- DIM Income Category
CREATE TABLE "dim_incomeCategory" (
	"idIncomeCategory" INT GENERATED ALWAYS AS IDENTITY,
	description VARCHAR(50) NOT NULL,
	CONSTRAINT "pk_IncomeCategory" PRIMARY KEY ("idIncomeCategory")
);
INSERT INTO "dim_incomeCategory" (description) VALUES
	('pró labore'), ('férias'), ('aluguel'), ('salário'), ('seguro'), ('13 salário'), ('bônus'),
	('herança'), ('freelancer');

-----------------------------------------------------------------------------------------------------------------------------------------
-- FATO Income
CREATE TABLE fato_income (
	"idFrequencyType" INT NOT NULL,
	"idIncomeCategory" INT NOT NULL,
	value FLOAT NOT NULL,
	"incomeDate" DATE,
	CONSTRAINT "fk_income_frequencyType" FOREIGN KEY ("idFrequencyType") REFERENCES "dim_frequencyType"("idFrequencyType"),
	CONSTRAINT "fk_incomeCategory" FOREIGN KEY ("idIncomeCategory") REFERENCES "dim_incomeCategory"("idIncomeCategory")
);