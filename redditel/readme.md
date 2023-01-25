A Bot that fetches challenges from r/dailyprogrammer and sends them to you via telegram.

For the bot to work you'll need: 
* A heroku account, you can create one [here](https://signup.heroku.com) if you don't have one. 
* A telegram account. 
* A reddit account

Fork this repository. \
Clone the fork you just created. 


Go to [Heroku website](heroku.com), login and create a new App; choose a meaningful name for your App. \
Go to Resources and search for Heroku postgres under add-ons and attach the database to your app. \
Now we need to add a python build pack, head over to Settings>Add Build Pack>Select the Python Option. 

Click [here](https://devcenter.heroku.com/articles/heroku-cli) to install heroku cli for your OS. \
create a .env file in the directory with the bot. You will save all your credentials in this file. 

Login to your telegram account and search for @BotFather follow the instructions given and then copy the bot token  given.
Save the token in the .env file you created as BOT_TOKEN = Your token 

Search for myidbot and type in /getid. Save the id you get from the bot in the .env file as CHAT_ID = id. 

Click [here](https://ssl.reddit.com/prefs/apps/) and create a new app > script. \
Add the following to the .env file cSC = secret, cID = personal use script, USER_AGENT = name, USERNAME = Your reddit username, PASSWORD = Your reddit password. 

On your terminal run the following command. \
`heroku authorizations:create`

Save the token as HEROKU_API_TOKEN = token and add HEROKU_APP_NAME = Your app name to the .env file.
Finally, go to heroku, click on the app you made > Settings > Reveal config vars and copy the database url and save it as DATABASE_URL = database url. \

On the terminal run the following commands: \
`heroku login` \
`heroku git:remote -a NAME_OF_YOUR_HEROKU_APP` \
`git add .` \
`git commit -m "deployment commit"` \
`git push --set-upstream heroku master`

Then:
`chmod +x reddit_bot.py` \
`./reddit_bot.py --create` \
`./reddit_bot.py --insert` This takes some time so you might want to get some coffee.

For each of the variables in the .env file, run the command `heroku config:set VARIABLE_NAME=VARIABLE_VALUE` \
run `heroku config:set QUESTIONS=number of questions you want per day` to set the number of questions to receive per day.

If I update the code, you can merge the changes with the code you have by running the following commands: \
`git pull` \
`git add .` \
`git commit -m "commit message"` \
`git push heroku`


The bot runs for five minutes then shuts down. You can visit https://cron-job.org/en/ and set the time when the bot should run and send the challenges.

If you can make this project better, open a PR and I will merge your pull request.
