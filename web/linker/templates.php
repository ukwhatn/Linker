<?php


function showMainDescription()
{
    return <<<HD
            <div class="description">
                <div class="ja">
                    <p>
                        <strong>"Linker"</strong>は、あなたの<a href="https://www.wikidot.com" target="_blank">Wikidot</a>と<a href="https://discord.com/" target="_blank">Discord</a>のアカウントを紐付けるためのサービスです。
                    </p>
                    <p>
                        このサービスで取得されたアカウントの情報は、<a href="https://scp-jp.wikidot.com" target="_blank">SCP財団Wiki</a>及びその関連サイト(他言語版Wikiを含む)、及びそれらのサイトの関連Discordサーバーの運営に使用される場合があります。
                    </p>
                    <p>
                        このサービスは、サーバーにあなたのWikidot及びDiscordアカウントのIDとユーザ名などの公開されている情報を取得・保存しますが、パスワードなどを取得・保存することはありません。
                    </p>
                    <p>
                        <strong>以上の事項に同意した上でこのサービスを利用するには、以下に進んでください。</strong>
                    </p>
                </div>
                <div class="en">
                    <p>
                        <strong>"Linker"</strong> is a service to link your <a href="https://www.wikidot.com" target="_blank">Wikidot</a> and <a href="https://discord.com/" target="_blank">Discord</a> accounts.
                    </p>
                    <p>
                        The account information acquired through this service may be used to manage the <a href="https://scpwiki.com" target="_blank">SCP Foundation Wiki</a>, its related sites (including wikis in other languages), and Discord servers.
                    </p>
                    <p>
                        This service acquires and stores your Wikidot and Discord account IDs, usernames, and other public information on the server, but doesn't acquire or store your passwords or other secret information.
                    </p>
                    <p>
                        <strong>If you agree to the above and wish to use this service, please proceed.</strong>
                    </p>
                </div>
            </div>
HD;
}

function showDiscordSection($body)
{
    return <<<HD
            <div class="section-wrap discord" id="discord">
                <div class="section-header ja">
                    1. Discordアカウントでログイン
                </div>           
                <div class="section-header en">
                    1. Sign in with your Discord account
                </div>       
                <div class="section-body">  
                    {$body}
                </div>
            </div>
HD;

}

function showSignInButton($OAuth)
{
    return <<<HD
            <a class="signin discord ja" href="{$OAuth->loginURL()}"><i class="fab fa-discord"></i>Discordでログイン</a>
            <a class="signin discord en" href="{$OAuth->loginURL()}"><i class="fab fa-discord"></i>Sign in with Discord</a>
HD;
}

function showDiscordUserPanel($userName, $userDiscriminator, $userId, $userAvatar)
{
    return <<<HD
        <div class="discord-user-panel-wrap">
            <div class="discord-user-panel ja">
                <i class="fab fa-discord"></i>
                <img class="discord-user-icon" src="https://cdn.discordapp.com/avatars/{$userId}/{$userAvatar}" alt="Discord user avatar">
                <div class="discord-user-area">
                    <div class="discord-user-name">{$userName}#{$userDiscriminator}</div>
                    <div class="discord-user-desc">としてサインイン中</div>
                    <div class="discord-user-logout"><a href="/linker?logout=true">サインアウト</a></div>
                </div>
            </div>
            <div class="discord-user-panel en">
                <i class="fab fa-discord"></i>
                <img class="discord-user-icon" src="https://cdn.discordapp.com/avatars/{$userId}/{$userAvatar}" alt="Discord user avatar">
                <div class="discord-user-area">
                    <div class="discord-user-name">{$userName}#{$userDiscriminator}</div>
                    <div class="discord-user-desc">is your account</div>
                    <div class="discord-user-logout"><a href="/linker?logout=true">Sign out</a></div>
                </div>
            </div>
            <script>
                let DiscordUserData = {
                    "id": "{$userId}",
                    "name": "{$userName}"
                }
            </script>
        </div>
HD;
}

