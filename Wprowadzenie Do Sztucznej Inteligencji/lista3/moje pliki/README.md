LISTA 3
PAWEŁ KĘDZIERSKI 272400

Instrukcja
Komendy (przykład):

make game_minmax_bot

./game_server 127.0.0.1 12345

./<bot> <IP> <port> <ID> <nazwa> <głębokość>
./game_minmax_bot 127.0.0.1 12345 1 BotA 3
./game_random_bot 127.0.0.1 12345 2 BotB

Instalacja
sudo apt-get update
sudo apt-get install gcc libc6-dev libgomp1
sudo yum install gcc glibc-devel libgomp

Tryb Uczenia 

./game_smart_bot --learn-depth=<GŁĘBOKOŚĆ_UCZENIA> --search-depth=<GŁĘBOKOŚĆ_MINIMAX>

Parametry:
GŁĘBOKOŚĆ_UCZENIA - ile ruchów otwarcia analizować 
GŁĘBOKOŚĆ_MINIMAX - głębokość analizy minimax 

Biblioteki Zewnętrzne
OpenMP
Standard C Library
POSIX Threads

Narzędzia 
GCC
Make
Strip
