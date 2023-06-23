export type Step = {
    step_num: number;
    content: string;
    variable_name: string;
    value: string;
};

export type Prompt = {
    role: string;
    content: string;
};

export type ChatRequest = {
    theme: string;
    history: Prompt[];
    search: number;
};

export type ChatResponse = {
    answer: string;
    headers: string[];
    steps: Step[];
    support: string;
    error?: string;
};

export type ChatAnswer = {
    user: string;
    assistant: string;
};

export type Claim = {
    typ: string;
    val: string;
};

export type AccessToken = {
    access_token: string;
    expires_on: string;
    id_token: string;
    provider_name: string;
    user_claims: Claim[];
    user_id: string;
};
