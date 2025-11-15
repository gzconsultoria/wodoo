from odoo import models, fields, api
from odoo.exceptions import ValidationError


class FinanceInvestmentPlan(models.Model):
    """
    Plano de investimento recomendado.
    Contém alocação de ativos e estratégia de rebalanceamento.
    """
    _name = "finance.investment_plan"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Investment Plan"
    _order = "date_created desc"

    finance_profile_id = fields.Many2one(
        "finance.profile",
        string="Perfil Financeiro",
        required=True,
        ondelete="cascade",
        tracking=True,
    )
    advisor_id = fields.Many2one(
        "res.users",
        string="Consultor",
        required=True,
        default=lambda self: self.env.user,
        tracking=True,
    )

    # Identificação
    name = fields.Char(
        string="Nome do Plano",
        required=True,
        tracking=True,
    )
    date_created = fields.Datetime(
        string="Data de Criação",
        default=fields.Datetime.now,
        readonly=True,
    )
    date_approved = fields.Date(
        string="Data de Aprovação",
        tracking=True,
    )

    # Estratégia
    description = fields.Text(
        string="Descrição da Estratégia",
        help="Justificativa técnica e fundamentos da alocação",
    )
    investment_horizon = fields.Selection(
        [
            ("short", "Curto Prazo (0-1 ano)"),
            ("medium", "Médio Prazo (1-5 anos)"),
            ("long", "Longo Prazo (5+ anos)"),
        ],
        string="Horizonte de Investimento",
        required=True,
        tracking=True,
    )
    expected_return = fields.Float(
        string="Retorno Esperado (%)",
        help="Meta anual de retorno",
        tracking=True,
    )

    # Alocação recomendada
    fixed_income_percent = fields.Float(
        string="Renda Fixa (%)",
        default=0,
        tracking=True,
    )
    variable_income_percent = fields.Float(
        string="Renda Variável (%)",
        default=0,
        tracking=True,
    )
    reits_percent = fields.Float(
        string="FII - Fundos Imobiliários (%)",
        default=0,
        tracking=True,
    )
    international_percent = fields.Float(
        string="Exterior (%)",
        default=0,
        tracking=True,
    )
    pension_percent = fields.Float(
        string="Previdência (%)",
        default=0,
        tracking=True,
    )

    total_allocation = fields.Float(
        string="Total de Alocação (%)",
        compute="_compute_total_allocation",
        store=True,
        help="Soma de todos os percentuais - deve ser 100%",
    )

    # Status
    state = fields.Selection(
        [
            ("draft", "Rascunho"),
            ("pending_approval", "Aguardando Aprovação"),
            ("approved", "Aprovado"),
            ("active", "Em Execução"),
            ("suspended", "Suspenso"),
            ("archived", "Arquivado"),
        ],
        string="Status",
        default="draft",
        tracking=True,
    )

    # Rebalanceamento
    rebalance_frequency = fields.Selection(
        [
            ("monthly", "Mensal"),
            ("quarterly", "Trimestral"),
            ("semiannual", "Semestral"),
            ("annual", "Anual"),
        ],
        string="Frequência de Rebalanceamento",
        tracking=True,
    )
    next_rebalance_date = fields.Date(
        string="Próximo Rebalanceamento",
        tracking=True,
    )

    # Linhas do plano
    plan_line_ids = fields.One2many(
        "finance.investment_plan_line",
        "plan_id",
        string="Detalhes de Alocação",
    )

    @api.depends(
        "fixed_income_percent",
        "variable_income_percent",
        "reits_percent",
        "international_percent",
        "pension_percent",
    )
    def _compute_total_allocation(self):
        """Calcula alocação total."""
        for record in self:
            record.total_allocation = (
                record.fixed_income_percent
                + record.variable_income_percent
                + record.reits_percent
                + record.international_percent
                + record.pension_percent
            )

    def action_submit_for_approval(self):
        """Submete plano para aprovação."""
        self.state = "pending_approval"
        self.message_post(body="Plano submetido para aprovação.")

    def action_approve(self):
        """Aprova o plano."""
        self.state = "approved"
        self.date_approved = fields.Date.today()
        self.message_post(body="Plano de investimento aprovado.")

    def action_activate(self):
        """Ativa o plano."""
        self.state = "active"
        self.message_post(body="Plano de investimento ativado.")

    def action_suspend(self):
        """Suspende o plano."""
        self.state = "suspended"
        self.message_post(body="Plano de investimento suspenso.")

    @api.constrains("total_allocation")
    def _check_total_allocation(self):
        """Valida que alocação total é 100%."""
        for record in self:
            if abs(record.total_allocation - 100.0) > 0.01:
                raise ValidationError(
                    f"Alocação total deve ser 100%. Atual: {record.total_allocation}%"
                )


class FinanceInvestmentPlanLine(models.Model):
    """
    Linhas detalhadas do plano de investimento.
    Especifica ativos recomendados e suas alocações.
    """
    _name = "finance.investment_plan_line"
    _description = "Investment Plan Line"

    plan_id = fields.Many2one(
        "finance.investment_plan",
        string="Plano",
        required=True,
        ondelete="cascade",
    )
    asset_class = fields.Selection(
        [
            ("fixed_income", "Renda Fixa"),
            ("stocks", "Ações"),
            ("reits", "FII"),
            ("international", "Exterior"),
            ("pension", "Previdência"),
        ],
        string="Classe de Ativo",
        required=True,
    )
    asset_name = fields.Char(
        string="Nome do Ativo",
        required=True,
        help="Ex: VALE3, LCI, Fundo X",
    )
    allocation_percent = fields.Float(
        string="Alocação (%)",
        required=True,
    )
    description = fields.Text(
        string="Justificativa da Recomendação",
    )
