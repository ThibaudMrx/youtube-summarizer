A Python-based solution demonstrating audio download and basic processing from YouTube. Includes progress logging and timing. Suitable for quick demos or stand-alone audio handling scripts.

## Features

- Downloads audio via YouTubeDL  
- Outputs an MP3 file  
- Logs processing time  

## Requirements

- Python 3.x  
- youtube-dl or yt-dlp  
- FFmpeg  

## Usage

1. Install dependencies by running `pip install -r app/requirements.txt`.
2. Open the `app/ProofOfWorkNotebook.ipynb` and change the input video URL. Then run the script

## License

Distributed under the MIT License. Copyright (c) 2025 - Thibaud Merieux



# Example results
### Input video :
http://www.youtube.com/watch?v=4FTIVJEBkNY

### Summary Extracted:

 Part 1
    1.a Saint Laurent Island is located near Gambel and the Bering Sea, approximately 65 km from Russian coast.
    1.b Two Russian citizens arrived on a small boat seeking asylum in October 2022 due to Vladimir Putin's order of mobilization for war in Ukraine.

   Part 2
    2.a The Bering Strait separates Chukotka, an autonomous region in Russia, and Alaska, a state in the United States.
    2.b Historically significant for Russian trade colonies, the Bering Strait later became a symbol of Cold War tensions and is affected by Arctic ice melt. Today, it connects the Arctic and Pacific Oceans.

   Part 3
    3.a The Bering Strait has become navigable throughout winter due to climate change accelerating in the Arctic four times faster than on the rest of the planet.
    3.b A new commercial route, the Northeast Route, is emerging between Pacific and European ports, potentially reducing shipping distance significantly.

   Part 4
    4.a Climate change presents economic and political opportunities for Russia, as it allows easier access to natural resources in the Arctic.
    4.b Russia is reasserting its territorial claims in the Arctic and expanding military bases along its coastline since the invasion of Ukraine.

   Part 5
    5.a The opening of the Bering Strait to regular navigation could position Russia at the center of global commercial exchanges, intensifying its maritime links with China, its main trade partner and oil supplier.
    5.b Climate change also attracts strategic interest from China as it allows for a Northern route avoiding Suez and Malacca congestion.

   Part 6
    6.a Disputes over the extension of the continental shelf exist between Russia, Canada, and Denmark over the Kara Sea.
    6.b Political instability in the region is increasing due to diplomatic provocations and military reinforcements by both Russia and Western powers.

   Part 7
    7.a Mourmansk serves as Russia's gateway to the Arctic and its natural resources, with key industries including fishing, nuclear-powered icebreaker fleet, and potential hub for LNG exports to Europe and China.
    7.b The US is expanding the port of Nome to monitor Bering Strait approach and has relocated F-35 fighters to Fairbanks airbase and an anti-missile base at Delta Junction.

### Next steps 
- Integrating with mflow to extract performance metrics of different models (so far, Mistral runs OK on my machine, better than other available solutions and is more reliable onthe output format)
- Creating a tree diagram as output
- Creating the front webpage
- Creating the docker image of the app
- Running the app serverless witht he docker image and AWS ressources
    
