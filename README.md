# cs5113fa22-project

## Development Schedule
- completed architecture descrition [10/27] - 2h
- spend 5h to design interface and write protoc file by [11/03]
- spend 3h to write the first version logging by [11/17]
- spend 12h to finish the project by [12/01]
- spend 2h preparing the final presentation by [12/14]

## Emoji Chooser
- create a 2d array of N*N to initalize the board
- each trainer will take different emoji from available human emoji
- each pokemon will take different emoji from available animal emoji list
- init N to be between 9 and 25
- init P to be random of (5, N)
- init T to be random of (5, N)
this will create 1 server machine that control the board, P machines for P pokemon and T machines for Trainer.

Dockercompose.yml: create (N+P+1) services that each sevice in N and P will communicate with 1 server service.
Dockerfile: build on top of Ubuntu base image, install all the deps requriments and command to run node.py
Protocol Buffer: create services that allow Trainer and Pokeman communicate with Server. 
