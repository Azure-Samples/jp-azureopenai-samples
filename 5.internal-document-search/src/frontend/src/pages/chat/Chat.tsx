import { useRef, useState, useEffect } from "react";
import { TextField, Panel, DefaultButton } from "@fluentui/react";
import { Dropdown, IDropdownOption } from "@fluentui/react/lib/Dropdown";

import styles from "./Chat.module.css";

import { chatApi, Approaches, ChatResponse, GptChatRequest, GptChatTurn } from "../../api";
import { AnswerChat, AnswerError, AnswerLoading } from "../../components/Answer";
import { QuestionInput } from "../../components/QuestionInput";
import { UserChatMessage } from "../../components/UserChatMessage";
import { SettingsButton } from "../../components/SettingsButton";
import { ClearChatButton } from "../../components/ClearChatButton";

const Chat = () => {
    const [isConfigPanelOpen, setIsConfigPanelOpen] = useState(false);

    const [gptModel, setGptModel] = useState<string>("gpt-3.5-turbo");
    const [systemPrompt, setSystemPrompt] = useState<string>("");
    const [temperature, setTemperature] = useState<string>("0.0");

    const lastQuestionRef = useRef<string>("");
    const chatMessageStreamEnd = useRef<HTMLDivElement | null>(null);

    const [isLoading, setIsLoading] = useState<boolean>(false);
    const [error, setError] = useState<unknown>();

    const [selectedAnswer, setSelectedAnswer] = useState<number>(0);
    const [answers, setAnswers] = useState<[user: string, response: ChatResponse][]>([]);

    const gpt_models: IDropdownOption[] = [
        { key: "gpt-3.5-turbo", text: "gpt-3.5-turbo" },
        { key: "gpt-3.5-turbo-16k", text: "gpt-3.5-turbo-16k" },
        { key: "gpt-4", text: "gpt-4" },
        { key: "gpt-4-32k", text: "gpt-4-32k" }
    ];

    const temperatures: IDropdownOption[] = Array.from({ length: 11 }, (_, i) => ({ key: (i / 10).toFixed(1), text: (i / 10).toFixed(1) }));

    const makeApiRequest = async (question: string) => {
        lastQuestionRef.current = question;

        error && setError(undefined);
        setIsLoading(true);

        try {
            const history: GptChatTurn[] = answers.map(a => ({ user: a[0], assistant: a[1].answer }));
            const request: GptChatRequest = {
                history: [...history, { user: question, assistant: undefined }],
                approach: Approaches.Read,
                overrides: {
                    gptModel: gptModel,
                    temperature: temperature,
                    systemPrompt: systemPrompt
                }
            };
            const result = await chatApi(request);
            setAnswers([...answers, [question, result]]);
        } catch (e) {
            setError(e);
        } finally {
            setIsLoading(false);
        }
    };

    const clearChat = () => {
        lastQuestionRef.current = "";
        error && setError(undefined);
        setAnswers([]);
    };

    useEffect(() => chatMessageStreamEnd.current?.scrollIntoView({ behavior: "smooth" }), [isLoading]);

    const onGptModelChange = (_ev?: React.FormEvent<HTMLDivElement>, option?: IDropdownOption) => {
        if (option !== undefined) {
            setGptModel(option.key as string);
        }
    };

    const onSystemPromptChange = (_ev?: React.SyntheticEvent<HTMLElement, Event>, newValue?: string) => {
        setSystemPrompt(newValue || "");
    };

    const onTempertureChange = (_ev?: React.FormEvent<HTMLDivElement>, option?: IDropdownOption) => {
        if (option !== undefined) {
            setTemperature(option.key as string);
        }
    };

    return (
        <div className={styles.container}>
            <div className={styles.commandsContainer}>
                <ClearChatButton className={styles.commandButton} onClick={clearChat} disabled={!lastQuestionRef.current || isLoading} />
                <SettingsButton className={styles.commandButton} onClick={() => setIsConfigPanelOpen(!isConfigPanelOpen)} />
            </div>
            <div className={styles.chatRoot}>
                <div className={styles.chatContainer}>
                    <div className={styles.chatMessageStream}>
                        {answers.map((answer, index) => (
                            <div key={index}>
                                <UserChatMessage message={answer[0]} />
                                <div className={styles.chatMessageGpt}>
                                    <AnswerChat key={index} answer={answer[1]} isSelected={selectedAnswer === index} />
                                </div>
                            </div>
                        ))}
                        {isLoading && (
                            <>
                                <UserChatMessage message={lastQuestionRef.current} />
                                <div className={styles.chatMessageGptMinWidth}>
                                    <AnswerLoading />
                                </div>
                            </>
                        )}
                        {error ? (
                            <>
                                <UserChatMessage message={lastQuestionRef.current} />
                                <div className={styles.chatMessageGptMinWidth}>
                                    <AnswerError error={error.toString()} onRetry={() => makeApiRequest(lastQuestionRef.current)} />
                                </div>
                            </>
                        ) : null}
                        <div ref={chatMessageStreamEnd} />
                    </div>

                    <div className={styles.chatInput}>
                        <QuestionInput
                            clearOnSend
                            placeholder="企業内向けChatGPTと会話を始めましょう。（例：ChatGPTについて教えて下さい）"
                            disabled={isLoading}
                            onSend={question => makeApiRequest(question)}
                        />
                    </div>
                </div>
                <Panel
                    headerText="Configure GPT settings"
                    isOpen={isConfigPanelOpen}
                    isBlocking={false}
                    onDismiss={() => setIsConfigPanelOpen(false)}
                    closeButtonAriaLabel="Close"
                    onRenderFooterContent={() => <DefaultButton onClick={() => setIsConfigPanelOpen(false)}>Close</DefaultButton>}
                    isFooterAtBottom={true}
                >
                    <Dropdown
                        className={styles.chatSettingsSeparator}
                        defaultSelectedKeys={[gptModel]}
                        selectedKey={gptModel}
                        label="GPT Model:"
                        options={gpt_models}
                        onChange={onGptModelChange}
                    />
                    <TextField
                        className={styles.chatSettingsSeparator}
                        value={systemPrompt}
                        label="System Prompt:"
                        multiline
                        autoAdjustHeight
                        onChange={onSystemPromptChange}
                    />
                    <Dropdown
                        className={styles.chatSettingsSeparator}
                        defaultSelectedKeys={[temperature]}
                        selectedKey={temperature}
                        label="Temperature:"
                        options={temperatures}
                        onChange={onTempertureChange}
                    />
                </Panel>
            </div>
        </div>
    );
};

export default Chat;
