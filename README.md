## Qual é o problema?
Eu tenho um hobbie de jogos de tabuleiro e estou em grupos de de jogatinas para me divertir, melhorar minhas capacidades cognitivas, de análise e de planejamento. Como também coleciono esses jogos, fico a procura dos melhores valores, tanto de usados quanto de novos. Faço parte de grupos de vendas e também acompanho sites, mas não tenho tempo para ficar entrando sempre para acompanhar as vendas e os leilões, e essa necessidade me deu uma ideia:
	Seria legal se existisse um dashboard com os registros dos leilões para conseguir analisar se o preço que estou pensando em pagar é justo ou não.
## Qual é a minha necessidade?
Preciso de:
- algo que busque os dados dos leilões do site
- um banco de dados para registrar os dados coletados
- algo para analisar esses dados registrados
## Estratégia de solução
1. Criar um script que vai fazer web scrapping no site de leilões e registrar em um banco de dados.
2. Agendar para ele rodar em horários específicos para buscar os dados sozinho.
3. Ter uma ferramenta de dashboards para que os dados possam ser analisados.
## Etapas
1. Escrever script em Python que faça web scrapping que registre em um banco de dados SQLite e seja lido por um Power BI.
2. Modularizar o código Python, criar uma estrutura de logs e enviar para o Sentry para acompanhamento de erros em produção.
3. Utilizar a AWS para ter uma instancia EC2 para o scrapper em python, uma instancia EC2 para a API de coleta de dados pelo Power BI, e um RDS para o banco de dados MYSQL. Tudo seguindo a estrutura bastion host.
4. Desenvolver o dashboard no Power BI com os dados coletados e armazenados.
## Passos do projeto
1. Desenvolver o MVP
	1. Criar tabelas Leilão e Jogo no SQLite
	2. Fazer a conexão do Python com o SQLite utilizando o ORM SQLModel
	3. Utilizar requests e beautifulsoup para o scrapping do site
2. Modularização
	1. Modularizar com um arquivo de conexão com o banco de dados (models.py)
	2. Modularizar com um arquivo estruturando os logs com a biblioteca logging e conexão com o Sentry (logger.py)
	3. Modularizar com um arquivo com as funções de scrapping (scrapper.py)
	4. Um arquivo principal que roda o processo (run.py)
3. Desenvolver a API
	1. Criar uma API que traga os dados do banco de dados
4. Criar estrutura AWS
	1. Criar a VPC
	2. Criar as Subnets
		1. Duas Subnets privadas para o RDS
		2. Uma Subnet publica para o EC2
	3. Criar o Subnet Group para o RDS 
	4. Criar os Security Group
		1. Security Group do EC2 com a conexão SSH liberada somente para o meu IP
		2. Security Group do RDS com a conexão TCP liberada somente para o Security Group do EC2
	5. Criar Gateway para a conexão a Internet do EC2
	6. Criar Route Tables
	7. Criar EC2
	8. Criar RDS
5. Desenvolver o Power BI
## Resultado
- Dados sendo gerados
## Melhorias
1. Solução para agendamento de processo.
	- Atual: utilizando a biblioteca schedulle para agendamento. 
	- Melhoria: utilizar Airflow no EC2 vai ser uma solução muito mais robusta e com mais controle sobre o processo. 
	- Motivo do não desenvolvimento: não foi utilizado pois a instancia EC2 no freetier não suporta o Airflow.
2. Segurança na API
	- Atual: API rodando no Uvicorn somente
	- Melhoria: Utilizar processos de validação e autenticação com tokens e hashes para segurança da API
	- Motivo do não desenvolvimento: aprendendo