function showWikidotAccountSection($account, $request)
{
    $statusTextMaster = [
        "unRequested" => <<<HD
            <div class="wikidot-link-status-body-desc">
                <div class="ja">
                    あなたのWikidotアカウント名を入力してください。
                </div>
                <div class="en">
                    Input your Wikidot account name:
                </div>
            </div>
            <div class="wikidot-link-status-body-request-form">
                <div class="input-group mb-3">
                  <span class="input-group-text" id="wikidot-link-status-body-request-form-addon1"><span class="ja">アカウント名</span><span class="en">Account Name</span></span>
                  <input type="text" id="inputField" class="form-control" placeholder="" aria-label="RequestUserName" aria-describedby="wikidot-link-status-body-request-form-addon1">
                </div>
                <button type="button" class="btn btn-primary" id="submitButton" onclick="confirmationCodeRequest()"><span class="ja">送信</span><span class="en">Submit</span></button>
            </div>
HD,
        "unConfirmed" => <<<HD
            <div class="wikidot-link-status-body-desc">
                <div class="ja">
                    あなたのWikidotアカウントにPMが送信されました。<br>
                    確認の上、認証コードを以下に入力してください。
                </div>
                <div class="en">
                    A PM has been sent to your Wikidot account. <br>
                    Please confirm and enter the verification code below.
                </div>
            </div>
            <div class="wikidot-link-status-body-request-form" id="requestedForm">
                <div class="input-group mb-3">
                  <span class="input-group-text" id="wikidot-link-status-body-request-form-addon1"><span class="ja">認証コード</span><span class="en">Verification Code</span></span>
                  <input type="text" id="inputField" class="form-control" placeholder="" aria-label="ConfirmationCode" aria-describedby="wikidot-link-status-body-request-form-addon1">
                </div>
                <button type="button" class="btn btn-primary" id="submitButton" onclick="verificationRequest()"><span class="ja">認証</span><span class="en">Verify</span></button>
            </div>
HD,
        "confirmed" => <<<HD
            <div class="wikidot-link-status-body-desc">
                <div class="ja">
                    このDiscordアカウントには、以下のWikidotアカウントがリンクされています。
                </div>
                <div class="en">
                    This Wikidot account is linked to your Discord account.
                </div>
            </div>
            <div class="wikidot-user-panel">
                <img src="wikidot.png" class="wikidoticon" alt="wikidot icon">
                <img src="https://www.wikidot.com/avatar.php?userid={$account['WikidotID']}" class="wikidot-user-icon" alt="icon">
                <a class="wikidot-user-name" target="_blank" href="https://www.wikidot.com/user:info/{$account['WikidotUserUnixName']}">{$account["WikidotUserName"]}</a>
            </div>
<!--            <button type="button" class="btn btn-danger" id="unlinkButton"><span class="ja">リンクを解除する</span><span class="en">Unlink your Wikidot account</span></button>-->
HD
    ];

    $statusText = "";
    $errorText = "";

    if ($request === false) {
        $statusText = $statusTextMaster["unRequested"];
    } else {
        switch ($request["Status"]) {
            case 0:
                // 未送信
                $statusText = $statusTextMaster["unConfirmed"];
                break;
            case 1:
                // 送信済み 認証待ち
                $statusText = $statusTextMaster["unConfirmed"];
                break;
            case 2:
                // 認証済み
                $statusText = $statusTextMaster["confirmed"];
                break;
            case 10:
                // 送信失敗(ユーザー未存在)
                $errorText = showErrorBlock("userNotExist");
                $statusText = $statusTextMaster["unRequested"];
                break;
            case 11:
                // 送信失敗(パーミッションエラー)
                $errorText = showErrorBlock("forbidden");
                $statusText = $statusTextMaster["unConfirmed"];
                break;
            case 12:
                // 送信失敗(その他の理由)
                $errorText = showErrorBlock("unexpected");
                $statusText = $statusTextMaster["unConfirmed"];
                break;
        };
    }

    return <<<HD
            <div class="section-wrap wikidot" id="wikidot">
                <div class="section-header ja">
                    2. Wikidotアカウントと連携
                </div>           
                <div class="section-header en">
                    2. Link your Wikidot account
                </div>       
                <div class="section-body">  
                    {$errorText}
                    {$statusText}
                </div>
            </div>
HD;

}

