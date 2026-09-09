# flightdeals

App simples que busca passagens aéreas em oferta periodicamente e avisa por Telegram.

## Como funciona

- Usa a **Data API da Travelpayouts** (gratuita) para consultar, para cada destino
  configurado, o preço mais barato encontrado recentemente em cada dia de um mês.
- Filtra pelo seu range de datas e pelo preço-alvo de cada destino, definidos em
  `flightdeals/config.yaml`.
- Quando encontra uma oferta nova (que ainda não foi avisada), manda uma mensagem
  pro seu Telegram.
- Guarda em `seen_deals.json` o que já foi notificado, pra não repetir o mesmo alerta
  a cada execução.

## Setup

1. Instale as dependências:
   ```
   pip install -r requirements.txt
   ```
2. Copie `.env.example` para `.env` e preencha:
   - `TRAVELPAYOUTS_TOKEN`: Profile → API token, em travelpayouts.com
   - `TELEGRAM_BOT_TOKEN`: token dado pelo @BotFather ao criar seu bot
   - `TELEGRAM_CHAT_ID`: seu chat_id no Telegram
3. Copie `flightdeals/config.example.yaml` para `flightdeals/config.yaml` e ajuste
   origem, destinos (cada um com seu preço-alvo) e range de datas.
4. Rode manualmente para testar:
   ```
   python -m flightdeals.main
   ```

## Rodando periodicamente

Já vem configurado pra rodar sozinho via **GitHub Actions**
(`.github/workflows/flight-deals.yml`), sem precisar de nada ligado no seu celular
ou computador. Só falta cadastrar os 3 secrets no repositório (Settings → Secrets
and variables → Actions):

- `TRAVELPAYOUTS_TOKEN`
- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHAT_ID`

O workflow roda automaticamente no horário definido em `.github/workflows/flight-deals.yml`
(padrão: 2x ao dia) e também pode ser disparado manualmente pela aba "Actions" do
repositório no GitHub, clicando em "Run workflow".

## Limitações importantes

- A Data API da Travelpayouts é **cache**, não busca ao vivo — os preços refletem
  buscas recentes de outros usuários, não uma cotação exata no momento. É ótima pra
  "farejar" oferta, mas confirme o preço final no site antes de comprar.
- A filtragem por duração exata da viagem (ex: "só viagens de 7 a 10 dias") não é
  feita pela API diretamente; o app compara apenas a data de ida dentro do range.
