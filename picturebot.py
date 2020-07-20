import random
import re

from discord.ext import commands

import credentials


## permissions
## read_message_history (to delete input messages)

state = {}

DEFAULTDIEFACES = [
    'Profession',
    'Past',
    'Side Job',
    'Special Thing'
]
FAILUREFACES = ['????', '!!!!']


description = '''PictureDice (tm) die rolling and trust bot.'''
bot = commands.Bot(command_prefix='.', description=description)


@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')



@bot.command()
async def trustsetup(ctx, rolename: str, starttrust: float):
    """Resets the trust for people in a <role> to <value>"""

    ### TODO exclude self, as assume GM

    ## get role
    ## get list of people with rolename
    ## assign default starting trust
    ## print people
    ## store state
    try:
        try:
            roleidx = [r.name.lower() for r in ctx.me.roles].index(rolename.lower())
            role =ctx.me.roles[roleidx]
        except:
            await ctx.send(ctx.message.author.mention + " role {} doens't appear to exist. Try one of {}".format(
                    rolename, ", ".join([r.name for r in ctx.me.roles if not r.name.startswith("@")])))
            return
        await ctx.message.delete()
        ctx.typing()

        state['gm']=ctx.message.author.name
        state['role']=rolename


        players = [m for m in role.members if not m.bot and m.name != state['gm']]

        numPlayers = len(players)

        playerTrust = {r.name:0 for r in players}

        state['trust'] = playerTrust
        if starttrust >0:
            starttrust = starttrust * numPlayers
        else:
            starttrust = -starttrust
        inttrust = starttrust // numPlayers
        for p in playerTrust:
            playerTrust[p]+=int(inttrust)

        randomtrust = int(starttrust - (inttrust * numPlayers))
        remainingExtraTrustPlayers = list(playerTrust.keys())
        for i in range(randomtrust):
            thisPlayer =random.choice(remainingExtraTrustPlayers)
            playerTrust[thisPlayer]+=1
            remainingExtraTrustPlayers.remove(thisPlayer)

        print(state)

        await ctx.send("{} trust reset. You're the GM now".format(ctx.message.author.mention))
        await printTrust(ctx)





    except Exception as e:
        print(e)
        return

##TODO trustset @user int

@bot.command()
async def trustchange(ctx, username:str, newtrust:int):
    """Lets the GM sets player <X> trust to <value>"""

    # find user (leading letters, if unique
    # send trust
    # dm (in channel) recipient
    # dm sender current trust
    # print all trusts to channel
    try:
        playerTrust = state.get('trust',{})

        ## find the sendee - the person trusted
        try:
            # extract a member id
            if not username.startswith("<@"):
                raise

            userid = username.replace("<@", "").replace(">", "").replace('!','')
            userid = int(userid)
            sendee = ctx.guild.get_member(userid)
        except:
            await ctx.send(ctx.message.author.mention + " @ the person whose trust you are trying to change")
            return
        await ctx.message.delete()
        ctx.typing()

        if not playerTrust:
            await ctx.send(ctx.message.author.mention + " trust is not set up. Talk to your GM to do a .trustsetup")
            return

        if ctx.message.author.name != state.get('gm'):
            await ctx.send(ctx.message.author.mention + " You are not the GM. {} is.".format(state.get('gm')))
            return
        playerTrust[sendee.name]=newtrust

        await ctx.send(sendee.mention+" The GM set your trust to {}".format(
                newtrust
        ))

        await printTrust(ctx)







    except Exception as e:
        print(e)
        return

async def printTrust(ctx):
    await ctx.send("\n".join(
            ["{}: {}".format(p, int(t)) for p, t in state.get('trust',{}).items()])
    )


