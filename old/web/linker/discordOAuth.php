<?php

class discordOAuth
{
    private $OAuth2ClientID = 939149483177025557;
    private $OAuth2ClientSecret = "S7vCArek5bSEZfzpWZdPJRn0CIzTztU1";

    private $authorizeURL = "https://discord.com/api/oauth2/authorize";
    private $tokenizeURL = "https://discord.com/api/oauth2/token";
    private $apiURLMe = "https://discord.com/api/users/@me";

    private $mainURL = "https://apps.ukwhatn.com/linker/";

    public function loginURL()
    {
        $requestParams = array(
            "client_id" => $this->OAuth2ClientID,
            "redirect_uri" => $this->mainURL,
            "response_type" => "code",
            "scope" => "identify"
        );
        return $this->authorizeURL . "?" . http_build_query($requestParams);
    }

    public function tokenize($code)
    {
        $requestParams = array(
            "client_id" => $this->OAuth2ClientID,
            "client_secret" => $this->OAuth2ClientSecret,
            "redirect_uri" => $this->mainURL,
            "grant_type" => "authorization_code",
            "code" => $code
        );
        $curl = curl_init();
        $curlOptions = array(
            CURLOPT_URL => $this->tokenizeURL,
            CURLOPT_POST => true,
            CURLOPT_POSTFIELDS => $requestParams,
            CURLOPT_SSL_VERIFYPEER => false,
            CURLOPT_RETURNTRANSFER => true
        );
        curl_setopt_array($curl, $curlOptions);
        $response = curl_exec($curl);
        curl_close($curl);
        return json_decode($response, true);
    }

    public function refreshToken($token)
    {
        $requestParams = array(
            "client_id" => $this->OAuth2ClientID,
            "client_secret" => $this->OAuth2ClientSecret,
            "grant_type" => "refresh_token",
            "refresh_token" => $token
        );
        $curl = curl_init();
        $curlOptions = array(
            CURLOPT_URL => $this->tokenizeURL,
            CURLOPT_POST => true,
            CURLOPT_POSTFIELDS => $requestParams,
            CURLOPT_SSL_VERIFYPEER => false,
            CURLOPT_RETURNTRANSFER => true
        );
        curl_setopt_array($curl, $curlOptions);
        $response = curl_exec($curl);
        curl_close($curl);
        return json_decode($response, true);
    }

    public function getMe($token)
    {
        $curl = curl_init();
        $curlOptions = array(
            CURLOPT_URL => $this->apiURLMe,
            CURLOPT_RETURNTRANSFER => true,
            CURLOPT_HTTPHEADER => array(
                "Authorization: Bearer " . $token
            )
        );
        curl_setopt_array($curl, $curlOptions);
        $response = curl_exec($curl);
        curl_close($curl);
        return json_decode($response, true);
    }

}