# Go Analog: a boardgame recommender

> [Go Analog](http://fromdatatoknowledge.xyz) is a web app that recommends boardgames to videogamers.

The web app works like this:
* You enter your Steam id
* Go Analog accesses your video game play history…
* …and recommends boardgames that are similar to the video games you play

All you need to use it is an active Steam account that isn't set to private.

## Table of contents
* [What's in the repo](#whats-in-the-repo)
* [How Go Analog works](#how-go-analog-works)
* [Why item-based collaborative filtering?](#why-item-based-collaborative-filtering)
* [Future plans and to do](#future-plans-and-to-do)
* [Links](#links)

## What's in the repo
This repo contains the code for the entire Go Analog project.

Erring on the side of privacy, I've omitted most of the raw data, since they include personal information that could potentially be used to identify users (usernames, real names, locations, etc.).

The code is mainly divided into three folders:
* **scraping_cleaning_normalizing** contains all of the scripts used to build the dataset, numbered by order of application
* **app** contains the Go Analog flask app
* **eda_tests** contains jupyter notebooks for analysis of the data set

## How Go Analog works
Go Analog makes recommendations using [item-based collaborative filtering](https://en.wikipedia.org/wiki/Item-item_collaborative_filtering). Basically, it recommends board games that are similar to the video games you play.

Similarity here really means 'liked by similar people.' So if the same people like both 'Pong' and 'Candy Land', those two games are similar. You can find the entire similarity matrix — really the heart of Go Analog! — [in the repo](https://github.com/BrianWilliamSmith/Insight-Project-board-game-recommender).

[Here](https://docs.google.com/presentation/d/16JGC_vJrtQKlkViPoCGy1kgdfBGs667lXzVwMJ1LmWM/edit?usp=sharing) are slides if you want to read more about the business context of the app or how the data were collected.

## Why item-based collaborative filtering?
I considered many algos while building the app:
* Item-based collaborative filtering
* User-based collaborative filtering
* Matrix factorization (SVD-based recommendation)
* A few baselines, including recommending the top 10 boardgames

Item-based collaborative filtering wins across the board
* It's really fast
    * To get item similarity, you look it up in a table
    * No online calculation of similarity
* It makes recommendations that are more relevant and diverse
    * It outperforms other models on MAP@k
    * It has better catalog coverage, serving a wider range of games to users
* It's really well-suited to the structure of the game-user data set
    * The game:user ratio in the dataset is relatively high
    * When there are many items but few users, user-based collaborative filtering doesn't work as well as item-based collaborative filtering (consistent with what I've found for Go Analog)

## Future plans and to do
* Add content-based recommendation
    *  The data set contains properties for every video game and board game, including game genre, playstyle, setting, and difficulty
    *  These could be used to build a better recommender that learns a user's tastes.
        * For example, I like really complex board games and sci-fi games
    *  Adding content-based recommendation would allow Go Analog to make predictions about any game, even games that no one has ever played
 
## Links
* [GoAnalog website](http://fromdatatoknowledge.xyz)
* [Slides for project](https://docs.google.com/presentation/d/16JGC_vJrtQKlkViPoCGy1kgdfBGs667lXzVwMJ1LmWM/edit?usp=sharing)
