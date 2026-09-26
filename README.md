# Agente com aprovação humana

Exemplo didático em Python: o programa **propõe** registrar um documento fictício para revisão, pede aprovação explícita e só então chama uma ferramenta local. Não usa modelo de IA nem envia dados a serviços externos.

## Executar

Requer Python 3, sem dependências externas:

```bash
python agente.py
```

Digite `aprovar` para executar; qualquer outra resposta cancela. Para testar:

```bash
python -m unittest -v test_agente.py
```

O GitHub Actions executa os testes a cada alteração.

## Decisões verificáveis

- A proposta é criada antes da ação.
- A ferramenta só registra após a palavra exata `aprovar`.
- A repetição da mesma proposta não cria dois registros no mesmo processo.
- Os registros ficam apenas na memória e desaparecem ao encerrar o programa.

**Limite:** este é um exemplo de controle de fluxo, não um agente autônomo, sistema de assinatura, envio ou solução de produção. Uma implementação real precisaria de identidade do aprovador, autorização por usuário, persistência, auditoria e proteção contra repetição entre processos.
