# GUIA DE INSTALAÇÃO E TROUBLESHOOTING

## 📦 Pré-requisitos

- **Odoo 19** (Community ou Enterprise)
- **Python 3.10+**
- **Módulos dependentes:**
  - `base` (padrão)
  - `mail` (padrão)
  - `calendar` (padrão)
  - `crm` (padrão)
  - `account` (padrão)

---

## 🚀 INSTALAÇÃO PASSO A PASSO

### 1. Copiar o Módulo

```bash
# Via terminal do servidor
cp -r finance_consulting /path/to/odoo/addons/

# Ou via Docker
docker cp finance_consulting odoo_container:/usr/lib/python3/dist-packages/odoo/addons/
```

### 2. Atualizar Lista de Módulos

```bash
# Via linha de comando
python odoo-bin -d seu_banco --addons-path=/path/to/addons -u base

# Ou via interface Odoo:
# 1. Ir para: Aplicações > Atualizar Lista de Aplicações
# 2. Clicar em "Atualizar"
```

### 3. Instalar o Módulo

**Via Interface:**
1. Ir para **Aplicações**
2. Remover filtro "Instalados"
3. Buscar por "Finance Consulting"
4. Clicar em **Instalar**

**Via CLI:**
```bash
python odoo-bin -d seu_banco -i finance_consulting
```

### 4. Configurar Grupos de Usuários

1. Ir para **Configurações > Usuários e Empresas > Usuários**
2. Selecionar usuário
3. Em **Grupos**, adicionar:
   - ✅ `Consultoria Financeira / Consultor`
   - ✅ `Consultoria Financeira / Compliance` (se compliance officer)
   - ✅ `Consultoria Financeira / Gerente` (se gerente)
4. Salvar

---

## 📋 CHECKLIST PÓS-INSTALAÇÃO

- [ ] Módulo aparece no menu principal (ícone de mala)
- [ ] Menu "Consultoria Financeira" com todas as opções
- [ ] Usuário tem acesso ao módulo (verifique grupo)
- [ ] ACL carregado sem erros (verifique logs)
- [ ] Pode criar novo perfil financeiro
- [ ] Pode criar novo suitability
- [ ] Record rules funcionam (vê apenas seus clientes)

---

## 🔍 VERIFICAÇÃO DE INSTALAÇÃO

### Via Python Console

```python
# Acessar console: Configurações > Técnico > Console Python

# Verificar se modelos existem
env['finance.profile'].search([])  # Deve retornar []
env['finance.suitability'].search([])

# Verificar grupos
env['res.groups'].search([('name', 'ilike', 'Consultoria')])

# Verificar ACL
env['ir.model.access'].search([
    ('model_id.model', '=', 'finance.profile')
])
```

### Via Logs

```bash
# Verificar logs para erros de carregamento
tail -f /var/log/odoo/odoo.log | grep finance_consulting

# Deve conter:
# INFO: finance_consulting module loaded
# Sem mensagens de ERROR ou CRITICAL
```

---

## 🚨 TROUBLESHOOTING

### ❌ Erro: "Módulo não aparece em Aplicações"

**Solução:**
1. Verifique se `__manifest__.py` está correto
2. Execute atualização de módulos
3. Limpe cache do navegador (Ctrl+Shift+Delete)
4. Restart do servidor Odoo

```bash
# Restart com atualização
python odoo-bin -d seu_banco -u base
```

---

### ❌ Erro: "Permissão negada" ao criar Perfil

**Causa:** Usuário não está no grupo correto

**Solução:**
1. Ir para **Configurações > Usuários**
2. Abrir usuário problemático
3. Ir para aba **Grupos**
4. Adicionar "Consultoria Financeira / Consultor"
5. Salvar e fazer logout/login

---

### ❌ Erro: "Campo não existe" em View

**Causa:** Campo Python existe mas não em XML, ou XML referencia campo inexistente

**Solução:**
1. Verificar nome do campo em modelo Python
2. Verificar ortografia em XML
3. Campos devem existir antes da view carregar
4. Rodar: `python odoo-bin -d seu_banco -u finance_consulting`

---

### ❌ Erro: "Alocação total deve ser 100%"

**Quando:** Ao criar Investment Plan

**Solução:**
```python
# Verificar cálculo:
fixed_income_percent = 40.0
variable_income_percent = 35.0
reits_percent = 15.0
international_percent = 10.0
pension_percent = 0.0
# Soma = 40 + 35 + 15 + 10 + 0 = 100 ✔️

# Se não bater 100%, ajuste os percentuais
```

---

### ❌ Erro: "Suitability não aparece no Perfil"

**Solução:**
1. Abrir Perfil Financeiro
2. Ir para aba "Suitability"
3. Criar Suitability clicando em "+"
4. Preencher e salvar
5. Voltar ao Perfil - deve aparecer na aba

**Nota:** Mostra a mais recente por data

---

### ❌ Erro: "Model not found: finance.profile"

**Causa:** Módulo não instalado corretamente

**Solução:**
```bash
# Verificar se arquivo __init__.py está correto
cat /path/to/addons/finance_consulting/__init__.py
# Deve conter:
# from . import models

# Verificar se models/__init__.py importa tudo
cat /path/to/addons/finance_consulting/models/__init__.py
```

---

### ❌ Erro: "ACL Error" ao acessar dados

**Causa:** ir.model.access.csv não foi carregado ou inválido

**Solução:**
1. Verificar CSV está bem formatado (sem espaços extras)
2. Rodar instalação novamente:
```bash
python odoo-bin -d seu_banco -u finance_consulting
```
3. Verificar ir.model.access no banco:
```python
env['ir.model.access'].search([])  # Deve listar regras
```

---

