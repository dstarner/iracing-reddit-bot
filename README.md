# iRacing Reddit Bot

The purpose of this bot is to automate replies to comments and posts in the [iRacing subreddit community](https://www.reddit.com/r/iRacing/). A majority of these posts cover only 5 or 6 topics, so if we can categorize them correctly and respond accordingly within seconds, we can try to improve the quality of the subreddit to keep it top-notch.

## Why?

Why am I deciding to make this bot? Well, let me tell you:

#### Rapid Growth of iRacing

With the rapid growth of iRacing in early 2020, we need to make sure that the communities and standards stay in good shape. This means answering people's questions, while ensuring that these questions are relevant, on topic, and are not repeated. A Reddit bot can self-moderate in a rapid way that humans simply can. Even on the mobile app, most people do not read the *"About"* section leading them to asking the same 4 questions that are listed in the sporting code. A bot can categorize these questions, answer them, and potentially even lock / hide the post. (That last part may be overkill, but the ability is there)

#### Because I Want to Learn

I've never written a Reddit bot before, and this is good practice. Initially it will be written in Python using the [Python PRAW API wrapping library](https://praw.readthedocs.io/en/latest/), but eventually I'd like to write a fully open-sourced Go library for interacting with Reddit, and port this bot over to Go. Why? Because the pursuit of knowledge is fun, no matter how tiring it gets.

This also lets me get my hands dirty on some NLP (Natural Language Processing) and text categorization. I've never done it before so it will be interesting to see how the bot evolves to be smarter and better at answering.

## TODOs

Since this is so new, here's a list of TODOs that I'd like to see

* Deploy it to heroku
* Add testing and GitHub actions for testing / deploying
* MORE [~POWER!~](https://i.kinja-img.com/gawker-media/image/upload/s--76jZSwWT--/c_fill,fl_progressive,g_center,h_450,q_80,w_800/18n2u2jtl147mjpg.jpg)topics! I want the bot to be able to answer at least 10 different categories of information correctly.
* Linking / quoting specific Sporting Code sections: I'd be nice to say "!irbot what is 3.5 of the sporting code?", and it would just quote out the incidents section while linking it for good measure. This would require a PDF reader library, and I don't know if linking to sections in PDFs is even possible, maybe just the page.
* Auto-replying to posts / comments: Right now it gets summoned with `!irbot`, but it would be cool if it could just respond to posts on its own if it had a high enough confidence in the post's topic.
* Some easter egg hidden away that will prompt a legendary response if requested.

Create a ticket if you have more suggestions 😃 I'm bored during quarantine so I don't mind working on this.
