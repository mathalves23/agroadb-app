# Política de segurança

## Reportar vulnerabilidades

Se descobrir uma vulnerabilidade de segurança, **não** abra um issue público com detalhes exploráveis. Contacte os mantenedores do repositório por um canal privado (por exemplo, *Security Advisories* do GitHub, se estiver ativado no projeto).

Inclua, sempre que possível:

- descrição do impacto;
- passos mínimos para reproduzir;
- versão/commit do código afectado.

## Boas práticas neste repositório

- Nunca commite ficheiros `.env`, chaves API, passwords ou dumps de bases de dados reais.
- Use `.env.example` apenas com **placeholders**; segredos ficam no ambiente ou no gestor de secrets da sua infraestrutura.
- Em produção: `SECRET_KEY` forte e aleatório, HTTPS (`FORCE_HTTPS` conforme documentação), base de dados e Redis com rede e credenciais restritas.

## Dependências

Execute auditorias periódicas (`pip audit`, `npm audit`) no seu ambiente e actualize dependências críticas em branches dedicadas, com testes.
