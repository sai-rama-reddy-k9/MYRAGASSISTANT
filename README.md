# RAG Project: Privacy and Security Threats in Agentic AI Systems

## Overview
This project demonstrates a Retrieval-Augmented Generation (RAG) pipeline designed to analyze and summarize publications related to **privacy and security threats in Agentic AI systems**. The assistant highlights current risks, mitigation strategies, and research trends while ensuring safe and secure retrieval.

## Features
- Ingests and indexes research publications in the `data/` directory.
- Uses RAG to generate concise, context-aware summaries and threat analyses.
- Enforces privacy and security by refusing irrelevant queries or hallucinations.
- Supports querying for:
  - Threat vectors  
  - Mitigation techniques  
  - Case studies and compliance issues  

## Project Domain
The knowledge base is focused on **academic and technical publications** in the field of **Agentic AI privacy and security**.  
This assistant is not optimized for general-purpose Q&A or unrelated document types.

## Getting Started

1. **Clone the repository**

```bash
git clone https://github.com/sai-rama-reddy-k9/MYRAGASSISTANT/blob/main/README.md
cd MyRagAssistant
```

2. **Install dependencies**

```bash
pip install -r requirements.txt
```

3. **Ingest data**

```bash
python -m src.ingest
```

4. **Run the application**

```bash
python -m src.main
```

## Usage

- Place new PDF or text publications in the `data/` folder.  
- Run `src.ingest` to update the knowledge base.  
- Start the assistant and ask queries, for example:

> How do RAG systems handle GDPR compliance?  
> What are common security risks in agentic AI pipelines?

---

## Example Queries

- What privacy risks are highlighted in recent research?  
- How can encryption help in secure RAG applications?  
- What compliance frameworks apply to agentic AI systems?  

---

## Evaluation

- Document chunking with overlap ensures context preservation.  
- Retrieval performance is measured using qualitative analysis and query accuracy.  

---

## Contributing

Contributions are welcome!  

- Open an issue for bug reports or feature requests.  
- Submit a pull request for improvements.  

---

## License

This project is licensed under the [MIT License](LICENSE).  
See the LICENSE file for details.  
