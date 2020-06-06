# TempAdoBot
A telegram bot for temptaking.ado.sg!

## About
This bot was made specifically for personels required to submit twice daily temperatures on temptaking.ado.sg. It was made to better lifes by reducing the hassle of manually submitting temperatures through the website and checking of who has yet to send their temperatures.

## Screenshots
<img src = "/screenshot1.jpg" width="200"> <img src = "/screenshot2.jpg" width="200">

## Preamble
This is **NOT** an automated bot that automatically sends a temperauture for you daily. It does **NOT** randomise temperatures for you. You **ARE** to take your temperature using a thermometer before using this tool.

## Features
1. One-time user-friendly set up!
2. Send your temperatures directly on telegram after a one-time setup
3. Set up daily reminders for AM and PM temperature (**recommended for groups**)
4. Check who have not send their temperatures for the day (**mainly for commanders who have the link - it is different from the one used to send temperatures**)
5. Check your personal temperature submission history for the day

## How to use
Search me up on telegram @TempAdoBot or simply [click me](http://t.me/TempAdoBot "Click to start using TempAdoBot")!

1. Sending of temperature (**__/sendtemp__**)
   - **__/setup__**
     - Use this to setup your PIN, URL and who you are, all hassle-free!
   - **__/pin__**
     - View/change your 4-digit PIN to send your temperatures (Eg. 0000)
   - **__/url__**
     - View/change your URL to send your temperatures (Eg. https://temptaking.ado.sg/group/unique-code)
   - **__/sender__**
     - View/change your name to send your temperatures
     - Select your name from the custom telegram keyboard
   - These three items (URL, PIN and sender) must be set before using /sendtemp
   - It is **highly encouraged** that this is done through direct messages to the bot and not on groups lest group spams
2. Setting up of daily temperature reminders
   - **__/subscribe__**
     - Subscribes to daily reminders for both AM and PM temperatures
     - AM reminders sent at **__1100__**
     - PM reminders sent at **__1530__**
   - **__/unsubscribe__**
     - Unsubscribes to daily reminders for both AM and PM temperatures
     - You will not receive any reminders from the bot anymore!
3. Checking of members who have not sent their temperatures for the day
   - **__/track__**
     - View/change the URL you use see everyone's temperature in the group (Eg. https://temptaking.ado.sg/overview/another-unique-code)
4. Checking of your personal temperature submission history
   - **__/history__**
     - View your AM and PM temperature submissions for the day

For more info, seek help from the bot by using **__/help__** :)

## Changelog
[Click to view changelog](/CHANGELOG.md)

## Future plans:
- [ ] Include ability to submit temperature for AM even if it is PM already
- [x] Include ability to broadcast to users when server is encountering issues
- [ ] Stop this bot :)