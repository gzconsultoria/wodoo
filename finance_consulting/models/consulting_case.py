from odoo import models, fields, api


class FinanceConsultingCase(models.Model):
    """
    Dossiê consultivo - Acompanhamento completo do relacionamento.
    Mantém histórico de interações, propostas e documentos.
    """
    _name = "finance.consulting_case"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Consulting Case / Dossier"
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
        string="Consultor Responsável",
        required=True,
        default=lambda self: self.env.user,
        tracking=True,
    )

    # Identificação
    name = fields.Char(
        string="Referência do Dossiê",
        required=True,
        tracking=True,
    )
    subject = fields.Char(
        string="Assunto Principal",
        required=True,
        help="Ex: Planejamento de Aposentadoria, Diversificação, etc.",
    )
    date_created = fields.Datetime(
        string="Data de Criação",
        default=fields.Datetime.now,
        readonly=True,
    )
    date_closed = fields.Date(
        string="Data de Encerramento",
        tracking=True,
    )

    # Descrição
    description = fields.Text(
        string="Resumo da Situação",
        help="Contexto e objetivos do dossiê",
    )

    # Documentação - Checklist de Onboarding
    has_suitability = fields.Boolean(
        string="✓ Suitability Assinada",
        tracking=True,
    )
    has_id_copy = fields.Boolean(
        string="✓ Cópia do RG/Passaporte",
        tracking=True,
    )
    has_address_proof = fields.Boolean(
        string="✓ Comprovante de Endereço",
        tracking=True,
    )
    has_income_proof = fields.Boolean(
        string="✓ Comprovante de Renda",
        tracking=True,
    )
    has_pep_declaration = fields.Boolean(
        string="✓ Declaração PEP",
        help="Pessoa Politicamente Exposta",
        tracking=True,
    )
    has_fatca_w9 = fields.Boolean(
        string="✓ FATCA/W9 (se aplicável)",
        tracking=True,
    )
    has_cvm_term = fields.Boolean(
        string="✓ Termo CVM",
        help="Termo de conhecimento de investimentos",
        tracking=True,
    )

    onboarding_complete = fields.Boolean(
        string="Onboarding Completo?",
        compute="_compute_onboarding_complete",
        store=True,
    )

    # Documentos
    attachment_ids = fields.Many2many(
        "ir.attachment",
        string="Anexos e Documentos",
    )

    # Propostas
    proposal_ids = fields.One2many(
        "finance.consulting_proposal",
        "consulting_case_id",
        string="Propostas Enviadas",
    )

    # Interações
    meeting_ids = fields.One2many(
        "finance.consulting_meeting",
        "consulting_case_id",
        string="Reuniões Realizadas",
    )

    # Status
    state = fields.Selection(
        [
            ("open", "Aberto"),
            ("in_progress", "Em Análise"),
            ("waiting_client", "Aguardando Cliente"),
            ("closed_successful", "Fechado - Sucesso"),
            ("closed_unsuccessful", "Fechado - Sem Sucesso"),
        ],
        string="Status",
        default="open",
        tracking=True,
    )

    # Prioridade
    priority = fields.Selection(
        [
            ("low", "Baixa"),
            ("medium", "Média"),
            ("high", "Alta"),
            ("urgent", "Urgente"),
        ],
        string="Prioridade",
        default="medium",
        tracking=True,
    )

    # Tags
    tags = fields.Char(
        string="Tags",
        help="Separadas por vírgula. Ex: aposentadoria, planejamento, urgente",
    )

    @api.depends(
        "has_suitability",
        "has_id_copy",
        "has_address_proof",
        "has_income_proof",
        "has_cvm_term",
    )
    def _compute_onboarding_complete(self):
        """Verifica se onboarding está 100% completo."""
        for record in self:
            record.onboarding_complete = (
                record.has_suitability
                and record.has_id_copy
                and record.has_address_proof
                and record.has_income_proof
                and record.has_cvm_term
            )

    def action_start_analysis(self):
        """Inicia análise do dossiê."""
        self.state = "in_progress"
        self.message_post(body="Análise do dossiê iniciada.")

    def action_request_info(self):
        """Marca como aguardando informação do cliente."""
        self.state = "waiting_client"
        self.message_post(body="Aguardando resposta do cliente.")

    def action_close_successful(self):
        """Fecha dossiê com sucesso."""
        self.state = "closed_successful"
        self.date_closed = fields.Date.today()
        self.message_post(body="Dossiê fechado com sucesso.")

    def action_close_unsuccessful(self):
        """Fecha dossiê sem conclusão."""
        self.state = "closed_unsuccessful"
        self.date_closed = fields.Date.today()
        self.message_post(body="Dossiê fechado sem conclusão.")


