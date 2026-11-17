# Fantasy Bot RPG — protótipo simples

## O que já faz
- Uma sala compartilhada por link.
- Várias pessoas podem enviar mensagens pelo navegador.
- O Gemini responde como Mestre e recebe o histórico recente da campanha.
- Interface adaptada para celular.

## Arquivos
- `app.py`: servidor Python + integração Gemini.
- `templates/index.html`: chat.
- `requirements.txt`: dependências.

## Configuração local
1. Instale as dependências: `pip install -r requirements.txt`
2. Defina a variável de ambiente `GEMINI_API_KEY` com sua chave.
3. Execute: `python app.py`
4. Abra `http://127.0.0.1:5000`.

Acesso local só funciona no mesmo aparelho. Para amigos entrarem de outros lugares,
publique o projeto em um serviço de hospedagem.

## Publicação no Render
- Crie um repositório GitHub e envie estes arquivos.
- No Render, crie um Web Service conectado ao repositório.
- Build command: `pip install -r requirements.txt`
- Start command: `gunicorn app:app`
- Adicione a variável de ambiente `GEMINI_API_KEY` com sua chave.
- Use o endereço público gerado pelo Render para convidar os amigos.

## Limitações deste protótipo
- Não há contas nem senha: qualquer pessoa com o link pode participar.
- O histórico fica na memória do servidor e pode ser perdido quando o serviço reiniciar.
- O plano gratuito do Render pode dormir por inatividade; a primeira abertura depois disso pode demorar.
- O uso da API Gemini pode estar sujeito a limites e custos do seu plano.
- Não coloque a chave Gemini no código do navegador, em prints ou em repositórios.