function afterTokenizeWindow($dbh, $OAuth, $response)
{
    // tokenを保存
    $_SESSION["discord_token"] = $response["access_token"];
    $_SESSION["refresh_token"] = $response["refresh_token"];

    // ユーザ情報取得
    $_SESSION["discord_user"] = $OAuth->getMe($_SESSION["discord_token"]);

    // エスケープ
    $userName = htmlspecialchars($_SESSION["discord_user"]["username"], ENT_QUOTES, 'UTF-8');
    $discriminator = htmlspecialchars($_SESSION["discord_user"]["discriminator"], ENT_QUOTES, 'UTF-8');
    $userId = htmlspecialchars($_SESSION["discord_user"]["id"], ENT_QUOTES, "UTF-8");

    // DBからデータ取得
    $prepare = $dbh->prepare("INSERT INTO Accounts (DiscordID, DiscordUserName, DiscordUserHash) VALUES(:discordId, :discordName, :discordHash) ON DUPLICATE KEY UPDATE DiscordUserName = :discordName, DiscordUserHash = :discordHash");
    $prepare->bindValue(":discordId", $userId);
    $prepare->bindValue(":discordName", $userName);
    $prepare->bindValue(":discordHash", $discriminator);
    $prepare->execute();
    $prepare = $dbh->prepare("SELECT * FROM Accounts WHERE DiscordID = :discordId");
    $prepare->bindValue(":discordId", $userId);
    $prepare->execute();
    $account = $prepare->fetch(PDO::FETCH_ASSOC);

    $prepare = $dbh->prepare("SELECT * FROM LinkRequests WHERE DiscordID = :discordId ORDER BY RequestDate DESC");
    $prepare->bindValue(":discordId", $userId);
    $prepare->execute();
    $request = $prepare->fetch(PDO::FETCH_ASSOC);

    // 説明表示
    echo showMainDescription();
    // Discordセクション表示
    echo showDiscordSection(showDiscordUserPanel($userName, $discriminator, $userId, $_SESSION["discord_user"]["avatar"]));
    // Wikidotアカウントセクション表示
    echo showWikidotAccountSection($account, $request);
}

function showErrorBlock($code)
{
    switch ($code) {
        case "outdatedToken":
            return <<<HD
                <div class="error-block">
                    <div class="error-block-content">
                        <i class="fas fa-exclamation-triangle"></i> 無効なトークンです。再度ログインしてください。
                    </div>
                </div>
HD;
            break;
        case "unexpected":
            return <<<HD
                <div class="error-block">
                    <div class="error-block-content">
                        <i class="fas fa-bug"></i> 予期しないエラーが発生しました。
                    </div>
                </div>
HD;
            break;
        case "forbidden":
            return <<<HD
                <div class="error-block">
                    <div class="error-block-content">
                        <i class="fas fa-bug"></i> PMを送信できませんでした。<a href="https://www.wikidot.com/account/messages#/settings" target="_blank" class="underLinedLink">一時的にPMの受信拒否設定を解除してください。</a>
                    </div>
                </div>
HD;
            break;
        case "userNotExist":
            return <<<HD
                <div class="error-block">
                    <div class="error-block-content">
                        <i class="fas fa-bug"></i> 入力された名前のWikidotアカウントが存在しませんでした。
                    </div>
                </div>
HD;
            break;
    }
}

function showAlertBlock($code)
{
    switch ($code) {
        case "logout":
            return <<<HD
            <div class="alert alert-success float" role="alert">
                <span class="ja">
                    ログアウトしました。
                </span>
                <span class="en">
                    Sign out successful.
                </span>
            </div>
HD;
            break;
        case "oauthError":
            return <<<HD
            <div class="alert alert-danger float" role="alert">
                <span class="ja">
                    ログインが中断されました。
                </span>
                <span class="en">
                    Sign-in cancelled.
                </span>
            </div>
HD;
            break;


    }
}