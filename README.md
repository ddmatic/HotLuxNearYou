# HotLuxNearYou

## The Apartment Hunt Saga

Apartment hunting can be a frustrating process. For weeks, I scrolled through listings, visited various places, and almost closed deals—only to discover that by the time I was ready, the apartment was **already gone**.

It felt like every time I found something promising, it slipped away just as quickly. 

To address this, I decided to build a solution. Refreshing a webpage every few minutes wasn’t practical, so I created a script that checks what's new on the market and keeps track of apartments that are no longer available. Now, I can wake up, check the updates, and know whether I've missed a good opportunity or if something new has rolled in.

This is the **HotLuxNearYou** project—designed to help streamline the apartment search process and make sure no good listings slip through the cracks.

## Features:
- Check new apartment listings every morning.
- Track apartments that are no longer available.
- Reduce the frustration of missing out on desirable apartments.
- On the first day, a file `apts_tdy.xlsx` will be created and updated daily.
- On the second day, a file `apts_ytd.xlsx` will be created to track yesterday's data _(Since you get new `apts_tdy.xlsx`)_. 
- All the data files will be stored in a `data` folder, which will be automatically created on the first run.
- On the first run, a `scripts` folder will be created, containing the `Hot Lux Near You Runner.bat` file, which can be used to easily run the application.

## Setup:
1. Clone the repository.
2. Install `reqs.txt`
3. Run the script periodically for the latest updates.
4. On the first run, a `scripts` folder will be created, where you'll find the `Hot Lux Near You Runner.bat` file to launch the app.

## License:
Feel free to adapt this script for your own apartment-hunting needs. All the configuration options are in the `config.py` file.

Happy hunting! 🏠✨
