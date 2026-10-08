# AI Farm Agent: estudo de fronteiras de ação

**Decisão:** B — STUDY · **Data:** 08/10/2026 · **Upstream:** [`ognistie/AI-Farm-Agent` em `4ffa018f50d25668e6e46726723b0ed6040caf2f`](https://github.com/ognistie/AI-Farm-Agent/tree/4ffa018f50d25668e6e46726723b0ed6040caf2f) · **Destino:** laboratório `agente-aprovacao-humana`.

O aplicativo externo automatiza uma sessão de desktop Windows com Maestro, agentes de domínio, memória local e execução de ações. Este repositório contém apenas um exemplo determinístico de aprovação em memória. Este estudo compara **fronteiras de autorização**, sem incorporar o aplicativo, seus prompts, seus modelos ou código upstream.

## Por que estudar aqui

O laboratório já demonstra proposta, decisão exata e efeito fictício. Seu próprio README registra que não oferece identidade do aprovador, persistência ou auditoria. O estudo ajuda a definir o próximo contrato de aprovação antes de ampliar o exemplo; não declara que o exemplo atual esteja pronto para contas reais. O `radar-evidence-kit` registra elegibilidade de citação e explicita que seus recibos não autorizam ações externas, então não é o destino deste probe.

## Evidência fixada no código upstream

| Limite | Código e condição | O que o probe demonstra |
|---|---|---|
| Leitura de arquivo fora do projeto | [`read_project` percorre `.md` e abre caminhos sem verificar o alvo real](https://github.com/ognistie/AI-Farm-Agent/blob/4ffa018f50d25668e6e46726723b0ed6040caf2f/ai-farm-agent/core/project_versions.py#L32-L60); [`plan_edit` envia o conteúdo lido ao cliente LLM](https://github.com/ognistie/AI-Farm-Agent/blob/4ffa018f50d25668e6e46726723b0ed6040caf2f/ai-farm-agent/agents/code_agent.py#L193-L215). | Um link simbólico `linked.md` dentro do projeto aponta para Markdown sintético fora da raiz; `read_project` o inclui. O helper de escrita `safe_rel` recusa o mesmo caminho, mas não é chamado na leitura. O probe **não chama LLM**. |
| Passo destrutivo em pedido de leitura | [`validate_steps` verifica forma e alguns objetivos, sem autorização geral por efeito](https://github.com/ognistie/AI-Farm-Agent/blob/4ffa018f50d25668e6e46726723b0ed6040caf2f/ai-farm-agent/core/plan_validator.py#L136-L202); o [controller valida e depois executa](https://github.com/ognistie/AI-Farm-Agent/blob/4ffa018f50d25668e6e46726723b0ed6040caf2f/ai-farm-agent/desktop/controller.py#L514-L562). | Uma subtask FILE para “listar arquivos” com passo `delete_file` é aprovada pelo validador. **Nenhuma exclusão é executada**; o teste não prova que o modelo geraria esse plano. |

O [executor](https://github.com/ognistie/AI-Farm-Agent/blob/4ffa018f50d25668e6e46726723b0ed6040caf2f/ai-farm-agent/core/automation.py#L362-L449) também aceita Python gerado no processo do usuário. Essa superfície não é reproduzida pelo probe e permanece fora deste laboratório. A [política de segurança upstream](https://github.com/ognistie/AI-Farm-Agent/blob/4ffa018f50d25668e6e46726723b0ed6040caf2f/SECURITY.md) já reconhece limites de execução e simulação. Não há evidência de incidente.

## Reprodução isolada

Requer Python 3.11+ e Git. Use uma cópia pública separada, revista e fixada no SHA; não instale dependências, não configure chave, não rode o aplicativo e não forneça diretórios reais ao probe.

```sh
git clone --no-checkout --depth 1 https://github.com/ognistie/AI-Farm-Agent.git ../ai-farm-agent-audit
git -C ../ai-farm-agent-audit fetch --depth 1 origin 4ffa018f50d25668e6e46726723b0ed6040caf2f
git -C ../ai-farm-agent-audit checkout --detach 4ffa018f50d25668e6e46726723b0ed6040caf2f
git -C ../ai-farm-agent-audit rev-parse HEAD
python3 studies/ai_farm_agent_probe.py --upstream ../ai-farm-agent-audit
```

O script recusa SHA divergente ou arquivos rastreados alterados. Ele carrega somente `project_versions.py` e `plan_validator.py` do checkout fixado, cria um diretório temporário e usa a string `SYNTHETIC_OUTSIDE`. Um checkout de terceiro continua sendo código executado no import: execute-o apenas em ambiente isolado. Na plataforma sem permissão para criar symlink, o teste correspondente retorna `SKIPPED` e código 2; isso não comprova segurança. `OBSERVED` significa **limite reproduzido**, não aprovação de segurança. Código 1 indica diferença frente ao snapshot e pede análise.

Resultado local em Linux/Python 3.12 com SHA fixado: `read_outside_symlink=OBSERVED`, `safe_rel_rejects_symlink=OBSERVED`, `delete_step_for_list_request=OBSERVED`. Este projeto não roda automaticamente esse probe na CI, porque ela não deve buscar nem executar um checkout externo. Os três testes existentes de `test_agente.py` continuam sendo o gate da CI deste repositório.

## Contrato de aprovação para uma experiência futura

1. O agente propõe uma ação tipada com ator, recurso, efeito (`read`, `write`, `delete`, `send`, `execute`), payload canônico, escopo e expiração. Texto externo é dado e não emite autorização.
2. Uma pessoa identificada vê a mesma versão do payload que poderá ser executada. A decisão é vinculada ao hash dessa versão e ao escopo; qualquer mudança invalida a decisão.
3. O executor, e não apenas o planejador, nega efeitos sem grant válido, inclusive exclusão numa tarefa de leitura. Um `dry_run` retorna antes de qualquer handler com efeito.
4. O executor registra um recibo idempotente, com resultado e versão de política, sem persistir segredos; cancelamento e repetição têm semântica definida.

Isto é uma **especificação de experimento**, não API implementada neste PR. Um primeiro teste de aceitação seria: “listar arquivos” + proposta `delete_file` → recusada sem tocar em arquivo; aprovação para payload A + execução de payload B → recusada. Antes de implementar, identificar um fluxo real da Help Mídias ou Radar e a identidade/integração responsável. n8n pode orquestrar notificações e revisão, enquanto a política e o efeito ficam em serviço testável.

## Critérios de reavaliação

- Caso de uso real para desktop Windows ou ação externa identificada, com dono e métricas de sucesso.
- Probes negativos em Windows, suíte determinística com dependências fixadas e avaliação de tarefas ambíguas; registrar resultados, não assumir que o README upstream os prova.
- Isolamento de execução, autorização por efeito e recurso, controle de symlinks/leitura, retenção de dados e revisão de licenças/assets.
- Medidas por tarefa de qualidade, erro grave, latência p95 e custo. Só então decidir se estudar basta ou se há motivo para extrair/reimplementar uma capacidade estreita.

Referência ampliada: relatório `Auditoria_AI_Farm_Agent_Radar_2026-10-08.md` no material de auditoria do projeto Radar. Não é dependência de runtime.
