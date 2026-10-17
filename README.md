# Vasco Ingressos Monitor

Monitor experimental da página de ingressos do jogo Vasco x Boca Juniors.

## Estado atual

A primeira versão é **somente detecção**: abre a página com Playwright, coleta texto e elementos do DOM relacionados a setores/categorias e registra mudanças.

Ela ainda NÃO seleciona setor, NÃO escolhe meia-entrada e NÃO adiciona nada ao carrinho. Isso é proposital: precisamos primeiro observar como o mapa interativo representa a disponibilidade real antes de automatizar cliques.

## URL monitorada

`https://vasco.eleventickets.com/#!/apresentacao/5cd8c7b86342e60220038fe6c296712b12724622`

## Executar localmente / Codespaces

```bash
pip install -r requirements.txt
playwright install chromium
python monitor.py
```

Variáveis opcionais:

- `CHECK_INTERVAL=20` — intervalo em segundos.
- `HEADLESS=true` — navegador sem interface; use `false` para depuração.
- `TICKET_URL=...` — substitui a URL padrão.

**Nunca coloque senha, cookie, token de sessão ou dados de pagamento neste repositório.**

## Próxima etapa

Precisamos executar esta versão e examinar o DOM/estado capturado quando o mapa está esgotado. Depois disso, podemos criar seletores específicos para detectar setores realmente clicáveis e, em seguida, testar a seleção de meia-entrada.
