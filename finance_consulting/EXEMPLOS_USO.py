"""
EXEMPLO DE USO DO MÓDULO FINANCE CONSULTING
Guia de operações comuns via Python console do Odoo.
"""

# ============================================
# 1. CRIAR PERFIL FINANCEIRO
# ============================================

# Para tester no console do Odoo:
# python manage.py shell

from odoo import fields

# Criar novo perfil
profile = env['finance.profile'].create({
    'partner_id': 1,  # ID do cliente (res.partner)
    'advisor_id': env.user.id,
    'net_worth': 500000.00,
    'aum': 250000.00,
    'monthly_income': 10000.00,
    'monthly_expenses': 4000.00,
    'risk_profile': 'moderate',
    'investment_horizon': 'long',
    'investment_goals': 'Aposentadoria confortável em 15 anos',
    'target_return': 8.5,
    'state': 'draft',
})
profile.action_activate_profile()


# ============================================
# 2. CRIAR SUITABILITY
# ============================================

suitability = env['finance.suitability'].create({
    'finance_profile_id': profile.id,
    'advisor_id': env.user.id,
    'date_expiry': fields.Date.today() + timedelta(days=730),
    'risk_profile': 'moderate',
    'investment_experience': 'intermediate',
    'knows_stocks': True,
    'knows_bonds': True,
    'knows_funds': True,
    'knows_derivates': False,
    'liquid_patrimony': 500000.00,
    'investment_availability': 30.0,
    'monthly_income': 10000.00,
    'primary_objective': 'retirement',
    'investment_horizon': 'long',
    'loss_tolerance_percent': 25.0,
    'past_losses_experience': 'Cliente enfrentou perdas em 2008, comportou-se bem.',
})
suitability.action_approve()


# ============================================
# 3. CRIAR PLANO DE INVESTIMENTO
# ============================================

plan = env['finance.investment_plan'].create({
    'finance_profile_id': profile.id,
    'advisor_id': env.user.id,
    'name': 'Plano Alocação Balanceada 2024',
    'description': 'Alocação equilibrada 50/50 para horizonte de longo prazo.',
    'investment_horizon': 'long',
    'expected_return': 8.5,
    'fixed_income_percent': 40.0,
    'variable_income_percent': 35.0,
    'reits_percent': 15.0,
    'international_percent': 10.0,
    'pension_percent': 0.0,
    'rebalance_frequency': 'quarterly',
})

# Adicionar linhas
env['finance.investment_plan_line'].create({
    'plan_id': plan.id,
    'asset_class': 'fixed_income',
    'asset_name': 'LCI - Banco XYZ',
    'allocation_percent': 20.0,
    'description': 'Renda fixa segura',
})

env['finance.investment_plan_line'].create({
    'plan_id': plan.id,
    'asset_class': 'fixed_income',
    'asset_name': 'CDB - Caixa',
    'allocation_percent': 20.0,
    'description': 'Diversificação renda fixa',
})

env['finance.investment_plan_line'].create({
    'plan_id': plan.id,
    'asset_class': 'stocks',
    'asset_name': 'IBOV - VFIIT',
    'allocation_percent': 35.0,
    'description': 'Exposição ao mercado acionário brasileiro',
})

env['finance.investment_plan_line'].create({
    'plan_id': plan.id,
    'asset_class': 'reits',
    'asset_name': 'XP LOG - Fundo Logístico',
    'allocation_percent': 15.0,
    'description': 'FII com bom histórico de dividendos',
})

env['finance.investment_plan_line'].create({
    'plan_id': plan.id,
    'asset_class': 'international',
    'asset_name': 'SPY - ETF S&P500',
    'allocation_percent': 10.0,
    'description': 'Exposição ao mercado americano',
})

plan.action_submit_for_approval()
plan.action_approve()
plan.action_activate()


# ============================================
# 4. CRIAR CARTEIRA
# ============================================

portfolio = env['finance.portfolio'].create({
    'finance_profile_id': profile.id,
    'advisor_id': env.user.id,
    'name': 'Carteira Principal - Cliente XYZ',
    'state': 'active',
})

