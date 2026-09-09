# flightdeals

App simples que busca passagens aéreas em oferta periodicamente e avisa por Telegram.

## Como funciona

- Usa a **Data API da Travelpayouts** (gratuita) para consultar, para cada destino
  configurado, o preço mais barato encontrado recentemente em cada dia de um mês.
- Filtra pelo seu range de datas e pelo preço-alvo definido em `flightdeals/config.yaml`.
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
   origem, destinos, range de datas e preço-alvo.
4. Rode manualmente para testar:
   ```
   python -m flightdeals.main
   ```

## Rodando periodicamente

Este script é feito pra rodar de tempos em tempos (ex: 1x por dia). A forma mais
simples é um cron job:

```
0 8 * * * cd /caminho/do/projeto && python -m flightdeals.main
```

## Limitações importantes

- A Data API da Travelpayouts é **cache**, não busca ao vivo — os preços refletem
  buscas recentes de outros usuários, não uma cotação exata no momento. É ótima pra
  "farejar" oferta, mas confirme o preço final no site antes de comprar.
- A filtragem por duração exata da viagem (ex: "só viagens de 7 a 10 dias") não é
  feita pela API diretamente; o app compara apenas a data de ida dentro do range.
