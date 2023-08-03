import { Example } from "./Example";

import styles from "./Example.module.css";

export type ExampleModel = {
    text: string;
    value: string;
};

const EXAMPLES: ExampleModel[] = [
    {
        text: "就業規則とは何ですか？",
        value: "就業規則とは何ですか？"
    },
    { text: "人事はどのような仕事をしますか？", value: "人事はどのような仕事をしますか？" },
    { text: "休暇にはどんな種類がありますか？", value: "休暇にはどんな種類がありますか？" }
];

interface Props {
    onExampleClicked: (value: string) => void;
}

export const ExampleList = ({ onExampleClicked }: Props) => {
    return (
        <ul className={styles.examplesNavList}>
            {EXAMPLES.map((x, i) => (
                <li key={i}>
                    <Example text={x.text} value={x.value} onClick={onExampleClicked} />
                </li>
            ))}
        </ul>
    );
};
