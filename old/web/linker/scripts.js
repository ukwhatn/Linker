const LANGUAGES = ["ja", "en"];

function changeLanguage(lang, updateStorage = true) {
    if (LANGUAGES.includes(lang)) {
        LANGUAGES.forEach(function (_lang) {
            if (lang === _lang) {
                let elems = document.getElementsByClassName(_lang);
                for (let i = 0; i < elems.length; i++) {
                    elems[i].style.display = "";
                }
            } else {
                let elems = document.getElementsByClassName(_lang);
                for (let i = 0; i < elems.length; i++) {
                    elems[i].style.display = "none";
                }
            }
        })
    }
    if (updateStorage === true) {
        localStorage.setItem("lang", lang);
    }
}


changeLanguage("ja", false);

window.onload = function () {
    let langInLocalStorage = localStorage.getItem("lang");
    if (langInLocalStorage !== null) {
        changeLanguage(langInLocalStorage, false);
    } else {
        changeLanguage("ja", false);
    }
}

function confirmationCodeRequest() {
    let userName = document.getElementById("inputField").value;
    fetch("https://apps.ukwhatn.com/linker/submitModule.php", {
        method: "POST",
        mode: "same-origin",
        cache: "no-cache",
        headers: {
            "Content-Type": "application/json",
        },
        referrerPolicy: "strict-origin-when-cross-origin",
        credentials: "same-origin",
        body: JSON.stringify({
            "mode": "confirm",
            "discordUser": DiscordUserData,
            "wikidotUserName": userName
        })
    }).then(response => {
        if (!response.ok) {
            throw new Error();
        }
        return response.json()
    }).then(data => {
        console.log(data)
        switch (data["status"]) {
            case "success":
                if (window.location.href === "https://apps.ukwhatn.com/linker/#wikidot") {
                    window.location.reload();
                } else {
                    window.location.href = "/linker/#wikidot"
                }

                break;
            case "error":
                console.error(data);
                throw new Error();
        }
    }).catch((e) => {
        window.alert("エラーが発生しました。もう一度お試しください。");
        console.warn(e);
    })
}

function verificationRequest() {
    let verificationCode = document.getElementById("inputField").value;
    fetch("https://apps.ukwhatn.com/linker/submitModule.php", {
        method: "POST",
        mode: "same-origin",
        cache: "no-cache",
        headers: {
            "Content-Type": "application/json",
        },
        referrerPolicy: "strict-origin-when-cross-origin",
        credentials: "same-origin",
        body: JSON.stringify({
            "mode": "verify",
            "discordUser": DiscordUserData,
            "verificationCode": verificationCode
        })
    }).then(response => {
        if (!response.ok) {
            throw new Error();
        }
        return response.json()
    }).then(data => {
        console.log(data)
        switch (data["status"]) {
            case "success":
                if (window.location.href === "https://apps.ukwhatn.com/linker/#wikidot") {
                    window.location.reload();
                } else {
                    window.location.href = "/linker/#wikidot"
                }

                break;
            case "error":
                if (data["reason"] === "wrong_code") {
                    alert("コードが間違っています、もう一度お試しください。");
                } else {
                    console.error(data);
                    throw new Error();
                }
        }
    }).catch((e) => {
        window.alert("エラーが発生しました。もう一度お試しください。");
        console.warn(e);
    })
}

function checkRequest() {
    if (document.getElementById("requestedForm") !== null) {
        fetch("https://apps.ukwhatn.com/linker/submitModule.php", {
            method: "POST",
            mode: "same-origin",
            cache: "no-cache",
            headers: {
                "Content-Type": "application/json",
            },
            referrerPolicy: "strict-origin-when-cross-origin",
            credentials: "same-origin",
            body: JSON.stringify({
                "mode": "check",
                "discordUser": DiscordUserData
            })
        }).then(response => {
            if (!response.ok) {
                throw new Error();
            }
            return response.json()
        }).then(data => {
            console.log(data)
            switch (data["request_status"]) {
                case "0":
                    // 未送信
                    break;
                case "1":
                    // 送信済
                    break;
                case "2":
                    // 確認済
                    break;
                case "10":
                    // ユーザ存在せず
                    if (window.location.href === "https://apps.ukwhatn.com/linker/#wikidot") {
                        window.location.reload();
                    } else {
                        window.location.href = "/linker/#wikidot"
                    }
                    break;
                case "11":
                    // forbidden
                    if (window.location.href === "https://apps.ukwhatn.com/linker/#wikidot") {
                        window.location.reload();
                    } else {
                        window.location.href = "/linker/#wikidot"
                    }
                    break;
                case "12":
                    // unexpected
                    if (window.location.href === "https://apps.ukwhatn.com/linker/#wikidot") {
                        window.location.reload();
                    } else {
                        window.location.href = "/linker/#wikidot"
                    }
                    break;
            }
        }).catch((e) => {
            window.alert("エラーが発生しました。もう一度お試しください。");
            console.warn(e);
        })
    }
}

if (document.getElementById("requestedForm") !== null) {
    setInterval(checkRequest, 5000);
}