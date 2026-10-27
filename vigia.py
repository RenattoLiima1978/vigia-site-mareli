#!/usr/bin/env python3
"""Vigia do site grupomareli.com.br na nuvem (GitHub Actions), para quando o Mac do Renatto estiver desligado.

Confere as páginas principais, o envio das fichas (sem mandar e-mail) e a agenda. Se algo falhar, confere
de novo 1 minuto depois; se continuar, a execução falha e o GitHub avisa o Renatto por e-mail e no app.
Se o site estiver fora do ar, aperta o "Implantar" do Easypanel (segredo GATILHO_DEPLOY) para religar.
"""
import datetime as dt
import json
import os
import sys
import time
import urllib.request

SITE = 'https://www.grupomareli.com.br'
PAGINAS = {
    '/': 'class="cenas"', '/ficha/': 'enviar.php', '/contratacao/': 'enviar.php', '/anadem/ficha/': 'enviar.php',
    '/ficha-sucessao/': 'enviar.php', '/indicacoes/': 'enviar.php', '/agenda/': 'agenda.js', '/dit/': '</html>',
    '/anadem/': '</html>', '/politicas/': '</html>', '/links.html': '</html>',
}


def pede(caminho, dados=None, cab=None):
    req = urllib.request.Request(SITE + caminho, data=dados, headers={'User-Agent': 'vigia-nuvem-mareli', **(cab or {})})
    with urllib.request.urlopen(req, timeout=25) as r:
        return r.status, r.read().decode('utf-8', 'ignore')


def confere():
    fora, problemas = [], []
    for caminho, marca in PAGINAS.items():
        try:
            st, corpo = pede(caminho + ('?v=' + str(int(time.time())) if caminho == '/' else ''))
            if st != 200 or marca not in corpo:
                problemas.append(f'{caminho} abriu errado ({st})')
        except Exception as e:
            fora.append(f'{caminho} fora do ar ({type(e).__name__})')
    try:
        _, corpo = pede('/ficha/enviar.php', b'site_web=vigia', {'Content-Type': 'application/x-www-form-urlencoded'})
        if '"ok":true' not in corpo:
            problemas.append('envio das fichas não responde')
    except Exception as e:
        fora.append(f'envio das fichas fora do ar ({type(e).__name__})')
    try:
        hoje = dt.date.today()
        _, corpo = pede(f'/agenda/api.php?acao=horarios&de={hoje}&ate={hoje + dt.timedelta(days=14)}')
        if not json.loads(corpo).get('ok'):
            problemas.append('agenda não mostra horários')
    except Exception as e:
        problemas.append(f'agenda com erro ({type(e).__name__})')
    return fora, problemas


def religa():
    gatilho = os.environ.get('GATILHO_DEPLOY', '')
    if not gatilho:
        return False
    try:
        urllib.request.urlopen(urllib.request.Request(gatilho, method='POST'), timeout=30)
        return True
    except Exception:
        return False


fora, problemas = confere()
if fora or problemas:
    print('Primeira conferência com problema, confiro de novo em 1 minuto:', '; '.join(fora + problemas))
    time.sleep(60)
    fora, problemas = confere()
if fora:
    ok = religa()
    print('SITE FORA DO AR:', '; '.join(fora))
    print('Apertei o Implantar do Easypanel para religar.' if ok else 'NÃO consegui apertar o Implantar: abra o Easypanel e clique em Implantar.')
if fora or problemas:
    print('PROBLEMA:', '; '.join(fora + problemas))
    sys.exit(1)
print('Tudo ok:', dt.datetime.utcnow().strftime('%d/%m %H:%M UTC'))
