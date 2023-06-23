import { Pivot, PivotItem } from "@fluentui/react";
import DOMPurify from "dompurify";

import styles from "./AnalysisPanel.module.css";

import { SupportingContent } from "../SupportingContent";
import { ChatResponse } from "../../api";
import { AnalysisPanelTabs } from "./AnalysisPanelTabs";

interface Props {
    className: string;
    response: ChatResponse | undefined;
}

const pivotItemDisabledStyle = { disabled: true, style: { color: "grey" } };

export const AnalysisPanel = ({ response, className }: Props) => {
    return (
        <div className={className}>
            <table className={styles.stepTable}>
                <thead>
                    <tr>
                        <th className={styles.stepTableColumnNo}>{response?.headers[0]}</th>
                        <th className={styles.stepTableColumnStep}>{response?.headers[1]}</th>
                        <th className={styles.stepTableColumnDetail}>{response?.headers[3]}</th>
                    </tr>
                    {/* <tr>{response?.headers.map((header, index) => (index != 2 ? <th className={styles.stepTableHeader}>{header}</th> : ""))}</tr> */}
                </thead>
                <tbody>
                    {response?.steps.map((step, index) => (
                        <tr>
                            <td className={styles.stepTableCellNo}> {step.step_num} </td>
                            <td className={styles.stepTableCellStep}>{step.content}</td>
                            {/* <td>{step.variable_name}</td> */}
                            <td className={styles.stepTableCellDetail}>{step.value}</td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
};