@bot.command()
async def trust(ctx, username:str=''):
    """Sends user <x> a trust"""

    try:
        playerTrust = state.get('trust',{})
        if not username:
            await printTrust(ctx)
            await ctx.message.delete()
            return

        # find the destination user
        try:
            # extract a member id
            if not username.startswith("<@"):
                raise

            userid = username.replace("<@", "").replace(">", "").replace('!','')
            userid = int(userid)
            sendee = ctx.guild.get_member(userid)
        except:
            await ctx.send(ctx.message.author.mention + " @ the person you want to trust")
            print('failed to find',username)
            return

        ## syntactically correct, so carry on
        await ctx.message.delete()
        ctx.typing()

        # find the sender and their trust
        fromGM=False
        sender = ctx.message.author
        if not playerTrust:
            await ctx.send(ctx.message.author.mention + " trust is not set up. Talk to your GM to do a .trustsetup")
            return
        elif sender.name not in playerTrust:
            if sender.name == state.get('gm'):
                fromGM = True
            else:
                await ctx.send(ctx.message.author.mention + " you aren't set up with trust. Do you have the right role - {}? or your GM can fix it with .trustchange".format(
                        state.get('role')
                ))
                return
        elif playerTrust[sender.name]<1:
            await ctx.send(ctx.message.author.mention + " you have no trust. No-one can help you now")
            return


        # find the person being trusted
        if sendee.name not in playerTrust:
            if sendee.name == state.get('gm') and fromGM:
                await ctx.send(ctx.message.author.mention + " You are the GM. Why?"
                         )
            elif sendee.name == state.get('gm'):
                await ctx.send(ctx.message.author.mention + " {} is the GM. Never trust the GM".format(
                        sendee.name
                ))
            else:
                await ctx.send(ctx.message.author.mention + " {} isn't set up with trust. Try one of these".format(
                        sendee.name
                ))
                await printTrust(ctx)

            return


        # send it, handling self & gm cases
        if sendee.name == sender.name:
            await ctx.send(ctx.message.author.mention + " trusted themselves. Selfish".format(
                    sendee.mention, playerTrust[sender.name]
            ))
            playerTrust[sender.name]-=1

        elif fromGM:
            await ctx.send(sendee.mention + " the GM gave you trust. Do you trust them?")
            playerTrust[sendee.name]+=1

        else:
            playerTrust[sender.name]-=1
            playerTrust[sendee.name]+=1
            await ctx.send(ctx.message.author.mention + " trusted {}".format(
                    sendee.mention, playerTrust[sender.name]
            ))

        await printTrust(ctx)







    except Exception as e:
        print('Exception',e)
        return


@bot.command()
async def rp(ctx):
    """Rolls both picture dice, when you try something awesome!"""
    await ctx.message.delete()

    result1 = rollPictureDie(1)
    result2 = rollPictureDie(2)
    if result1 in FAILUREFACES and result1==result2:
        await ctx.send(ctx.message.author.mention + " failed, badly. Double **{}**".format(result1))
    elif result1 in FAILUREFACES and result2 in FAILUREFACES:
        await ctx.send(ctx.message.author.mention + " failed, badly. **{}** and **{}**".format(result1, result2))
    elif result1 in FAILUREFACES or result2 in FAILUREFACES:
        await ctx.send(ctx.message.author.mention + " succeeded, partly. **{}** but also **{}**".format(result1, result2))
    elif result1 == result2:
        await ctx.send(ctx.message.author.mention + " double succeeded! **{}**".format(result1))
    else:
        await ctx.send(ctx.message.author.mention + " succeeded! **{}** or **{}** ".format(result1, result2))


@bot.command()
async def rh(ctx, dienumber:int=0):
    """Rolls one picture die, for helping someone. Optional die number."""
    await ctx.message.delete()

    ## roll one picture dice - when helping someone
    result = rollPictureDie(dienumber)
    if result in FAILUREFACES:
        await ctx.send(ctx.message.author.mention + " tried to help, but made things worse. **{}**".format(result))
    else:
        await ctx.send(ctx.message.author.mention + " successfully helped with: **{}**".format(result))


def rollPictureDie(dienumber):
    diefaces = state.get('dice',{}).get(dienumber, DEFAULTDIEFACES)
    diefaces = diefaces + FAILUREFACES

    return random.choice(diefaces)


@bot.event
async def on_command_error(error, ctx):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(ctx.message.channel, 'Usage: `.r #d#` e.g. `.r 1d20`\nUse .help for more info.')

