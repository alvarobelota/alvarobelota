# flightdeals

App simples que busca passagens aéreas em oferta periodicamente e avisa por Telegram.

## Como funciona

- Usa a **Google Flights API da SerpApi** — busca real (mesmo motor do Google Flights,
  calcula conexões de verdade, ex: Manaus→Panamá→Orlando).
- Testa um conjunto de janelas de data (ida + volta) definidas em
  `flightdeals/config.yaml`, já que o plano grátis da SerpApi tem cota de 100
  buscas/mês — não dá pra escanear cada dia do período individualmente.
- Quando encontra uma oferta nova (preço dentro do teto, ainda não avisada), manda
  uma mensagem pro seu Telegram.
- Guarda em `seen_deals.json` o que já foi notificado, pra não repetir o mesmo alerta.

## Setup

1. Instale as dependências:
   ```
   pip install -r requirements.txt
   ```
2. Copie `.env.example` para `.env` e preencha:
   - `SERPAPI_KEY`: sua chave em serpapi.com (conta grátis, sem cartão)
   - `TELEGRAM_BOT_TOKEN`: token dado pelo @BotFather ao criar seu bot
   - `TELEGRAM_CHAT_ID`: seu chat_id no Telegram (mande /start pro bot primeiro)
3. Copie `flightdeals/config.example.yaml` para `flightdeals/config.yaml` e ajuste
   origem, destino, janelas de data e preço-alvo.
4. Rode manualmente para testar:
   ```
   python -m flightdeals.main
   ```

## Rodando periodicamente

Já vem configurado pra rodar sozinho via **GitHub Actions**
(`.github/workflows/flight-deals.yml`), sem precisar de nada ligado no seu celular
ou computador. Secrets necessários no repositório (Settings → Secrets and variables
→ Actions):

- `SERPAPI_KEY`
- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHAT_ID`

O workflow roda automaticamente no horário definido em `.github/workflows/flight-deals.yml`
(padrão: 1x por semana, domingo) e também pode ser disparado manualmente pela aba
"Actions" do repositório no GitHub, clicando em "Run workflow".

## Limitações importantes

- O plano grátis da SerpApi dá **100 buscas/mês**. Cada janela de data em
  `config.yaml` = 1 busca por execução do workflow. Com 8 janelas e execução
  semanal, dá ~32 buscas/mês — dentro da cota, mas sem escanear todo dia do
  período. Se quiser mais cobertura de datas, precisa reduzir a frequência ou
  o número de janelas (ou assinar um plano pago da SerpApi).
- Os preços são os que o Google Flights mostra no momento da busca — não são
  garantidos até a compra.
