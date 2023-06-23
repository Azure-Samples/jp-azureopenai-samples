import { Example } from "./Example";

import styles from "./Example.module.css";

export type ExampleModel = {
    text: string;
    value: string;
    search: number;
    image: string;
};

import sample01 from "../../assets/sample01.png";
import sample02 from "../../assets/sample02.png";
import sample03 from "../../assets/sample03.png";

const EXAMPLES: ExampleModel[] = [
    {
        text: "商品企画書の作成支援",
        value: "私は家電メーカーのコントソ株式会社の商品企画担当者です。調理家電を担当しています。自社の強みを活かし、かつ既存の顧客にもっと多くの製品を買ってもらうための商品のアイディアを出したいです。",
        search: 1,
        image: sample01
    },
    {
        text: "パーソナルトレーニング",
        value: "私はスポーツジムのトレーナーです。お客様の現在の状態と目標とスケジュールを話し合い、目標を達成するためのトレーニングメニューを作成したいです。",
        search: 0,
        image: sample02
    },
    {
        text: "キャリアアドバイザー",
        value: "私は転職エージェントです。転職希望者の今までのキャリアをヒアリングして、出来るだけ希望に近い業種、転職先候補および必要なスキル開発計画を提案したいです。",
        search: 1,
        image: sample03
    }
];

// const EXAMPLES: ExampleModel[] = [
//     {
//         text: "新規ブランド立ち上げ",
//         value: "新ブランドによる新たな顧客層の開拓とグループ全体のイメージ向上を図りたい"
//     },
//     {
//         text: "人材確保の課題",
//         value: "現在人材不足に悩まされています。経済成長やグローバル競争の激化により、優秀な人材を採用することがますます困難になっています。特にIT分野の競争が激しいため、優秀なエンジニアやデータサイエンティストを採用することが難しくデジタルトランスフォーメーションに取り組めていません。"
//     },
//     {
//         text: "新規事業による収益改善",
//         value: "会社が経営が悪化しているので新規事業を立てて新たな収益の柱にするためのアイデアを社内で検討したい。"
//     }
// ];

interface Props {
    onExampleClicked: (value: string, search: number) => void;
}

export const ExampleList = ({ onExampleClicked }: Props) => {
    return (
        <ul className={styles.examplesNavList}>
            {EXAMPLES.map((x, i) => (
                <li key={i}>
                    <Example text={x.text} value={x.value} image={x.image} search={x.search} onClick={onExampleClicked} />
                </li>
            ))}
        </ul>
    );
};
