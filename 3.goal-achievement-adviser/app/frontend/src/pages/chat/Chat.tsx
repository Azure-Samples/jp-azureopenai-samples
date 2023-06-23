import { useRef, useState, useEffect } from "react";
import { Checkbox, Panel, DefaultButton, TextField, SpinButton, COACHMARK_ATTRIBUTE_NAME, TextFieldBase } from "@fluentui/react";
import { SparkleFilled } from "@fluentui/react-icons";

import styles from "./Chat.module.css";
import { AnswerIcon } from "../../components/Answer/AnswerIcon";

import { chatApi, ChatResponse, ChatRequest, Prompt, Step, ChatAnswer } from "../../api";
import { Answer, AnswerError, AnswerLoading } from "../../components/Answer";
import { QuestionInput } from "../../components/QuestionInput";
import { ExampleList } from "../../components/Example";
import { UserChatMessage } from "../../components/UserChatMessage";
import { AnalysisPanel, AnalysisPanelTabs } from "../../components/AnalysisPanel";
// import { SettingsButton } from "../../components/SettingsButton";
// import { ClearChatButton } from "../../components/ClearChatButton";

const Chat = () => {
    // const [isConfigPanelOpen, setIsConfigPanelOpen] = useState(false);
    // const [promptTemplate, setPromptTemplate] = useState<string>("");
    // const [retrieveCount, setRetrieveCount] = useState<number>(3);
    // const [useSemanticRanker, setUseSemanticRanker] = useState<boolean>(true);
    // const [useSemanticCaptions, setUseSemanticCaptions] = useState<boolean>(false);
    // const [excludeCategory, setExcludeCategory] = useState<string>("");
    const [useSuggestFollowupQuestions, setUseSuggestFollowupQuestions] = useState<boolean>(false);

    const lastQuestionRef = useRef<string>("");
    const themeRef = useRef<string>("");
    // const chatMessageStreamEnd = useRef<HTMLDivElement | null>(null);

    const [isLoading, setIsLoading] = useState<boolean>(false);
    const [error, setError] = useState<unknown>();

    const [activeCitation, setActiveCitation] = useState<string>();
    const [activeAnalysisPanelTab, setActiveAnalysisPanelTab] = useState<AnalysisPanelTabs | undefined>(undefined);

    const [selectedAnswer, setSelectedAnswer] = useState<number>(0);

    const [history, setHistory] = useState<Prompt[]>([]);
    const [answers, setAnswers] = useState<ChatAnswer[]>([]);
    const [support, setSupport] = useState<string>("");
    const [search, setSearch] = useState<number>(0);

    const [chatResponse, setChatResponse] = useState<ChatResponse>();

    const [company_name, setCompanyName] = useState<string | undefined>("");

    const [clearOnSend, setClearOnSend] = useState<boolean>(true);

    const [question, setQuestion] = useState<string>("");

    const sendQuestion = (question: string) => {
        makeApiRequest(question);

        if (clearOnSend) {
            setQuestion("");
            setSupport("");
        }
    };

    const makeApiRequest = async (question: string) => {
        if (!themeRef.current) themeRef.current = question;

        lastQuestionRef.current = question;

        error && setError(undefined);
        setIsLoading(true);
        setActiveCitation(undefined);
        setActiveAnalysisPanelTab(undefined);

        // let historyToSend = history.slice();

        if (answers.length > 0) {
            // replace the last prompt with full json data { headers : [], steps [{},{},{}], answer : "" }
            // let assistantPromptToSend: Prompt = { role: "assistant", content: encodeURIComponent(JSON.stringify(chatResponse)) };
            // historyToSend[historyToSend.length - 1] = assistantPromptToSend;

            const newChatUserTurn: Prompt = { role: "user", content: question };
            history.push(newChatUserTurn);

            // let assistantPromptToSend: Prompt = { role: "assistant", content: encodeURIComponent(JSON.stringify(chatResponse)) };
            // historyToSend.push(assistantPromptToSend);
            // historyToSend.push(newChatUserTurn);
        }

        const request: ChatRequest = {
            theme: themeRef.current,
            history: history,
            search: search
            // history: historyToSend
        };
        chatApi(request)
            .then(result => {
                // { type: "json", value: "encoded data" }
                const jsonResult = JSON.parse(result);

                if (jsonResult.type === "json") {
                    // { headers : [], steps [{},{},{}], answer : "" }
                    let responseData: string = decodeURIComponent(jsonResult.value);
                    const chatResponse: ChatResponse = JSON.parse(responseData);

                    const answer: ChatAnswer = { user: question, assistant: chatResponse.answer };
                    answers.unshift(answer);
                    setAnswers(answers);
                    setSupport(chatResponse.support);
                    setChatResponse(chatResponse);

                    const newChatBotTurn: Prompt = { role: "assistant", content: jsonResult.value };
                    history.push(newChatBotTurn);
                } else if (jsonResult.type === "html") {
                    const sas_url = decodeURIComponent(jsonResult.value);
                    window.open(sas_url, "_blank", "popup");
                } else if (jsonResult.type === "text") {
                    let responseData: string = decodeURIComponent(jsonResult.value);

                    const answer: ChatAnswer = { user: question, assistant: responseData };
                    answers.unshift(answer);
                    setAnswers(answers);

                    const newChatBotTurn: Prompt = { role: "assistant", content: jsonResult.value };
                    history.push(newChatBotTurn);
                }
            })
            .catch(error => {
                setError(error);
            })
            .then(() => {
                setIsLoading(false);
            });
    };

    const onQuestionChange = (newValue?: string) => {
        if (!newValue) {
            setQuestion("");
        } else if (newValue.length <= 1000) {
            setQuestion(newValue);
        }
    };

    // useEffect(() => chatMessageStreamEnd.current?.scrollIntoView({ behavior: "smooth" }), [isLoading]);

    const onUseSuggestFollowupQuestionsChange = (_ev?: React.FormEvent<HTMLElement | HTMLInputElement>, checked?: boolean) => {
        setUseSuggestFollowupQuestions(!!checked);
    };

    const onExampleClicked = (example: string, search: number) => {
        // makeApiRequest(example);
        setSearch(search);
        setQuestion(example);
    };

    const onShowCitation = (citation: string, index: number) => {
        if (activeCitation === citation && activeAnalysisPanelTab === AnalysisPanelTabs.CitationTab && selectedAnswer === index) {
            setActiveAnalysisPanelTab(undefined);
        } else {
            setActiveCitation(citation);
            setActiveAnalysisPanelTab(AnalysisPanelTabs.CitationTab);
        }

        setSelectedAnswer(index);
    };

    const onToggleTab = (tab: AnalysisPanelTabs, index: number) => {
        if (activeAnalysisPanelTab === tab && selectedAnswer === index) {
            setActiveAnalysisPanelTab(undefined);
        } else {
            setActiveAnalysisPanelTab(tab);
        }

        setSelectedAnswer(index);
    };

    const onHandleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        setCompanyName(e.target.value);
    };

    return (
        <div className={styles.container}>
            <div className={styles.chatRoot}>
                <div className={styles.chatContainer}>
                    {!lastQuestionRef.current ? (
                        <div className={styles.chatEmptyState}>
                            <SparkleFilled fontSize={"80px"} primaryFill={"rgba(115, 118, 225, 1)"} aria-hidden="true" aria-label="Chat logo" />
                            <h3 className={styles.chatEmptyStateTitle}>目標を入力してください</h3>
                        </div>
                    ) : (
                        <></>
                    )}
                    <div className={styles.chatInput}>
                        <QuestionInput
                            clearOnSend={clearOnSend}
                            placeholder=""
                            disabled={isLoading}
                            question={question}
                            onSend={question => sendQuestion(question)}
                            onChange={newValue => onQuestionChange(newValue)}
                        />
                    </div>
                    {!lastQuestionRef.current ? (
                        <div className={styles.chatEmptyState}>
                            <ExampleList onExampleClicked={onExampleClicked} />
                        </div>
                    ) : (
                        <div className={styles.chatMessageStream}>
                            {support && (
                                // <table className={styles.hintTable}>
                                //     <thead>
                                //         <tr>
                                //             <th className={styles.supportTableColumnHint}>
                                //                 <div className={styles.chatMessageGpt}>
                                //                     <AnswerIcon />
                                //                     サポート
                                //                 </div>
                                //             </th>
                                //             <th className={styles.supportTableColumnContent}>
                                //                 <div className={styles.chatMessageGpt}>{support}</div>
                                //             </th>
                                //         </tr>
                                //     </thead>
                                // </table>
                                // <div className={styles.hintDisplayArea}>
                                //     <span className={styles.supportHintIcon}>
                                //         <AnswerIcon />
                                //         サポート
                                //     </span>
                                //     <span className={styles.supportHintContent}>{support}</span>
                                // </div>
                                <table className={styles.hintDisplayTable}>
                                    <tbody>
                                        <tr>
                                            <td className={styles.supportHintIcon}>
                                                <AnswerIcon />
                                                サポート
                                            </td>
                                            <td className={styles.supportHintContent}>{support}</td>
                                        </tr>
                                    </tbody>
                                </table>
                            )}
                            {isLoading && (
                                <>
                                    <div className={styles.chatMessageGptMinWidth}>
                                        <AnswerLoading />
                                    </div>
                                    <UserChatMessage message={lastQuestionRef.current} />
                                </>
                            )}
                            {error ? (
                                <>
                                    <div className={styles.chatMessageGptMinWidth}>
                                        <AnswerError error={error.toString()} onRetry={() => makeApiRequest(lastQuestionRef.current)} />
                                    </div>
                                    <UserChatMessage message={lastQuestionRef.current} />
                                </>
                            ) : null}
                            {answers.map((answer, index) => (
                                <div key={index}>
                                    <div className={styles.chatMessageGpt}>
                                        <Answer
                                            key={index}
                                            answer={answer.assistant}
                                            isSelected={selectedAnswer === index && activeAnalysisPanelTab !== undefined}
                                            onCitationClicked={c => onShowCitation(c, index)}
                                            // onThoughtProcessClicked={() => onToggleTab(AnalysisPanelTabs.ThoughtProcessTab, index)}
                                            // onSupportingContentClicked={() => onToggleTab(AnalysisPanelTabs.SupportingContentTab, index)}
                                            // onFollowupQuestionClicked={q => makeApiRequest(q)}
                                            // showFollowupQuestions={useSuggestFollowupQuestions && answers.length - 1 === index}
                                        />
                                    </div>
                                    <UserChatMessage message={answer.user} />
                                </div>
                            ))}
                            {/* {answers.map((answer, index) => (
                                <div key={index}>
                                    <div className={styles.chatMessageGpt}>
                                        <UserChatMessage message={answer.user} />
                                        <Answer
                                            key={index}
                                            answer={answer.assistant}
                                            isSelected={selectedAnswer === index && activeAnalysisPanelTab !== undefined}
                                            onCitationClicked={c => onShowCitation(c, index)}
                                        />
                                    </div>
                                </div>
                            ))} */}
                            {/* <div ref={chatMessageStreamEnd} /> */}
                        </div>
                    )}
                </div>
                {chatResponse && <AnalysisPanel className={styles.chatAnalysisPanel} response={chatResponse} />}
            </div>
        </div>
    );
};

export default Chat;
