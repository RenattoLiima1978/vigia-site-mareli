# Vigia do site Grupo Mareli (na nuvem)

Confere o site **grupomareli.com.br** a cada 5 minutos pelo GitHub Actions, mesmo com o Mac desligado:
páginas principais, envio das fichas (sem mandar e-mail) e agenda.

- Se algo falhar duas vezes seguidas (com 1 minuto de intervalo), a execução fica vermelha e o GitHub avisa por e-mail e no app.
- Se o site estiver fora do ar, o vigia aperta sozinho o "Implantar" do Easypanel para religar.
- Uma vez por mês o vigia grava `ultimo-mes.txt`, para o GitHub não pausar a verificação automática.

O vigia do Mac (`6-ferramentas/monitor_site.py`) continua: ele confere também o e-mail das fichas e o iCloud.
