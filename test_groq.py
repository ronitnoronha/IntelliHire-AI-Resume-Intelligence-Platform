"""Manual Groq connectivity check; intentionally excluded from unit tests."""


def main():
    from ai.llm import MODEL, get_client

    client = get_client()
    if client is None:
        raise SystemExit("Set GROQ_API_KEY in .env before running this check.")

    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": "Say hello in exactly five words."}],
    )
    print(response.choices[0].message.content)


if __name__ == "__main__":
    main()
