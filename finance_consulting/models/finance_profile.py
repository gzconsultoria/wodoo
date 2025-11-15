from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta


class FinanceProfile(models.Model):
    """
    Perfil financeiro do cliente.
    Armazena informações críticas para consultoria de investimentos.
    """
    _name = "finance.profile"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Finance Profile"
    _order = "date_created desc"

    # Identificação
    partner_id = fields.Many2one(
        "res.partner",
        string="Cliente",
        required=True,
        ondelete="cascade",
        tracking=True,
    )
    advisor_id = fields.Many2one(
        "res.users",
        string="Consultor Responsável",
        required=True,
        default=lambda self: self.env.user,
        tracking=True,
    )

    # Dados financeiros
    net_worth = fields.Float(
        string="Patrimônio Líquido",
        tracking=True,
        help="Valor total de ativos menos passivos",
    )
    aum = fields.Float(
        string="AUM (Valor Investido)",
        tracking=True,
        help="Assets Under Management - valor total investido",
    )
    monthly_income = fields.Float(
        string="Renda Mensal",
        tracking=True,
    )
    monthly_expenses = fields.Float(
        string="Despesas Mensárias",
        tracking=True,
    )
    monthly_savings = fields.Float(
        string="Poupança Mensal",
        compute="_compute_monthly_savings",
        store=True,
        help="Renda Mensal - Despesas Mensárias",
    )

    # Perfil de risco
    risk_profile = fields.Selection(
        [
            ("conservative", "Conservador"),
            ("moderate", "Moderado"),
            ("aggressive", "Arrojado"),
        ],
        string="Perfil de Risco",
        tracking=True,
        help="Perfil definido pela Suitability",
    )
    investment_horizon = fields.Selection(
        [
            ("short", "Curto Prazo (0-1 ano)"),
            ("medium", "Médio Prazo (1-5 anos)"),
            ("long", "Longo Prazo (5+ anos)"),
        ],
        string="Horizonte de Investimento",
        tracking=True,
    )

    # Metas e objetivos
    investment_goals = fields.Text(
        string="Objetivos de Investimento",
        help="Descrever metas financeiras específicas",
    )
    target_return = fields.Float(
        string="Retorno Esperado (%)",
        help="Meta de retorno anual esperada",
    )

    # Status
    state = fields.Selection(
        [
            ("draft", "Rascunho"),
            ("active", "Ativo"),
            ("paused", "Pausado"),
            ("archived", "Arquivado"),
        ],
        string="Status",
        default="draft",
        tracking=True,
    )
    suitability_status = fields.Selection(
        [
            ("pending", "Pendente"),
            ("approved", "Aprovado"),
            ("expired", "Vencido"),
        ],
        string="Status Suitability",
        compute="_compute_suitability_status",
        store=True,
    )
    suitability_expiry_date = fields.Date(
        string="Data de Vencimento da Suitability",
        tracking=True,
    )

    # Datas
    date_created = fields.Datetime(
        string="Data de Criação",
        default=fields.Datetime.now,
        readonly=True,
    )
    date_last_review = fields.Datetime(
        string="Última Revisão",
        tracking=True,
    )

    # Relacionamentos
    suitability_id = fields.Many2one(
        "finance.suitability",
        string="Suitability Atual",
        compute="_compute_suitability",
        store=True,
    )
    investment_plan_ids = fields.One2many(
        "finance.investment_plan",
        "finance_profile_id",
        string="Planos de Investimento",
    )
    portfolio_ids = fields.One2many(
        "finance.portfolio",
        "finance_profile_id",
        string="Carteiras",
    )
    consulting_case_ids = fields.One2many(
        "finance.consulting_case",
        "finance_profile_id",
        string="Dossiês Consultivos",
    )

    # Evolução financeira
    aum_history = fields.Text(
        string="Histórico AUM (JSON)",
        help="Registro histórico de evolução do patrimônio",
    )

    @api.depends("monthly_income", "monthly_expenses")
    def _compute_monthly_savings(self):
        """Calcula poupança mensal disponível."""
        for record in self:
            record.monthly_savings = record.monthly_income - record.monthly_expenses

    @api.depends("suitability_expiry_date")
    def _compute_suitability_status(self):
        """Verifica status da suitability baseado na data de vencimento."""
        today = fields.Date.today()
        for record in self:
            if not record.suitability_expiry_date:
                record.suitability_status = "pending"
            elif record.suitability_expiry_date < today:
                record.suitability_status = "expired"
            else:
                record.suitability_status = "approved"

    @api.depends("partner_id")
    def _compute_suitability(self):
        """Obtém suitability mais recente do cliente."""
        for record in self:
            suitability = self.env["finance.suitability"].search(
                [("finance_profile_id", "=", record.id)],
                order="date_created desc",
                limit=1,
            )
            record.suitability_id = suitability

    def action_activate_profile(self):
        """Ativa o perfil financeiro."""
        self.state = "active"
        self.message_post(body="Perfil financeiro ativado.")

    def action_pause_profile(self):
        """Pausa o perfil financeiro."""
        self.state = "paused"
        self.message_post(body="Perfil financeiro pausado.")

    def action_archive_profile(self):
        """Arquiva o perfil financeiro."""
        self.state = "archived"
        self.message_post(body="Perfil financeiro arquivado.")

    def action_register_review(self):
        """Registra revisão do perfil."""
        self.date_last_review = fields.Datetime.now()
        self.message_post(body="Revisão do perfil realizada.")

    @api.constrains("monthly_income", "monthly_expenses", "aum", "net_worth")
    def _check_positive_values(self):
        """Valida que valores financeiros são positivos."""
        for record in self:
            if record.monthly_income < 0:
                raise ValidationError("Renda mensal não pode ser negativa.")
            if record.monthly_expenses < 0:
                raise ValidationError("Despesas não podem ser negativas.")
            if record.aum < 0:
                raise ValidationError("AUM não pode ser negativo.")
            if record.net_worth < 0:
                raise ValidationError("Patrimônio líquido não pode ser negativo.")
