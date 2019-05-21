import asyncio
import websockets
import numpy as np
import random


def get_bytes(var):
    data_bytes = bytes(str(var),'utf-8')
    len_data_bytes = bytes(str(len(data_bytes)),'utf-8')
    return len_data_bytes, data_bytes

async def send_var(websocket,var):
    len_data_bytes, data_bytes = get_bytes(var)
    await websocket.send(len_data_bytes)
    await websocket.send(data_bytes)

async def response(websocket,path):
    
    dimension = await websocket.recv()
    print(f"We got the dimension from the client: {dimension}")
    dimension = int(dimension)

    probNo = await websocket.recv()
    print(f"We got the problem number from the client: {probNo}")
    probNo = int(probNo)

    q = doCalculations(dimension,probNo)
    Q = np.sum(q, axis=0)

    totalDimension = 2**dimension
    q0 = np.reshape(q,(totalDimension*totalDimension))

    print(Q)
    print(q0)
   
    for i in range(0,totalDimension):
        await websocket.send(str(int(Q[i])))

    for i in range(0,totalDimension*totalDimension):
        await websocket.send(str(int(q0[i])))


def doCalculations(dim,probNo):
    dim = int(dim)
    totalDim = 2**dim
    
    if(probNo == 0):
        randomNumber = random.randint(1,25618)
    else:
        if(probNo > 25618):
            probNo = probNo % 25618
        randomNumber = probNo

    print("Random number is: "+ str(randomNumber))
    y = ix2prob(randomNumber,totalDim)
    y = np.reshape(y, totalDim)
    y = np.diag(y)

    x = recmonsetup(dim)
    x = np.reshape(x, (totalDim,totalDim), order = "F")

    q = np.matmul(y,x)    

    return q

def recmonsetup(dim):
    if(dim==0):
        return 1  
    else:
        Ds = recmonsetup(dim-1)
        D = np.block([[Ds, Ds], [Ds, -Ds]]) 
        return D

def ix2prob(randomNumber, totalDim):
    y = np.zeros((totalDim,1))
    kk = 0
    for x in range(0,totalDim):
        y[x] = int(2*(randomNumber % 2)-1)
        randomNumber = int(np.floor(randomNumber/2))
        kk = int(kk + (y[x] + 1)/2)       
    return y

while True:
    start_server = websockets.serve(response, 'localhost', 1234)
    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()
