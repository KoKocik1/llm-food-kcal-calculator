def get_formatted_response(generated_response):
    """Format the response with sources."""
    sources = set(
        doc.metadata["source"] for doc in generated_response["source_documents"]
    )
    response_text = generated_response["result"]
    response_text += "\n\nSources:\n"

    sources = sorted(sources)
    return (response_text, sources)
