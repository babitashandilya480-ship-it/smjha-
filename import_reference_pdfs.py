"""Index the user's supplied PDFs once, retaining file-page attribution."""
import hashlib
import json
from pathlib import Path
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
SOURCES = [
    ('evaluation', '927eb952.pdf', 'LLM Testing and Evaluation'),
    ('astra-summary', 'GPT-6-Astra-System-Card-Summary.pdf', 'GPT-6 Astra — System Card Summary'),
    ('frontier-building', 'How-Frontier-LLMs-Are-Built.pdf', 'How Frontier LLMs Are Built'),
    ('agent-prompting', 'LLMs_and_GPT6_Astra_Agent_Prompting.pdf', 'Understanding LLMs & Building an Astra-Style Agent'),
    ('model-research-evaluation', 'model_research_evaluation_questions.pdf', 'Model Research & Evaluation Questions'),
]

def main():
    documents = []
    for key, filename, title in SOURCES:
        path = Path.home() / 'Downloads' / filename
        reader = PdfReader(path)
        pages = [{'pdf_page': i+1, 'text': page.extract_text().strip()}
                 for i, page in enumerate(reader.pages)]
        # The prompting guide has an inspected, genuinely blank second page.
        # Retain its position so later citations stay PDF pages 3, 4 and 5.
        if any(not p['text'] and not (key=='agent-prompting' and p['pdf_page']==2) for p in pages):
            raise ValueError(f'{filename}: a page needs OCR')
        source_digest = hashlib.sha256(path.read_bytes()).hexdigest()
        # Keep the first reference idempotent with the earlier single-guide import.
        digest = hashlib.sha256((ROOT / 'data/reference-guide.json').read_bytes()).hexdigest() if key == 'evaluation' else source_digest
        documents.append({'key': key, 'filename': filename, 'title': title,
                          'digest': digest, 'source_digest': source_digest,
                          'pages': pages})
        print(f'{filename}: {len(pages)} pages indexed')
    (ROOT / 'data' / 'supplied-references.json').write_text(
        json.dumps(documents, ensure_ascii=False, indent=2), encoding='utf-8')

if __name__ == '__main__':
    main()
