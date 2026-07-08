#!/usr/bin/env bash
# Hook Stop do plugin workflow-comercial.
#
# Dispara toda vez que Claude termina de responder. Se a skill gerar-proposta
# rodou nesta sessão e produziu um rascunho de proposta, este hook exige que
# o Passo 8 do SKILL.md (depósito no SharePoint/CRM) já tenha acontecido
# antes do turno terminar de verdade — essa é a trilha de auditoria do
# processo, já que o Cowork não mantém log técnico completo por conta própria.
#
# Convenção de hooks do Claude Code: saída (stderr) + exit code 2 bloqueia o
# Stop e devolve a mensagem para o agente continuar o turno; exit code 0
# libera o Stop normalmente. Verifique essa convenção contra a documentação
# de hooks vigente (/en/hooks) antes de publicar em produção — este script
# foi escrito com base na referência de plugins, não testado contra uma
# sessão real do Cowork.
#
# O marcador de depósito é criado pela própria skill gerar-proposta (Passo 8)
# depois de confirmar o upload no SharePoint/CRM via conector M365. Local do
# marcador: dentro do diretório do projeto atual, para não vazar entre
# projetos/clientes diferentes.

set -u

MARCADOR="${CLAUDE_PROJECT_DIR:-.}/.proposta_deposito_confirmado"
RASCUNHO_PENDENTE="${CLAUDE_PROJECT_DIR:-.}/.proposta_rascunho_em_andamento"

# Se não há rascunho de proposta em andamento nesta sessão/projeto, o hook
# não tem nada a checar — libera o Stop normalmente. Isso evita que o hook
# trave sessões que não têm nada a ver com a skill gerar-proposta.
if [ ! -f "$RASCUNHO_PENDENTE" ]; then
  exit 0
fi

if [ -f "$MARCADOR" ]; then
  # Depósito confirmado — remove o marcador de "em andamento" e libera o Stop.
  rm -f "$RASCUNHO_PENDENTE"
  exit 0
fi

echo "Bloqueado: existe um rascunho de proposta gerado nesta sessão que ainda não foi" >&2
echo "depositado no SharePoint/CRM (Passo 8 da skill gerar-proposta). Deposite o" >&2
echo "documento final e confirme antes de encerrar — essa é a trilha de auditoria" >&2
echo "obrigatória do processo." >&2
exit 2
