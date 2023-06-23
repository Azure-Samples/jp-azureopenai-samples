import styles from "./Example.module.css";

interface Props {
    text: string;
    value: string;
    search: number;
    image: string;
    onClick: (value: string, search: number) => void;
}

export const Example = ({ text, value, image, search, onClick }: Props) => {
    return (
        <div className={styles.example} onClick={() => onClick(value, search)}>
            <p className={styles.exampleText}>
                サンプルシナリオ:
                <br />
                {text}
            </p>
            <img className={styles.exampleImage} src={image} />
        </div>
    );
};
