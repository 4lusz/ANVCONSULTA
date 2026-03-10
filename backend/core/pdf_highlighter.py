import os
import fitz  # PyMuPDF
import unicodedata
import re


def remover_acentos(texto: str) -> str:
    return "".join(
        c for c in unicodedata.normalize("NFKD", texto)
        if not unicodedata.combining(c)
    )


def normalizar(texto: str) -> str:
    if not texto:
        return ""
    texto = texto.lower()
    texto = remover_acentos(texto)
    return texto


def destacar_keywords_pdf(
    pdf_path: str,
    termos: list[str],
    suffix: str | None = None,
    output_dir: str | None = None
) -> str | None:
    """
    Cria uma copia do PDF com as EXPRESSÕES destacadas.
    Cada item de `termos` é tratado como uma expressão única.
    """

    if not pdf_path or not os.path.isfile(pdf_path):
        return None

    if not termos:
        return None

    try:
        doc = fitz.open(pdf_path)
        total_marcas = 0

        # normaliza expressões uma única vez
        expressoes = [
            (normalizar(t), t)
            for t in termos
            if t.strip()
        ]

        for page in doc:
            texto_pagina = page.get_text()
            texto_pagina_norm = normalizar(texto_pagina)

            for expressao_norm, expressao_raw in expressoes:
                palavras = expressao_norm.split()

                # 🔹 REGRA 1: palavra única e curta → palavra isolada
                if len(palavras) == 1 and len(palavras[0]) <= 5:
                    padrao = rf"\b{re.escape(palavras[0])}\b"
                    matches = list(re.finditer(padrao, texto_pagina_norm))
                else:
                    # 🔹 REGRA 2: expressão longa → substring normal
                    if expressao_norm not in texto_pagina_norm:
                        continue
                    matches = list(
                        re.finditer(re.escape(expressao_norm), texto_pagina_norm)
                    )

                for match in matches:
                    inicio, fim = match.start(), match.end()
                    trecho_original = texto_pagina[inicio:fim]

                    areas = page.search_for(
                        trecho_original,
                        flags=fitz.TEXT_DEHYPHENATE
                    )

                    for area in areas:
                        highlight = page.add_highlight_annot(area)
                        highlight.update()
                        total_marcas += 1

        if total_marcas == 0:
            doc.close()
            return None

        base_dir = output_dir or os.path.dirname(pdf_path)
        os.makedirs(base_dir, exist_ok=True)

        nome_base = os.path.splitext(os.path.basename(pdf_path))[0]

        if suffix:
            highlighted_path = os.path.join(
                base_dir,
                f"{nome_base}_{suffix}_highlight.pdf"
            )
        else:
            highlighted_path = os.path.join(
                base_dir,
                f"{nome_base}_highlight.pdf"
            )

        doc.save(highlighted_path)
        doc.close()

        return highlighted_path

    except Exception as e:
        print("[WARN] Falha ao destacar keywords no PDF")
        print(e)
        return None
