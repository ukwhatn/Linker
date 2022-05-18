<?php
session_name("LINKER_TOKEN");
session_start();
$dbh = null;
require_once "database.php";

$data = json_decode(file_get_contents("php://input"), true);

if ($_SERVER["REQUEST_METHOD"] === "POST") {
    if (!array_key_exists("discord_user", $_SESSION) || !array_key_exists("discordUser", $data)) {
        echo json_encode(array("status" => "error", "reason" => "invalid_request", "data" => [$_SESSION, $data]));
        exit;
    } else {
        if ($_SESSION["discord_user"]["id"] !== $data["discordUser"]["id"]) {
            echo json_encode(array("status" => "error", "reason" => "invalid_user"));
            exit;
        } else {
            switch ($data["mode"]) {
                case "confirm":
                    if (!array_key_exists("wikidotUserName", $data)) {
                        echo json_encode(array("status" => "error", "reason" => "invalid_request"));
                        exit;
                    } else {
                        $prepare = $dbh->prepare("INSERT INTO LinkRequests(DiscordID, WikidotUserName) VALUES(:discordId, :wikidotUserName)");
                        $prepare->bindValue(":discordId", $_SESSION["discord_user"]["id"]);
                        $prepare->bindValue(":wikidotUserName", $data["wikidotUserName"]);
                        $prepare->execute();
                        echo json_encode(array("status" => "success"));
                        exit;
                    }
                    break;
                case "verify":
                    if (!array_key_exists("verificationCode", $data)) {
                        echo json_encode(array("status" => "error", "reason" => "invalid_request"));
                        exit;
                    } else {
                        // DBからデータ取得
                        $prepare = $dbh->prepare("SELECT * FROM LinkRequests WHERE DiscordID = :discordId ORDER BY RequestDate DESC");
                        $prepare->bindValue(":discordId", $_SESSION["discord_user"]["id"]);
                        $prepare->execute();
                        $request = $prepare->fetch(PDO::FETCH_ASSOC);

                        if ($request["VerificationCode"] !== $data["verificationCode"]) {
                            echo json_encode(array("status" => "error", "reason" => "wrong_code"));
                            exit;
                        } else {
                            // requestをupdate
                            $prepare = $dbh->prepare("UPDATE LinkRequests SET Status = 2, ConfirmDate = CURRENT_TIMESTAMP WHERE id = :id");
                            $prepare->bindValue(":id", $request["id"]);
                            $prepare->execute();
                            // accountをupdate
                            $prepare = $dbh->prepare("UPDATE Accounts SET WikidotVerified = 1 WHERE DiscordID = :discordId");
                            $prepare->bindValue(":discordId", $_SESSION["discord_user"]["id"]);
                            $prepare->execute();
                            echo json_encode(array("status" => "success"));
                            exit;
                        }

                    }
                    break;
                case "check":
                    // DBからデータ取得
                    $prepare = $dbh->prepare("SELECT * FROM LinkRequests WHERE DiscordID = :discordId ORDER BY RequestDate DESC");
                    $prepare->bindValue(":discordId", $_SESSION["discord_user"]["id"]);
                    $prepare->execute();
                    $request = $prepare->fetch(PDO::FETCH_ASSOC);

                    echo json_encode(["request_status" => $request["Status"]]);
            }
            exit;
        }
    }
} else {
    echo json_encode(array("status" => "error", "reason" => "invalid_request"));
    exit;
}