async def delete_messages(message, author):
    async for historicMessage in message.channel.history():
        if historicMessage.author == bot.user:
            if (author.name in historicMessage.content) or (author.mention in historicMessage.content):
                await historicMessage.delete()

        if historicMessage.content.startswith('.r'):
            if author == historicMessage.author:
                try:
                    await historicMessage.delete()
                except:
                    print('Error: Cannot delete user message!')

@bot.command()
async def r(ctx, roll: str):
    """Rolls a dice using #d# format.
    e.g .r 3d6"""

    resultTotal = 0
    resultString = ''
    try:
        try:
            numDice = roll.split('d')[0]
            diceVal = roll.split('d')[1]
        except Exception as e:
            print(e)
            await ctx.send("Format has to be in #d# %s." % ctx.message.author.name)
            return

        if int(numDice) > 500:
            await ctx.send("I cant roll that many dice %s." % ctx.message.author.name)
            return

        await delete_messages(ctx.message, ctx.message.author)

        ctx.typing()
        await ctx.send("Rolling %s d%s for %s" % (numDice, diceVal, ctx.message.author.name))
        rolls, limit = map(int, roll.split('d'))

        for r in range(rolls):
            number = random.randint(1, limit)
            resultTotal = resultTotal + number

            if resultString == '':
                resultString += str(number)
            else:
                resultString += ', ' + str(number)

        if numDice == '1':
            await ctx.send(ctx.message.author.mention + "  :game_die:\n**Result:** " + resultString)
        else:
            await ctx.send(
                ctx.message.author.mention + "  :game_die:\n**Result:** " + resultString + "\n**Total:** " + str(resultTotal))

        state['lastroll'] = roll
    except Exception as e:
        print(e)
        return


@bot.command()
async def rr(ctx):
    """rerolls the last thing"""
    roll = state.get('lastroll','')
    await r(ctx, roll)


@bot.command()
async def rt(ctx, roll: str):
    """Rolls dice using #d#s# format with a set success threshold, Where s is the thresold type (< = >).
    e.g .r 3d10<55"""

    numberSuccesses = 0
    resultString = ''

    try:
        valueList = re.split("(\d+)", roll)
        valueList = list(filter(None, valueList))

        diceCount = int(valueList[0])
        diceValue = int(valueList[2])
        thresholdSign = valueList[3]
        successThreshold = int(valueList[4])

    except Exception as e:
        print(e)
        await ctx.send("Format has to be in #d#t# %s." % ctx.message.author.name)
        return

    if int(diceCount) > 500:
        await ctx.send("I cant roll that many dice %s." % ctx.message.author.name)
        return

    await delete_messages(ctx.message, ctx.message.author)

    ctx.typing()
    await ctx.send("Rolling %s d%s for %s with a success theshold %s %s" % (
    diceCount, diceValue, ctx.message.author.name, thresholdSign, successThreshold))

    try:
        for r in range(0, diceCount):

            number = random.randint(1, diceValue)
            isRollSuccess = False

            if thresholdSign == '<':
                if number < successThreshold:
                    numberSuccesses += 1
                    isRollSuccess = True

            elif thresholdSign == '=':
                if number == successThreshold:
                    numberSuccesses += 1
                    isRollSuccess = True

            else:  # >
                if number > successThreshold:
                    numberSuccesses += 1
                    isRollSuccess = True

            if resultString == '':
                if isRollSuccess:
                    resultString += '**' + str(number) + '**'
                else:
                    resultString += str(number)
            else:
                if isRollSuccess:
                    resultString += ', ' + '**' + str(number) + '**'
                else:
                    resultString += ', ' + str(number)

            isRollSuccess = False

        if diceCount == 1:
            if numberSuccesses == 0:
                await ctx.send(ctx.message.author.mention + "  :game_die:\n**Result:** " + resultString + "\n**Success:** :x:")
            else:
                await ctx.send(
                    ctx.message.author.mention + "  :game_die:\n**Result:** " + resultString + "\n**Success:** :white_check_mark:")
        else:
            await ctx.send(
                ctx.message.author.mention + "  :game_die:\n**Result:** " + resultString + "\n**Successes:** " + str(numberSuccesses))
    except Exception as e:
        print(e)
        return


bot.run(credentials.token)