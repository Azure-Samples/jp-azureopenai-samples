import { ChatRequest } from "./models";

export async function chatApi(options: ChatRequest): Promise<string> {
    const response = await fetch("/chat", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            theme: options.theme,
            history: options.history,
            search: options.search
        })
    });

    // const parsedResponse: AskResponse = await response.json();
    const parsedResponse: string = await response.text();
    if (response.status > 299 || !response.ok) {
        throw Error(response.statusText || "Unknown error");
    }

    return parsedResponse;
}

export function getCitationFilePath(citation: string): string {
    return `/content/${citation}`;
}
