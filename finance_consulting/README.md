# Módulo de Consultoria Financeira para Odoo 19

Um módulo completo e modular para gestão de consultoria financeira, investimentos e conformidade CVM.

## 🎯 Funcionalidades Principais

### 1. **Perfis Financeiros (Finance Profile)**
- Armazenamento seguro de informações financeiras dos clientes
- Cálculo automático de poupança mensal
- Histórico de evolução de patrimônio
- Tracking de status de suitability
- Integração com mail.thread para auditoria completa

### 2. **Suitability (Conformidade CVM)**
- Formulário completo conforme regulação CVM
- Avaliação de perfil de risco (Conservador/Moderado/Arrojado)
- Verificação de experiência e conhecimento de produtos
- Controle automático de vencimento (2 anos)
- Status de aprovação com assinatura

### 3. **Planos de Investimento**
- Alocação recomendada por classe de ativos:
  - Renda Fixa
  - Renda Variável
  - FII (Fundos Imobiliários)
  - Exterior
  - Previdência
- Justificativa técnica da estratégia
- Horizonte de investimento
- Rebalanceamento automático com frequência configurável

### 4. **Carteira (Portfolio Tracker)**
- Acompanhamento em tempo real de posições
- Cálculo de rentabilidade consolidada, YTD e mensal
- Rastreamento de aportes e resgates
- Identificação automática de carteiras que precisam rebalanceamento
- Detalhamento por classe de ativo

### 5. **Dossiê Consultivo (Consulting Case)**
- Histórico completo de interações com cliente
- Checklist de onboarding (RG, comprovante renda, Suitability, Termo CVM, FATCA)
- Registro de propostas enviadas
- Documentação integrada
- Rastreamento de reuniões
- Integração com Google Calendar (preparado para expansão)

### 6. **Segurança e Conformidade**
- Grupos de permissão: Consultor, Compliance Officer, Gerente
- Record rules garantindo isolamento de dados por consultor
- ACL completo por modelo e grupo
- Auditoria via mail.thread em todas as entidades críticas
- Alertas automáticos de suitability vencida

## 📋 Modelos Implementados

### Core Models
- `finance.profile` - Perfil financeiro do cliente
- `finance.suitability` - Avaliação de suitability
- `finance.investment_plan` - Plano de investimento
- `finance.investment_plan_line` - Linhas detalhadas de alocação
- `finance.portfolio` - Carteira de investimentos
- `finance.portfolio_position` - Posições individuais
- `finance.consulting_case` - Dossiê consultivo
- `finance.consulting_proposal` - Propostas
- `finance.consulting_meeting` - Reuniões

## 🔐 Segurança

### Grupos de Acesso
```
├── Consultor (group_finance_consultant)
│   └── Acesso total a seus próprios clientes
├── Compliance Officer (group_finance_compliance)
│   └── Acesso a todas as suitability para validação
└── Gerente (group_finance_manager)
    └── Acesso total a todos os dados e relatórios
```

### Record Rules
- Consultores veem apenas seus próprios perfis
- Compliance vê todas suitability
- Gerentes têm acesso irrestrito
- Permissões granulares por modelo

## 📊 Views Implementadas (Padrão Odoo 19)

### Padrões Seguidos
✅ Uso de `modifiers` ao invés de `attrs` (Odoo 19+)
✅ Estrutura obrigatória: `<header>`, `<sheet>`, `<chatter>`
✅ Search views minimalistas sem divs/notebooks
✅ Validação XML rigorosa
✅ Campos computed com `store=True`
✅ OWL padrão em templates kanban
✅ Sem `active_id` em form views

### Views por Modelo
- **Finance Profile**: List, Form, Search
- **Suitability**: List, Form, Search com filtros de vencimento
- **Investment Plan**: List, Form, Search
- **Portfolio**: List, Form, Search com alertas de rebalanceamento
- **Consulting Case**: List, Form, Search com checklist visual

## 🚀 Instalação

### Pré-requisitos
- Odoo 19
- Módulos base: `base`, `mail`, `calendar`, `crm`, `account`

### Passos

1. **Copiar o módulo para addons:**
```bash
cp -r finance_consulting /path/to/odoo/addons/
```

2. **Instalar no Odoo:**
   - Ir para Apps
   - Buscar por "Finance Consulting Module"
   - Clicar em "Install"

3. **Criar Grupos de Acesso:**
   - Ir para Configurações > Usuários
   - Adicionar usuários aos grupos:
     - "Consultoria Financeira / Consultor"
     - "Consultoria Financeira / Compliance"
     - "Consultoria Financeira / Gerente"

## 📈 Uso Típico

### Fluxo 1: Onboarding de Cliente
1. Criar Perfil Financeiro
2. Preencher Suitability (CVM)
3. Criar Dossiê Consultivo e marcar documentos
4. Gerar Plano de Investimento
5. Registrar Carteira com posições

