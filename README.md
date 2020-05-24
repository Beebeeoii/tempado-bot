# TempAdoBot
A telegram bot for temptaking.ado.sg!

## Features
1. Send your temperature directly through me on telegram after a one-time setup
2. Set up daily reminders for AM and PM temperature
3. Check who have not send their temperatures for the day

# This is not an automated bot that automatically sends a temperauture for you daily! You are to take your temperature using a thermometer before using this tool!

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