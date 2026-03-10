# ANVCONSULTA

Sistema automatizado de monitoramento do Diário Oficial da União (DOU) focado em atos relacionados à ANVISA.

O sistema coleta publicações do DOU, processa os PDFs, identifica expressões configuradas pelo usuário e envia alertas automáticos por email com resumo gerado por IA.

## Funcionalidades

- Monitoramento automatizado do Diário Oficial da União
- Conversão de PDFs em texto processável
- Filtragem por expressões configuráveis
- Geração de alertas automáticos por email
- Destaque das expressões encontradas no PDF
- Deduplicação de alertas
- Resumo automático dos atos utilizando IA
- Execução contínua como serviço (systemd)

## Tecnologias

- Python
- PyMuPDF
- Automação de processamento de texto
- Integração com IA
- Linux / systemd

## Estrutura do projeto

