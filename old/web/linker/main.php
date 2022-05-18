<?php
ini_set('display_errors', "On");

require_once "discordOAuth.php";
$OAuth = new discordOAuth();

require_once "templates.php";
require_once "database.php";

session_name("LINKER_TOKEN");
session_start();

?>

<html lang="ja">
<head>

    <title>Wikidot Linker</title>
    <meta charset="utf-8">
    <meta name="author" content="ukwhatn">

    <meta name="viewport" content="width=device-width,initial-scale=1.0,minimum-scale=1.0"/>
    <link rel="apple-touch-icon" type="image/png" href="apple-touch-icon-180x180.png">
    <link rel="icon" type="image/png" href="icon-192x192.png">

    <!-- reset css -->
    <link
            href="https://unpkg.com/sanitize.css"
            rel="stylesheet"
    />

    <!-- BootStrap -->
    <link
            href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.0-beta1/dist/css/bootstrap.min.css"
            rel="stylesheet"
            integrity="sha384-giJF6kkoqNQ00vy+HMDP7azOuL0xtbfIcaT9wjKHr8RbDVddVHyTfAAsrekwKmP1"
            crossorigin="anonymous">
    <script
            src="https://cdn.jsdelivr.net/npm/bootstrap@5.0.0-beta1/dist/js/bootstrap.bundle.min.js"
            integrity="sha384-ygbV9kiqUc6oa4msXn9868pTtWMgiQaeYH7/t7LECLbyPA2x65Kgf80OJFdroafW"
            crossorigin="anonymous"></script>

    <!-- Font Awesome -->
    <link
            rel="stylesheet"
            href="https://use.fontawesome.com/releases/v5.15.4/css/all.css"
            integrity="sha384-DyZ88mC6Up2uqS4h/KRgHuoeGwBcD4Ng9SiP4dIRy0EXTlnuz47vAwmeGwVChigm"
            crossorigin="anonymous">

    <!-- Custom Style Sheet -->
    <link rel="stylesheet" href="./styles.css">
</head>
<body>
<header>
    <div class="header-title">
        Linker
    </div>
    <div class="header-language-button-wrap">
        <a class="header-language-button ja" onclick="changeLanguage('en')">English</a>
        <a class="header-language-button en" onclick="changeLanguage('ja')">日本語</a>
    </div>
</header>

<div id="main-contents" class="main-contents">
    <?php
    // GETリクエストにのみmain-contentの内容をレスポンス
    if ($_SERVER["REQUEST_METHOD"] === "GET") {
        // logout = true => sessionに保存されたトークンを破棄
        if (array_key_exists("logout", $_GET) && $_GET["logout"] === "true") {
            foreach (["discord_token", "refresh_token", "discord_user"] as $key) {
                if (array_key_exists($key, $_SESSION)) {
                    unset($_SESSION[$key]);
                }
            }
            echo showAlertBlock("logout");
        }

        // OAuthエラー時
        if (array_key_exists("error", $_GET) && $_GET["error"] === "access_denied") {
            echo showAlertBlock("oauthError");
        }

        // code付 = discord認証後
        if (array_key_exists("code", $_GET)) {
            // token引換
            $tokens = $OAuth->tokenize($_GET["code"]);
            // token化に成功
            if (array_key_exists("access_token", $tokens) && array_key_exists("refresh_token", $tokens)) {
                // ステータス表示
                afterTokenizeWindow($dbh, $OAuth, $tokens);
            } // 既に使用されているtoken
            elseif (array_key_exists("error", $tokens)) {
                // codeなしにリダイレクト
                Header("Location: https://apps.ukwhatn.com/linker/");
            } // 不明なエラー
            else {
                // 説明表示
                echo showMainDescription();
                // エラー表示
                echo showErrorBlock("unexpected");
                // Discord
                echo showDiscordSection(showSignInButton($OAuth));
            }
        } // discord認証前
        else {
            // sessionにtokenが残っている = token refresh
            if (array_key_exists("discord_token", $_SESSION) && array_key_exists("refresh_token", $_SESSION)) {
                // tokenを再発行
                $refreshedTokens = $OAuth->refreshToken($_SESSION["refresh_token"]);
                // tokenが通った
                if (array_key_exists("access_token", $refreshedTokens) && array_key_exists("refresh_token", $refreshedTokens)) {
                    // ステータス表示
                    afterTokenizeWindow($dbh, $OAuth, $refreshedTokens);
                } // tokenが通らなかった
                else {
                    // 説明表示
                    echo showMainDescription();
                    // エラー表示
                    echo showErrorBlock("outdatedToken");
                    // Discord
                    echo showDiscordSection(showSignInButton($OAuth));
                }
            } // sessionが残っていない
            else {
                // 説明表示
                echo showMainDescription();
                // Discord
                echo showDiscordSection(showSignInButton($OAuth));
            }
        }
    }
    ?>
</div>
<footer>
    Linker is developed and maintained by <a href="https://github.com/ukwhatn" target="_blank">ukwhatn</a>.<br>
    Code License: <a
            href="https://opensource.org/licenses/MIT"
            target="_blank">MIT License</a>
    /
    Page License: <a
            href="https://creativecommons.org/licenses/by-sa/4.0/deed.en"
            target="_blank"><i class="fab fa-creative-commons"></i> CC BY-SA 4.0</a><br>
    Components: <a
            href="https://getbootstrap.jp/"
            target="_blank"><i class="fab fa-bootstrap"></i> Bootstrap</a>(License: <a
            href="https://opensource.org/licenses/MIT"
            target="_blank">MIT License</a>),
    <a
            href="https://fontawesome.com/"
            target="_blank"><i class="fab fa-font-awesome"></i> Font Awesome</a>(License: <a
            href="http://scripts.sil.org/OFL"
            target="_blank">SIL OFL 1.1</a>(Font), <a
            href="https://opensource.org/licenses/MIT"
            target="_blank">MIT License</a>(Code))
</body>
<script src="scripts.js"></script>
</html>


