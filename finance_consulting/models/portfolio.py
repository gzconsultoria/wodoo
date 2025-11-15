from odoo import models, fields, api


class FinancePortfolio(models.Model):
    """
    Carteira de investimentos do cliente.
    Acompanha posições reais vs. recomendado.
    """
    _name = "finance.portfolio"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Portfolio Tracker"
    _order = "date_last_update desc"

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
        string="Nome da Carteira",
        required=True,
        tracking=True,
    )
    date_created = fields.Datetime(
        string="Data de Criação",
        default=fields.Datetime.now,
        readonly=True,
    )
    date_last_update = fields.Datetime(
        string="Última Atualização",
        auto_now=True,
    )

    # Valores
    total_value = fields.Float(
        string="Valor Total da Carteira",
        compute="_compute_total_value",
        store=True,
        help="Soma de todas as posições",
    )
    total_contributions = fields.Float(
        string="Total de Aportes",
        compute="_compute_total_contributions",
        store=True,
    )
    total_withdrawals = fields.Float(
        string="Total de Resgates",
        compute="_compute_total_withdrawals",
        store=True,
    )

    # Performance
    consolidated_return = fields.Float(
        string="Rentabilidade Consolidada (%)",
        compute="_compute_consolidated_return",
        store=True,
        help="Retorno total da carteira desde criação",
    )
    ytd_return = fields.Float(
        string="Rentabilidade YTD (%)",
        help="Retorno desde início do ano",
    )
    monthly_return = fields.Float(
        string="Rentabilidade Mensal (%)",
        help="Retorno do mês atual",
    )

    # Posições
    position_ids = fields.One2many(
        "finance.portfolio_position",
        "portfolio_id",
        string="Posições",
    )

    # Rebalanceamento
    allocation_variance = fields.Float(
        string="Variância de Alocação (%)",
        compute="_compute_allocation_variance",
        store=True,
        help="Desvio entre alocação atual vs. recomendada",
    )
    needs_rebalance = fields.Boolean(
        string="Necessita Rebalanceamento?",
        compute="_compute_needs_rebalance",
        store=True,
    )

    # Status
    state = fields.Selection(
        [
            ("active", "Ativa"),
            ("paused", "Pausada"),
            ("closed", "Encerrada"),
        ],
        string="Status",
        default="active",
        tracking=True,
    )

    @api.depends("position_ids.current_value")
    def _compute_total_value(self):
        """Calcula valor total da carteira."""
        for record in self:
            record.total_value = sum(record.position_ids.mapped("current_value"))

    @api.depends("position_ids.contributions")
    def _compute_total_contributions(self):
        """Calcula total de aportes."""
        for record in self:
            record.total_contributions = sum(record.position_ids.mapped("contributions"))

    @api.depends("position_ids.withdrawals")
    def _compute_total_withdrawals(self):
        """Calcula total de resgates."""
        for record in self:
            record.total_withdrawals = sum(record.position_ids.mapped("withdrawals"))

    @api.depends("total_value", "total_contributions", "total_withdrawals")
    def _compute_consolidated_return(self):
        """Calcula rentabilidade consolidada."""
        for record in self:
            net_invested = record.total_contributions - record.total_withdrawals
            if net_invested > 0:
                record.consolidated_return = (
                    (record.total_value - net_invested) / net_invested
                ) * 100
            else:
                record.consolidated_return = 0

    @api.depends("position_ids")
    def _compute_allocation_variance(self):
        """Calcula variância de alocação."""
        for record in self:
            # Implementação simplificada
            record.allocation_variance = 0

    @api.depends("allocation_variance")
    def _compute_needs_rebalance(self):
        """Verifica se carteira precisa rebalanceamento."""
        for record in self:
            # Threshold padrão: 5% de desvio
            record.needs_rebalance = abs(record.allocation_variance) > 5

    def action_update_values(self):
        """Atualiza valores das posições."""
        self.date_last_update = fields.Datetime.now()
        self.message_post(body="Valores da carteira atualizados.")

    def action_rebalance(self):
        """Registra rebalanceamento da carteira."""
        self.message_post(body="Carteira rebalanceada conforme plano.")


class FinancePortfolioPosition(models.Model):
    """
    Posições individuais dentro da carteira.
    """
    _name = "finance.portfolio_position"
    _description = "Portfolio Position"

    portfolio_id = fields.Many2one(
        "finance.portfolio",
        string="Carteira",
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
        string="Nome/Ticker",
        required=True,
    )
    quantity = fields.Float(
        string="Quantidade",
    )
    average_price = fields.Float(
        string="Preço Médio",
    )
    current_price = fields.Float(
        string="Preço Atual",
    )
    current_value = fields.Float(
        string="Valor Atual",
        compute="_compute_current_value",
        store=True,
    )
    contributions = fields.Float(
        string="Aportes",
        default=0,
    )
    withdrawals = fields.Float(
        string="Resgates",
        default=0,
    )
    individual_return = fields.Float(
        string="Retorno Individual (%)",
        compute="_compute_individual_return",
        store=True,
    )

    @api.depends("quantity", "current_price")
    def _compute_current_value(self):
        """Calcula valor atual da posição."""
        for record in self:
            record.current_value = record.quantity * record.current_price

    @api.depends("current_value", "contributions", "withdrawals")
    def _compute_individual_return(self):
        """Calcula retorno individual da posição."""
        for record in self:
            net_invested = record.contributions - record.withdrawals
            if net_invested > 0:
                record.individual_return = (
                    (record.current_value - net_invested) / net_invested
                ) * 100
            else:
                record.individual_return = 0