### Fluxo 2: Revisão de Cliente
1. Abrir Dossiê do cliente
2. Registrar nova Reunião
3. Atualizar dados do Perfil Financeiro
4. Registrar nova Proposta se necessário
5. Acompanhar via Chatter e Atividades

### Fluxo 3: Monitoramento de Suitability
- Sistema verifica vencimento diariamente
- Status automático para "vencido" na data limite
- Filtro rápido em Suitability para renovação
- Botão "Renovar" (2 anos)

## 🔄 Automações

### Cron Jobs
- **Diário**: Verifica suitability vencida
- **Semanal**: Verifica carteiras que precisam rebalanceamento

### Ações Automáticas
- Alerta quando suitability expira
- Notificação de rebalanceamento necessário
- Log automático de mudanças críticas (mail.thread)

## 📐 Campos Customizados

### Campos Computed (store=True)
- `monthly_savings` (Profile)
- `suitability_status` (Profile)
- `total_allocation` (Investment Plan)
- `total_value` (Portfolio)
- `consolidated_return` (Portfolio)
- `needs_rebalance` (Portfolio)
- `is_expired` (Suitability)

## 🛠️ Boas Práticas Implementadas

✅ **Padrões Odoo 19:**
- Sem `attrs`, apenas `modifiers`
- Sem `states="..."` em XML
- Views com validação rigorosa
- Campos sempre em snake_case
- Métodos action_ prefixados

✅ **Segurança:**
- Record rules por usuário/grupo
- ACL completo no ir.model.access.csv
- Mail thread em entidades críticas
- Validação de valores (positivos, percentuais, etc)

✅ **Performance:**
- Campos computed com store=True
- Índices potenciais via constraints
- Evita loops Python com search

✅ **Manutenibilidade:**
- Um modelo por arquivo
- Métodos pequenos e focados
- Docstrings em públicos
- Comentários nas restrições

## 📝 Relatórios Futuros

Preparados para expansão:
- Relatório de Performance de Carteira
- Relatório de Compliance
- Análise de Alocação vs Recomendado
- Auditoria de Transações

## 🔗 Relacionamentos

```
res.partner (Cliente)
    ├── finance.profile (1:N)
    │   ├── finance.suitability (1:N)
    │   ├── finance.investment_plan (1:N)
    │   │   └── finance.investment_plan_line (1:N)
    │   ├── finance.portfolio (1:N)
    │   │   └── finance.portfolio_position (1:N)
    │   └── finance.consulting_case (1:N)
    │       ├── finance.consulting_proposal (1:N)
    │       ├── finance.consulting_meeting (1:N)
    │       └── ir.attachment (N:N)
```

## 🚨 Validações Implementadas

### Constraints
- Patrimônio/AUM/Renda não podem ser negativos
- Alocação total deve ser 100%
- Tolerância à perda entre 0-100%
- Valores financeiros sempre positivos

### Domain Filters
- Consultant vê só seus clientes
- Suitability expirada marcada automaticamente
- Portfolio identifica necessidade de rebalanceamento

## 📞 Suporte Técnico

### Troubleshooting

**Erro: "Alocação total deve ser 100%"**
- Verificar percentuais em Renda Fixa, Variável, FII, Exterior, Previdência
- Soma deve ser exatamente 100%

**Suitability não apareça em Perfil**
- Criar nova Suitability após perfil
- Sistema busca a mais recente por data

**Permissão negada em modelo**
- Verificar grupo do usuário
- Confirmar ir.model.access.csv está carregado
- Reiniciar navegador se necessário

## 📦 Estrutura de Arquivos

```
finance_consulting/
├── __manifest__.py          # Metadados do módulo
├── __init__.py              # Imports
├── models/
│   ├── __init__.py
│   ├── finance_profile.py
│   ├── suitability.py
│   ├── investment_plan.py
│   ├── portfolio.py
│   └── consulting_case.py
├── views/
│   ├── menus.xml
│   ├── finance_profile_views.xml
│   ├── suitability_views.xml
│   ├── investment_plan_views.xml
│   ├── portfolio_views.xml
│   └── consulting_case_views.xml
├── security/
│   ├── security_groups.xml
│   └── ir.model.access.csv
└── data/
    ├── default_stages.xml
    ├── cron_jobs.xml
    └── automated_actions.xml
```

## 🎓 Características Educacionais

Ideal para aprender:
- Padrões Odoo 19
- Arquitetura modular
- Segurança em Odoo (record rules, ACL)
- Mail thread e auditoria
- Campos computed
- Validações e constraints
- Views XML avançadas
- Cron jobs

## 📄 Licença

LGPL-3

## 🏢 Autor

GZ Consultoria

---

**Versão**: 19.0.1.0.0
**Compatibilidade**: Odoo 19+
**Status**: Pronto para uso em produção
