"""Gera configuração local sem imprimir ou sobrescrever segredos existentes."""
from pathlib import Path
import secrets

root = Path(__file__).resolve().parent.parent
target = root / '.env'
if target.exists():
    print('O arquivo .env já existe e foi preservado.')
else:
    content = (root / '.env.example').read_text(encoding='utf-8')
    content = content.replace('DJANGO_SECRET_KEY=gere-com-o-script-configurar', f'DJANGO_SECRET_KEY={secrets.token_urlsafe(48)}')
    content = content.replace('POSTGRES_PASSWORD=gere-com-o-script-configurar', f'POSTGRES_PASSWORD={secrets.token_urlsafe(32)}')
    with target.open('x', encoding='utf-8') as output:
        output.write(content)
    print('Configuração local criada. Segredos não são exibidos nem incluídos no ZIP.')
