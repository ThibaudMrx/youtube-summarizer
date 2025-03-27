# YouTube Summarizer

A Python-based solution demonstrating audio download and basic processing from YouTube. This tool is ideal for quick demos or stand-alone audio handling scripts. It downloads audio via YouTubeDL, outputs an MP3 file, and logs processing time.

## Features

-  Downloads audio via YouTubeDL
-  Outputs an MP3 file
-  Logs processing time

## Requirements

-  Docker

## License

Distributed under the MIT License.  
Copyright (c) 2025 - Thibaud Merieux

## Example Results

### Input Video

http://www.youtube.com/watch?v=4FTIVJEBkNY

### Summary Extracted

**Part 1**  
**1.a** Saint Laurent Island is located near Gambel and the Bering Sea, approximately 65 km from Russian coast.  
**1.b** Two Russian citizens arrived on a small boat seeking asylum in October 2022 due to Vladimir Putin's order of mobilization for war in Ukraine.

**Part 2**  
**2.a** The Bering Strait separates Chukotka, an autonomous region in Russia, and Alaska, a state in the United States.  
**2.b** Historically significant for Russian trade colonies, the Bering Strait later became a symbol of Cold War tensions and is affected by Arctic ice melt. Today, it connects the Arctic and Pacific Oceans.

**Part 3**  
**3.a** The Bering Strait has become navigable throughout winter due to climate change accelerating in the Arctic four times faster than on the rest of the planet.  
**3.b** A new commercial route, the Northeast Route, is emerging between Pacific and European ports, potentially reducing shipping distance significantly.

**Part 4**  
**4.a** Climate change presents economic and political opportunities for Russia, as it allows easier access to natural resources in the Arctic.  
**4.b** Russia is reasserting its territorial claims in the Arctic and expanding military bases along its coastline since the invasion of Ukraine.

**Part 5**  
**5.a** The opening of the Bering Strait to regular navigation could position Russia at the center of global commercial exchanges, intensifying its maritime links with China, its main trade partner and oil supplier.  
**5.b** Climate change also attracts strategic interest from China as it allows for a Northern route avoiding Suez and Malacca congestion.

**Part 6**  
**6.a** Disputes over the extension of the continental shelf exist between Russia, Canada, and Denmark over the Kara Sea.  
**6.b** Political instability in the region is increasing due to diplomatic provocations and military reinforcements by both Russia and Western powers.

**Part 7**  
**7.a** Mourmansk serves as Russia's gateway to the Arctic and its natural resources, with key industries including fishing, a nuclear-powered icebreaker fleet, and potential as a hub for LNG exports to Europe and China.  
**7.b** The US is expanding the port of Nome to monitor the Bering Strait approach and has relocated F-35 fighters to Fairbanks airbase and an anti-missile base at Delta Junction.

## Next Steps
-  Use Youtube generated subtitles form a lighter load (downloading audio and extracting text with whisper is too heavy, it was just a playground idea to use some LLM libraries)
-  Integrate with MLflow to extract and analyze performance metrics of various models.
-  Implement a tree diagram for visualizing output.
-  [DRAFT DONE] Develop the front-end webpage for user interaction. FastAPI MVP exists
-  [DONE] Containerize the application by creating a Docker image.
-  [DONE] Deploy the application serverlessly using the Docker image and AWS resources.

## Helpers

To set up and run the project locally, follow these steps:

```sh
python3 -m venv venv
pip install -r requirements.txt
source venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8000
```

Note : Now is needed a running mistral model on an ollama endpoint

### Docker Setup

To run the application using Docker, use the following commands:

```sh
# Create a Docker network
docker network create youtube-summarizer-network

# Build the Docker image
docker build -t youtube-summarizer .

# Run the Ollama container
docker run -p 11434:11434 --name ollama --gpus=all --network youtube-summarizer-network ollama/ollama
docker exec -it ollama ollama run mistral

# Run the YouTube Summarizer app container
docker run -p 8000:8000 --name youtube-summarizer --gpus=all --network youtube-summarizer-network youtube-summarizer
# Here the app should work properly.

# Test connectivity from the app container
docker exec -it youtube-summarizer curl -I http://ollama:11434/

# Run the HTTP test script
docker exec -it youtube-summarizer python3 testsOllamaHTTP.py
```

## Contact

For more information or inquiries, please contact Thibaud Merieux.
