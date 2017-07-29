import asyncio

timer = 0

def updatetimer():
    global timer
    timer+=1
    

async def bgloop(TIME, funktorun):
    #Sleep value for reward loop in seconds, love being rewarded for sleeping
    while True:
        funktorun()
        await asyncio.sleep(TIME)


async def inp():
    while True:
        s = input('~')
        if s=='l' or s =='L':
            print('Trying to list')
        if s=='r' or s == 'R':
            print('Trying to recruit members')

#Description: List of async tasks to run in the on ready event
async def tasks():
    await asyncio.wait([
            inp(),
            bgloop(1, updatetimer),
            
            
        ])


loop = asyncio.get_event_loop()
loop.run_until_complete(tasks())
loop.close()



