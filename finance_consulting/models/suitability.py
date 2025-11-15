from odoo import models, fields, api
from odoo.exceptions import ValidationError


class FinanceSuitability(models.Model):
    """
    Formulário de Suitability - Conformidade CVM.
    Avalia o perfil de risco e adequação de investimentos.
    """
    _name = "finance.suitability"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Finance Suitability (CVM)"
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

    # Informações gerais
    date_created = fields.Datetime(
        string="Data de Criação",
        default=fields.Datetime.now,
        readonly=True,
    )
    date_expiry = fields.Date(
        string="Data de Vencimento",
        tracking=True,
        help="A Suitability vence após 2 anos",
    )
    is_expired = fields.Boolean(
        string="Vencido?",
        compute="_compute_is_expired",
        store=True,
    )

    # Perfil de risco (CVM)
    risk_profile = fields.Selection(
        [
            ("conservative", "Conservador - Segurança principal"),
            ("moderate", "Moderado - Equilíbrio risco/retorno"),
            ("aggressive", "Arrojado - Busca máximo retorno"),
        ],
        string="Perfil de Risco",
        required=True,
        tracking=True,
    )

    # Experiência do investidor
    investment_experience = fields.Selection(
        [
            ("none", "Nenhuma experiência"),
            ("basic", "Experiência básica"),
            ("intermediate", "Experiência intermediária"),
            ("advanced", "Experiência avançada"),
        ],
        string="Nível de Experiência",
        required=True,
        tracking=True,
    )

    # Conhecimento em produtos
    knows_stocks = fields.Boolean(
        string="Conhece Ações?",
        tracking=True,
    )
    knows_bonds = fields.Boolean(
        string="Conhece Renda Fixa?",
        tracking=True,
    )
    knows_funds = fields.Boolean(
        string="Conhece Fundos?",
        tracking=True,
    )
    knows_derivates = fields.Boolean(
        string="Conhece Derivativos?",
        tracking=True,
    )

    # Informações financeiras
    liquid_patrimony = fields.Float(
        string="Patrimônio Líquido",
        required=True,
        tracking=True,
    )
    investment_availability = fields.Float(
        string="Disponibilidade de Investimento",
        tracking=True,
        help="Percentual da renda disponível para investimentos",
    )
    monthly_income = fields.Float(
        string="Renda Mensal",
        tracking=True,
    )

    # Objetivos
    primary_objective = fields.Selection(
        [
            ("preservation", "Preservação de capital"),
            ("income", "Geração de renda"),
            ("growth", "Crescimento do patrimônio"),
            ("retirement", "Aposentadoria"),
            ("education", "Educação"),
            ("other", "Outro"),
        ],
        string="Objetivo Principal",
        required=True,
        tracking=True,
    )
    investment_horizon = fields.Selection(
        [
            ("short", "Curto prazo (0-1 ano)"),
            ("medium", "Médio prazo (1-5 anos)"),
            ("long", "Longo prazo (5+ anos)"),
        ],
        string="Horizonte de Investimento",
        required=True,
        tracking=True,
    )

    # Tolerância ao risco
    loss_tolerance_percent = fields.Float(
        string="Tolerância à Perda (%)",
        help="Percentual máximo aceitável de perda do patrimônio em cenário adverso",
        tracking=True,
    )
    past_losses_experience = fields.Text(
        string="Experiência com Perdas Anteriores",
        help="Como se comportou em caso de perdas financeiras no passado",
    )

    # Status e aprovação
    state = fields.Selection(
        [
            ("draft", "Rascunho"),
            ("approved", "Aprovado"),
            ("expired", "Vencido"),
            ("cancelled", "Cancelado"),
        ],
        string="Status",
        default="draft",
        compute="_compute_state",
        store=True,
        tracking=True,
    )

    # Documentação
    signed_date = fields.Date(
        string="Data de Assinatura",
        tracking=True,
    )
    notes = fields.Text(
        string="Observações do Consultor",
    )

    @api.depends("is_expired")
    def _compute_state(self):
        """Calcula estado baseado em vencimento."""
        for record in self:
            if record.is_expired:
                record.state = "expired"
            else:
                record.state = "approved"

    @api.depends("date_expiry")
    def _compute_is_expired(self):
        """Verifica se suitability está vencida."""
        today = fields.Date.today()
        for record in self:
            record.is_expired = record.date_expiry < today if record.date_expiry else True

    def action_approve(self):
        """Aprova a suitability."""
        self.signed_date = fields.Date.today()
        self.message_post(body="Suitability aprovada e assinada.")

    def action_renew(self):
        """Renova a suitability por mais 2 anos."""
        from datetime import timedelta

        today = fields.Date.today()
        self.date_expiry = today + timedelta(days=730)
        self.signed_date = today
        self.message_post(body="Suitability renovada por mais 2 anos.")

    @api.constrains("liquid_patrimony", "monthly_income", "loss_tolerance_percent")
    def _check_positive_values(self):
        """Valida que valores são positivos."""
        for record in self:
            if record.liquid_patrimony < 0:
                raise ValidationError("Patrimônio não pode ser negativo.")
            if record.monthly_income < 0:
                raise ValidationError("Renda mensal não pode ser negativa.")
            if record.loss_tolerance_percent < 0 or record.loss_tolerance_percent > 100:
                raise ValidationError("Tolerância à perda deve estar entre 0% e 100%.")
