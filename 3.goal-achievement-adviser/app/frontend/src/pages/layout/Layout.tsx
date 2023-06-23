import { Outlet, NavLink, Link } from "react-router-dom";
import { useState, useMemo } from "react";
import { AccessToken, Claim } from "../../api";
import mslogo from "../../assets/msft-logo-color-text.png";
import styles from "./Layout.module.css";

const Layout = () => {
    const [loginUser, setLoginUser] = useState<string>("");
    const [isLogin, setIsLogin] = useState<boolean>(false);

    const getLoginUserName = async () => {
        const loginUser: string = "";

        let displayName = "";
        let login = false;

        try {
            const result = await fetch("/.auth/me");
            const response: AccessToken[] = await result.json();
            const loginUserClaim = response[0].user_claims.find((claim: Claim) => claim.typ === "preferred_username");
            if (loginUserClaim) {
                displayName = loginUserClaim.val;
                const i = displayName.indexOf("@");
                if (i !== -1) displayName = displayName.slice(0, i);
            } else displayName = response[0].user_id;

            login = true;
        } catch (e) {
            displayName = "guest";

            login = false;
        }

        setLoginUser(displayName);
        setIsLogin(login);
    };

    getLoginUserName();

    return (
        <div className={styles.layout}>
            <header className={styles.header} role={"banner"}>
                <div className={styles.headerContainer}>
                    <div className={styles.headerNavLeftMargin}>
                        <a href="https://www.microsoft.com/ja-jp" target={"_blank"} title="Microsoft link">
                            <img src={mslogo} alt="Microsoft" aria-label="Link to Microsoft" className={styles.microsoftLogo} />
                        </a>
                    </div>
                    <Link to="/" className={styles.headerTitleContainer}>
                        <h3 className={styles.headerTitle}>Azure OpenAI Service 目標達成アシスタント デモ</h3>
                    </Link>
                    <nav>
                        <ul className={styles.headerNavList}>
                            <li className={styles.headerNavLeftMargin}>{loginUser}</li>
                            {isLogin ? (
                                <li className={styles.headerNavLeftMargin}>
                                    <a href="/.auth/logout" className={styles.headerNavPageLink}>
                                        Sign Out
                                    </a>
                                </li>
                            ) : (
                                <></>
                            )}
                        </ul>
                    </nav>
                </div>
            </header>

            <Outlet />
        </div>
    );
};

export default Layout;