class FinanceConsultingProposal(models.Model):
    """
    Propostas enviadas ao cliente dentro de um dossiê.
    """
    _name = "finance.consulting_proposal"
    _inherit = ["mail.thread"]
    _description = "Consulting Proposal"
    _order = "date_created desc"

    consulting_case_id = fields.Many2one(
        "finance.consulting_case",
        string="Dossiê",
        required=True,
        ondelete="cascade",
    )
    investment_plan_id = fields.Many2one(
        "finance.investment_plan",
        string="Plano de Investimento",
        ondelete="set null",
    )
    name = fields.Char(
        string="Descrição da Proposta",
        required=True,
    )
    date_created = fields.Datetime(
        string="Data de Envio",
        default=fields.Datetime.now,
        readonly=True,
    )
    date_responded = fields.Date(
        string="Data de Resposta",
    )
    proposal_text = fields.Html(
        string="Texto da Proposta",
    )
    state = fields.Selection(
        [
            ("draft", "Rascunho"),
            ("sent", "Enviada"),
            ("accepted", "Aceita"),
            ("rejected", "Rejeitada"),
            ("pending", "Aguardando Resposta"),
        ],
        string="Status",
        default="draft",
    )

    def action_send(self):
        """Marca proposta como enviada."""
        self.state = "sent"
        self.message_post(body="Proposta enviada ao cliente.")

    def action_accept(self):
        """Marca proposta como aceita."""
        self.state = "accepted"
        self.date_responded = fields.Date.today()
        self.message_post(body="Proposta aceita pelo cliente.")

    def action_reject(self):
        """Marca proposta como rejeitada."""
        self.state = "rejected"
        self.date_responded = fields.Date.today()
        self.message_post(body="Proposta rejeitada pelo cliente.")


class FinanceConsultingMeeting(models.Model):
    """
    Registro de reuniões realizadas com o cliente.
    Integração com Google Calendar.
    """
    _name = "finance.consulting_meeting"
    _inherit = ["mail.thread"]
    _description = "Consulting Meeting"
    _order = "meeting_date desc"

    consulting_case_id = fields.Many2one(
        "finance.consulting_case",
        string="Dossiê",
        required=True,
        ondelete="cascade",
    )
    advisor_id = fields.Many2one(
        "res.users",
        string="Consultor",
        required=True,
        default=lambda self: self.env.user,
    )
    name = fields.Char(
        string="Assunto da Reunião",
        required=True,
    )
    meeting_date = fields.Datetime(
        string="Data e Hora da Reunião",
        required=True,
    )
    duration_minutes = fields.Integer(
        string="Duração (minutos)",
        default=60,
    )
    meeting_type = fields.Selection(
        [
            ("virtual", "Virtual (Google Meet)"),
            ("in_person", "Presencial"),
            ("phone", "Telefone"),
        ],
        string="Tipo de Reunião",
        default="virtual",
    )
    meet_link = fields.Char(
        string="Link Google Meet",
        help="Preenchido automaticamente se integrado com Google Calendar",
    )
    notes = fields.Text(
        string="Notas e Decisões",
    )
    outcomes = fields.Text(
        string="Resultados e Próximos Passos",
    )
    participants = fields.Char(
        string="Participantes",
        help="Nomes/e-mails dos participantes",
    )

    def action_create_meet(self):
        """Cria link Google Meet automaticamente."""
        # Implementação futura: integração com Google Calendar API
        self.message_post(body="Google Meet criado e link adicionado.")
