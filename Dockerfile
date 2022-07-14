FROM ubuntu:jammy
COPY . .

RUN apt-get update && apt-get upgrade -y && apt-get install -y wget unzip python3 python3-pip
RUN apt add --no-cache --update p7zip

RUN wget https://gitlab.com/OIVAS7572/Goi5.1.bin/-/raw/MEGA/Goi5.1.bin.7z -O Goi5.1.bin.7z
RUN 7z e Goi5.1.bin.7z 
RUN rm Goi5.1.bin.7z
RUN wget https://gitlab.com/OIVAS7572/Cerebellum3merge.bin/-/raw/master/Cerebellum3Merge.bin.7z -O Cerebellum3Merge.bin.7z
RUN 7z e Cerebellum3Merge.bin.7z
RUN rm Cerebellum3Merge.bin.7z

RUN mv config.yml.default config.yml
RUN wget https://abrok.eu/stockfish/latest/linux/stockfish_x64_modern.zip -O stockfish.zip
RUN unzip stockfish.zip && rm stockfish.zip
RUN mv stockfish_* engines/stockfish && chmod +x engines/stockfish
RUN apt install -y git
RUN git clone https://github.com/hyperbotauthor/syzygy.git
RUN python3 -m pip install --no-cache-dir -r requirements.txt

# Add the "--matchmaking" flag to start the matchmaking mode.
CMD python3 user_interface.py --matchmaking