# Adicionar posições
positions_data = [
    {
        'asset_class': 'fixed_income',
        'asset_name': 'LCI - Banco XYZ',
        'quantity': 50000.0,
        'average_price': 1.0,
        'current_price': 1.0,
        'contributions': 50000.0,
        'withdrawals': 0.0,
    },
    {
        'asset_class': 'fixed_income',
        'asset_name': 'CDB - Caixa',
        'quantity': 50000.0,
        'average_price': 1.0,
        'current_price': 1.0,
        'contributions': 50000.0,
        'withdrawals': 0.0,
    },
    {
        'asset_class': 'stocks',
        'asset_name': 'IBOV - VFIIT',
        'quantity': 1200.0,
        'average_price': 75.0,
        'current_price': 78.5,
        'contributions': 87500.0,
        'withdrawals': 0.0,
    },
]

for pos in positions_data:
    pos['portfolio_id'] = portfolio.id
    env['finance.portfolio_position'].create(pos)


# ============================================
# 5. CRIAR DOSSIÊ CONSULTIVO
# ============================================

case = env['finance.consulting_case'].create({
    'finance_profile_id': profile.id,
    'advisor_id': env.user.id,
    'name': 'CONS-2024-001',
    'subject': 'Planejamento Financeiro Completo',
    'description': 'Avaliação de perfil e construção de plano de investimento.',
    'priority': 'high',
    'state': 'in_progress',
    'has_suitability': True,
    'has_id_copy': True,
    'has_address_proof': True,
    'has_income_proof': True,
    'has_cvm_term': True,
})


# ============================================
# 6. CRIAR PROPOSTA
# ============================================

proposal = env['finance.consulting_proposal'].create({
    'consulting_case_id': case.id,
    'investment_plan_id': plan.id,
    'name': 'Proposta de Alocação Balanceada',
    'proposal_text': '<h2>Recomendação de Alocação</h2><p>Baseado na análise realizada...</p>',
    'state': 'draft',
})
proposal.action_send()


# ============================================
# 7. REGISTRAR REUNIÃO
# ============================================

from datetime import datetime, timedelta

meeting = env['finance.consulting_meeting'].create({
    'consulting_case_id': case.id,
    'advisor_id': env.user.id,
    'name': 'Apresentação do Plano de Investimento',
    'meeting_date': datetime.now() + timedelta(days=1),
    'duration_minutes': 90,
    'meeting_type': 'virtual',
    'participants': 'João Silva, Maria Santos',
    'notes': 'Revisar plano e sanar dúvidas.',
    'outcomes': 'Plano aceito. Iniciar implementação.',
})


# ============================================
# 8. GERENCIAR STATUS
# ============================================

# Marcar revisão
profile.action_register_review()

# Finalizar caso
case.action_close_successful()

# Renovar suitability (2 anos)
suitability.action_renew()

# Atualizar valores carteira
portfolio.action_update_values()


# ============================================
# 9. CONSULTAS ÚTEIS
# ============================================

# Listar perfis do usuário atual
meus_perfis = env['finance.profile'].search([
    ('advisor_id', '=', env.user.id),
    ('state', '=', 'active'),
])

# Listar suitability vencidas
suitability_vencidas = env['finance.suitability'].search([
    ('is_expired', '=', True),
])

# Listar carteiras que precisam rebalanceamento
carteiras_desbalanceadas = env['finance.portfolio'].search([
    ('needs_rebalance', '=', True),
])

# Listar dossiês abertos
casos_abertos = env['finance.consulting_case'].search([
    ('state', 'in', ['open', 'in_progress']),
])

# Filtrar por cliente
cliente_id = 1
perfis_cliente = env['finance.profile'].search([
    ('partner_id', '=', cliente_id),
])

print(f"Perfis criados: {len(meus_perfis)}")
print(f"Suitability vencidas: {len(suitability_vencidas)}")
print(f"Carteiras desbalanceadas: {len(carteiras_desbalanceadas)}")
print(f"Casos abertos: {len(casos_abertos)}")