### ❌ Erro: "Record rule violation"

**Quando:** Ao tentar editar registro de outro consultor

**Esperado:** Este é o comportamento correto (isolamento de dados)

**Solução:** Se é gerente, adicione grupo:
- "Consultoria Financeira / Gerente"

---

### ❌ Widget não funciona (degraded)

**Exemplos:** statusbar não colorido, float não ajusta

**Solução:**
1. Limpar cache do navegador
2. Fazer logout e login
3. Atualizar página (F5)

**Se persistir:**
```bash
# Limpar cache do servidor
rm -rf ~/.cache/odoo/
python odoo-bin -d seu_banco --cache-ttl=0
```

---

## ✅ TESTES DE VALIDAÇÃO

### Teste 1: Criar Perfil Completo

```python
profile = env['finance.profile'].create({
    'partner_id': 1,
    'advisor_id': env.user.id,
    'net_worth': 500000.0,
    'aum': 250000.0,
    'monthly_income': 10000.0,
    'monthly_expenses': 4000.0,
    'risk_profile': 'moderate',
    'state': 'draft',
})
print(f"✅ Perfil criado: {profile.id}")
profile.action_activate_profile()
print(f"✅ Perfil ativado: {profile.state}")
```

**Esperado:** Ambos prints executam sem erro

---

### Teste 2: Validação de Constraint

```python
# Isso deve falhar (renda negativa)
try:
    env['finance.profile'].create({
        'partner_id': 1,
        'advisor_id': env.user.id,
        'monthly_income': -5000.0,  # ❌ Negativo
    })
except Exception as e:
    print(f"✅ Constraint funcionando: {e}")
```

**Esperado:** Lança exceção de validação

---

### Teste 3: Visibilidade de Dados (Record Rule)

```python
# Usuario A
user_a = env['res.users'].search([('id', '=', 2)])  # ID do outro usuário
with env.as_user(user_a):
    # Deve ver apenas seus perfis
    meus_perfis = env['finance.profile'].search([])
    print(f"✅ User A vê: {len(meus_perfis)} perfis (apenas seus)")

# Manager vê todos
admin = env['res.users'].browse(1)  # Admin
with env.as_user(admin):
    todos = env['finance.profile'].search([])
    print(f"✅ Manager vê: {len(todos)} perfis (todos)")
```

**Esperado:** User A vê menos do que Manager

---

### Teste 4: Mail Thread

```python
profile = env['finance.profile'].browse(1)
profile.action_register_review()

# Verificar se mensagem foi registrada
messages = profile.message_ids
print(f"✅ Mensagens de auditoria: {len(messages)}")
# Deve conter mensagem de revisão
```

**Esperado:** Pelo menos 1 mensagem aparece

---

## 📞 SUPORTE

### Verificar Logs

```bash
# Todos erros do módulo
grep -i finance_consulting /var/log/odoo/odoo.log

# Apenas últimas 50 linhas
tail -50 /var/log/odoo/odoo.log
```

### Debug Python

```python
# Ativar logging detalhado
import logging
logger = logging.getLogger('finance_consulting')
logger.setLevel(logging.DEBUG)

# Agora erros aparecerão nos logs
```

### Reemitir Avisos

Se algo errado aconteceu na instalação:

```bash
# Desinstalar
python odoo-bin -d seu_banco -u --uninstall finance_consulting

# Remover dados
rm -rf /path/to/addons/finance_consulting/.git
# Ou deletar e recopiar módulo

# Reinstalar
python odoo-bin -d seu_banco -i finance_consulting
```

---

## 🎓 TESTES FUNCIONAIS

### Fluxo Completo de Consultoria

1. **Criar Cliente** 
   - Ir para CRM > Clientes
   - Criar novo cliente (res.partner)

2. **Criar Perfil**
   - Consultoria > Clientes > Perfis Financeiros
   - Novo com dados financeiros
   - Ativar

3. **Criar Suitability**
   - Consultoria > Clientes > Suitability
   - Novo para o cliente
   - Aprovar

4. **Criar Plano**
   - Consultoria > Planejamento > Planos
   - Com alocação 100%
   - Ativar

5. **Criar Carteira**
   - Consultoria > Planejamento > Carteiras
   - Com posições reais
   - Verificar rentabilidade

6. **Criar Dossiê**
   - Consultoria > Dossiês
   - Marcar documentação
   - Criar proposta
   - Registrar reunião
   - Fechar sucesso

**Resultado esperado:** Todos passos completam sem erro

---

## 📊 MONITORAMENTO PÓS-INSTALAÇÃO

### Verificar Saúde do Módulo

```bash
# Diariamente, rodar:
grep -c "ERROR" /var/log/odoo/odoo.log
# Deve retornar 0 ou número muito baixo

# Semanal, verificar:
df -h  # Espaço em disco
free -h  # Memória RAM
```

### Performance

```python
# Verificar modelos grandes
len(env['finance.profile'].search([]))  # Número de perfis
len(env['finance.portfolio'].search([]))  # Carteiras

# Se > 10000 registros, considerar índices no BD
```

---

## ✨ PRÓXIMOS PASSOS

1. **Personalizar:** Adapte campos conforme sua necessidade
2. **Relatórios:** Crie relatórios de performance (module reports)
3. **Integração:** Google Calendar, Email
4. **Automações:** Cron jobs customizados
5. **Treinamento:** Treinar usuários em fluxos

---

## 🆘 CONTACT / SUPORTE

Para dúvidas de implementação, verifique:
- `README.md` - Documentação geral
- `ODOO19_COMPLIANCE.md` - Padrões técnicos
- `EXEMPLOS_USO.py` - Exemplos práticos
- Código com comentários detalhados

**Bom trabalho! 🚀**
