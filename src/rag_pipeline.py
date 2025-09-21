import os
import logging
from dotenv import load_dotenv
from src.utils import load_yaml_config
from src.prompt_builder import build_prompt_from_config
from langchain_groq import ChatGroq
from src.paths import APP_CONFIG_FPATH, PROMPT_CONFIG_FPATH, OUTPUTS_DIR
from src.ingest import get_db_collection, embed_documents
from src.prompt_builder import build_system_prompt_from_config
from src.utils import load_publication  # to include publication content in system prompt if desired


logger = logging.getLogger()

def setup_logging():
    if not logger.handlers:  # prevent duplicate handlers
        logger.setLevel(logging.INFO)
        file_handler = logging.FileHandler(os.path.join(OUTPUTS_DIR, "rag_assistant.log"))
        file_handler.setLevel(logging.INFO)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

# Load environment variables
load_dotenv()
os.environ["TOKENIZERS_PARALLELISM"] = "false"

# Load vector DB
collection = get_db_collection(collection_name="publications")

def retrieve_relevant_documents(
    query: str,
    n_results: int = 5,
    threshold: float = 0.3,
):
    logging.info(f"Retrieving relevant documents for query: {query}")

    relevant_results = {"ids": [], "documents": [], "distances": []}

    logging.info("Embedding query...")
    query_embedding = embed_documents([query])[0]

    logging.info("Querying collection...")
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results,
        include=["documents", "distances"],
    )

    logging.info("Filtering results...")
    for i, distance in enumerate(results["distances"][0]):
        if distance < threshold:
            relevant_results["ids"].append(results["ids"][0][i])
            relevant_results["documents"].append(results["documents"][0][i])
            relevant_results["distances"].append(distance)

    return relevant_results["documents"]


def respond_to_query(
    prompt_spec: dict,
    query: str,
    llm: str,
    app_config: dict,
    n_results: int = 5,
    threshold: float = 0.3,
):
    # Get relevant documents
    relevant_documents = retrieve_relevant_documents(query, n_results=n_results, threshold=threshold)

    # Build the input_data from retrieved documents (join with separators)
    input_data = "\n\n---\n\n".join(relevant_documents)

    # Build system prompt (use advanced or basic as you like)
    # Example: use the advanced system prompt from your prompt YAML
    system_prompt_spec = prompt_spec.get("system_prompt_spec")  # optional: if you pass it in
    # Or load directly from your prompt YAML in main and pass it down

    # If you have the publication content and want it in the system prompt:
    try:
        publication_text = load_publication()
    except Exception:
        publication_text = ""

    system_prompt = build_system_prompt_from_config(
        app_config.get("system_prompt", {}), publication_content=publication_text
    ) if app_config.get("system_prompt") else ""

    # Build the task/user prompt from the prompt spec (pass app_config for reasoning)
    task_prompt = build_prompt_from_config(prompt_spec, input_data=input_data, app_config=app_config)

    # Optionally preview the prompt while debugging
    # print_prompt_preview(system_prompt + "\n\n" + task_prompt)

    final_prompt = (system_prompt + "\n\n" + task_prompt).strip() if system_prompt else task_prompt

    # Call the LLM
    llm_client = ChatGroq(model=llm)
    response = llm_client.invoke(final_prompt)
    return response.content


if __name__ == "__main__":
    setup_logging()
    app_config = load_yaml_config(APP_CONFIG_FPATH)
    prompt_config = load_yaml_config(PROMPT_CONFIG_FPATH)

    vectordb_params = app_config["vectordb"]
    llm = app_config["llm"]

    exit_app = False
    while not exit_app:
        query = input(
            "Enter a question, 'config' to change parameters, or 'exit' to quit: "
        )

        if query.lower() == "exit":
            exit_app = True
            break

        elif query.lower() == "config":
            threshold = float(input("Enter the retrieval threshold: "))
            n_results = int(input("Enter the Top K value: "))
            vectordb_params = {"threshold": threshold, "n_results": n_results}
            continue

        response = respond_to_query(
            prompt_spec=prompt_config["rag_assistant_prompt"],  # 👈 fix here
            query=query,
            llm=llm,
            app_config=app_config,       # ✅ required, missing in your call
            **vectordb_params,
        )

        logging.info("-" * 100)
        logging.info("LLM response:")
        logging.info(response + "\n\n")
