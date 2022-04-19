<a href="https://jaobernardi.space"><img src="assets/images/jdspace.png"></a>
<hr>
<p align="center">End-point de convergência de dados.</p>
<p align="center">
    <a href="https://twitter.com/jaobernard">
        <img alt="Feito por João Bernardi" src="https://img.shields.io/badge/feito%20por-%40jaobernard-39013C">
    </a>
    <a>
        <img src="https://img.shields.io/github/last-commit/jaobernardi/jaobernardi.space?color=39013C">
    </a>
    <a href="https://jaobernardi.space">
        <img src="https://img.shields.io/website?down_message=offline&up_message=online&url=https%3A%2F%2Fjaobernardi.space">
    </a>
</p>
<hr><br><br>

## To-do
- [ ] Database:
    - [ ] Shared database for @arquivodojao.
    - [x] Tokens
    - [x] Sessions
    - [x] Users
    - [x] Salts
- [ ] Backend
    - [x] HTTP(S) Server
        - [x] Data relaying 
    - [x] Request parsing
    - [x] Response parsing
    - Handlers:
        - Services
            - [ ] Twitter video downloading
                - [x] By ID
                - [x] By URL
        - Default:
            - [x] File serving
            - [x] Custom per path behavior (settings file)
        - Auth:
            - Third party auths:
                - [ ] Spotify
                - [ ] Google
        - API:
            - Twitter
                - [x] Webhooks
                    - [x] Stream webhook data
            - Spotify
                - [ ] Read current song
                - [ ] Stream spotify data
        - [x] Content
        - [x] Filtering
- [ ] Front-end
    - [ ] Homepage