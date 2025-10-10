import os

URLS = dict(
    trf1=dict(
        pje1g='https://pje1g.trf1.jus.br',
        pje2g='https://pje2g.trf1.jus.br',
    ),
    trf3=dict(
        pje1g='https://pje1g.trf3.jus.br',
        pje2g='https://pje2g.trf3.jus.br',
    ),
    trf5=dict(
        pje1g='https://pje1g.trf5.jus.br',
        pje2g='https://pje2g.trf5.jus.br',
    ),
    trf6=dict(
        pje1g='https://pje1g.trf6.jus.br',
        pje2g='https://pje2g.trf6.jus.br',
    )
)
QUERY_TIMEOUT = int(os.getenv('QUERY_TIMEOUT', '50'))