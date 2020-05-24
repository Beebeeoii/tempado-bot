# TempAdoBot
A telegram bot for temptaking.ado.sg!

## About
This bot was made specifically for personels required to submit twice daily temperatures on temptaking.ado.sg. It was made to better lifes by reducing the hassle of manually submitting temperatures through the website and checking of who has yet to send their temperatures.

## Features
1. Send your temperature directly through me on telegram after a one-time setup
2. Set up daily reminders for AM and PM temperature (**recommended for groups**)
3. Check who have not send their temperatures for the day

# This is NOT an automated bot that automatically sends a temperauture for you daily. You ARE to take your temperature using a thermometer before using this tool.

## How to use
Search me up on telegram @ TempAdoBot or simply click http://t.me/TempAdoBot

1. Sending of temperature (**__/sendtemp__**)
   - **__/setsendurl__** <URL>
     - Set up your URL to that you use to send your temperatures (Eg. https://temptaking.ado.sg/group/<unique-code>)
     - This is **required** before you can execute /setsender!
   - **__/setsendpin__** <4-digit PIN>
     - Set up your 4-digit PIN you use to send your temperatures (Eg. 0000)
   - **__/setsender__**
     - Set who you are whenever you send a temperature through the bot
     - Select your name from the custom telegram keyboard
   - These three items (URL, PIN and sender) must be set before using /sendtemp
   - It is **highly encouraged** that this is done through direct messages to the bot and not on groups lest group spams
2. Setting up of daily temperature reminders
   - **__/subscribe__**
     - Subscribes to daily reminders for both AM and PM temperatures
     - AM reminders sent at 1100
     - PM reminders sent at **__1530__**
   - **__/unsubscribe__**
     - Unsubscribes to daily reminders for both AM and PM temperatures
     - You will not receive any reminders from the bot anymore!
3. Checking of members who have not sent their temperatures for the day (**__/forcecheck__**)
   - **__/setcheckurl__** <URL>
     - Set up your URL to that you use to send your temperatures (Eg. https://temptaking.ado.sg/overview/<unique-code>)
     - This must be done before using /forcecheck

For more info, seek help from the bot by using **__/help__** :) 

## Future plans:
- [] Stop this bot (for there is no reason for this after this COVID period)