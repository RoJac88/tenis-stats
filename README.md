# Tênis Stats

Os scripts de insert são gerados a partir das planilhas na pasta csv. Para criar o banco de dados e popular os dados utilize o comando: `flask init`

Para facilitar a demonstração do app foram incluídas apenas as partidas de 2019 e 2020 e apenas os jogadores com pelo menos uma partida disputada neste período.

## Rotas

| Rota | Função |
| --- | --- |
| '/' | Página de introdução e números do Banco de Dados |
| '/entrar/' | Página de Login |
| '/tenistas/' | Menu de tenistas |
| '/admin/tenistas/' | Listar Tenistas |
| '/tenistas/<player_id>/' | Detalhes do tenista |
| '/admin/tenistas/alterar/<player_id>/' | Alterar tenista |
| '/admin/tenistas/novo/<player_id>/' | Inserir novo tenista |
| '/admin/tenistas/remover/<player_id>/' | Remover tenista |
| '/torneios/' | Menu de Torneios |
| '/torneios/<t_code>/' | Detalhes e partidas do torneio |
| '/admin/torneios/' | Listar torneios |
| '/admin/torneios/alterar/<t_code>/' | Alterar Torneio |
| '/admin/torneios/novo/<t_code>/' | Inserir novo Torneio |
| '/admin/torneios/remover/<t_code>/' | Remover Torneio |
| '/admin/torneios/limpar/<t_code>/' | Apagar partidas do Torneio |
| '/partidas/' | Listar partidas |
| '/partidas/<player_id>/' | Listar partidas do jogador |
| '/partidas/<player_id>/<m_code>/' | Detalhes da partida |
| '/admin/partidas/' | Listar partidas |
| '/admin/partidas/alterar/<m_code>/' | Alterar Partida |
| '/admin/partidas/novo/<m_code>/' | Inserir nova Partida |
| '/admin/partidas/remover/<m_code>/' | Remover Partida |
| '/rankings/' | --- |
| '/sobre/' | --- |

