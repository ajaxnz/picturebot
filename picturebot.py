import random
import re
import math

from discord.ext import commands
import discord

import credentials


## permissions
## read_message_history (to delete input messages)

GLOBALstate = {
    'trustchannels':{}}

DEFAULTDIEFACES = [
    'Profession',
    'Past',
    'Side Job',
    'Special Thing'
]
FAILUREFACES = ['????', '!!!!']


description = '''PictureDice (tm) die rolling and trust bot.

Setup assumes the members of the game will have a role to identify them'''
bot = commands.Bot(command_prefix='.', description=description)


@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')



def printTrust(ctx):
    state = GLOBALstate.setdefault(ctx.channel.name, {})
    return "\n".join(
            ["{}: {}".format(state['players'][p].display_name, int(t)) for p, t in state.get('trust',{}).items()])

def getUser(ctx, username):
    ## decodes the string username returns the user object
    try:
        # extract a member id
        if not username.startswith("<@"):
            raise

        userid = username.replace("<@", "").replace(">", "").replace('!', '')
        userid = int(userid)
        user = ctx.guild.get_member(userid)
        return user
    except:
        return None


@bot.command()
async def truststart(ctx, totaltrust: int, role_or_player: str,
                     player2:str=None,
                     player3:str=None,
                     player4:str=None,
                     player5:str=None,
                     player6:str=None,
                     player7:str=None,
                     player8:str=None,
                     player9:str=None,
                     player10:str=None
                     ):
    """Set up trust in this channel for users or role.
total trust <value>
rolename or list of @users"""

    try:
        state = {}
        GLOBALstate[ctx.channel.name] = state

        if role_or_player.startswith('<@'):
            players = []
            for username in [role_or_player, player2,player3,player4,player5,player6,player7,player8,player9,player10]:
                if username:
                    user = getUser(ctx, username)
                    if user:
                        players.append(user)
                    else:
                        await ctx.send(ctx.message.author.mention + " user {} doesn't appear to exist. @ them?".format(
                                username))
                        return

        else:
            role = None
            botRoles = {r.name:r for r in ctx.me.roles}
            userRoles = {r.name:r for r in ctx.message.author.roles}
            availableroles = {s for s in set(botRoles.keys()) | set(userRoles.keys()) if not s.startswith("@")}
            for r in availableroles:
                if r.lower() == role_or_player.lower():
                    role = botRoles.get(r, userRoles.get(r))
                    break
            if not role:
                await ctx.send(ctx.message.author.mention + " role {} doesn't appear to exist. Try {}".format(
                        role_or_player, ", ".join(availableroles)))
                return
            players = [m for m in role.members if not m.bot and m.name != state['gm'] and m.status==discord.Status.online]
            state['role']=role_or_player
        await ctx.message.delete()
        ctx.typing()

        state['gm']=ctx.message.author.name
        state['players'] = {p.name:p for p in players}
        state['trust'] = {p.name:0 for p in players}

        numPlayers = len(players)
        totaltrust = abs(totaltrust)
        inttrust = totaltrust // numPlayers
        for p in state['trust']:
            state['trust'][p]+=int(inttrust)

        randomtrust = int(totaltrust - (inttrust * numPlayers))
        for p in random.sample(state['trust'].keys(),randomtrust):
            state['trust'][p]+=1

        print(state)

        await ctx.send("{} trust reset. You're the GM in this channel now".format(ctx.message.author.mention))
        await ctx.send(printTrust(ctx))





    except Exception as e:
        print(e)
        return

##TODO trustset @user int

@bot.command()
async def trustset(ctx, username:str, newtrust:int):
    """For the GM to set player <X> trust to <value>"""

    # find user (leading letters, if unique
    # send trust
    # dm (in channel) recipient
    # dm sender current trust
    # print all trusts to channel
    try:
        state = GLOBALstate.setdefault(ctx.channel.name,{})

        if not state.get('trust'):
            await ctx.send(ctx.message.author.mention + " trust is not set up. The GM can set it up using .truststart")
            return

        ## find the sendee - the person trusted
        sendee = getUser(ctx, username)
        if not sendee:
            await ctx.send(ctx.message.author.mention + " @ the person whose trust you are trying to change")
            return
        await ctx.message.delete()
        ctx.typing()


        if ctx.message.author.name != state.get('gm'):
            await ctx.send(ctx.message.author.mention + " You are not the GM. {} is.".format(state.get('gm')))
            return
        if newtrust == -231742:
            if sendee.name in state['trust']:
                state['trust'].pop(sendee.name,None)
                state['players'].pop(sendee.name)
                await ctx.send(ctx.message.author.mention + " removed " + sendee.mention + " from this trust pool")
            else:
                await ctx.send(ctx.message.author.mention + " tried to remove " + sendee.display_name + " but they don't exist.")
        else:
            newtrust = max(0,newtrust)
            state['trust'][sendee.name]=newtrust
            state['players'][sendee.name]=sendee
            await ctx.send(sendee.mention+" The GM set your trust to {}".format(
                  newtrust
            ))

        await ctx.send(printTrust(ctx))


    except Exception as e:
        print(e)
        return


@bot.command()
async def trustremove(ctx, username:str):
    """For the GM to remove players from the current trust pool"""

    await trustset(ctx, username, -231742)




@bot.command()
async def trust(ctx, username:str=''):
    """Sends user <x> a trust"""

    try:
        state = GLOBALstate.setdefault(ctx.channel.name,{})
        if not state.get('trust'):
            await ctx.send(ctx.message.author.mention + " trust is not set up. The GM can set it up using .truststart")
            return

        if not username:
            await ctx.send(printTrust(ctx))
            await ctx.message.delete()
            return

        # find the destination user
        sendee = getUser(ctx, username)
        if not sendee:
            await ctx.send(ctx.message.author.mention + " @ the person you want to trust")
            print('failed to find',username)
            return

        ## syntactically correct, so carry on
        await ctx.message.delete()
        ctx.typing()

        # find the sender and their trust
        fromGM=False
        sender = ctx.message.author
        if sender.name not in state['trust']:
            if sender.name == state.get('gm'):
                fromGM = True
            else:
                await ctx.send(ctx.message.author.mention + " you aren't set up with trust. Do you have the right role - {}? or your GM can fix it with .trustset".format(
                        state.get('role')
                ))
                return
        elif state['trust'][sender.name]<1:
            await ctx.send(ctx.message.author.mention + " you have no trust. No-one can help you now")
            return


        # find the person being trusted
        if sendee.name not in state['trust']:
            if sendee.name == state.get('gm') and fromGM:
                await ctx.send(ctx.message.author.mention + " You are the GM. Why?"
                         )
            elif sendee.name == state.get('gm'):
                await ctx.send(ctx.message.author.mention + " {} is the GM. Never trust the GM".format(
                        sendee.name
                ))
            else:
                await ctx.send(ctx.message.author.mention + " {} isn't set up with trust. Try one of these".format(
                        sendee.display_name
                ))
                await ctx.send(printTrust(ctx))

            return


        # send it, handling self & gm cases
        if sendee.name == sender.name:
            await ctx.send(ctx.message.author.mention + " trusted themselves. Selfish".format(
                    sendee.mention, state['trust'][sender.name]
            ))
            state['trust'][sender.name]-=1

        elif fromGM:
            await ctx.send(sendee.mention + " the GM gave you trust. Do you trust them?")
            state['trust'][sendee.name]+=1

        else:
            state['trust'][sender.name]-=1
            state['trust'][sendee.name]+=1
            await ctx.send(ctx.message.author.mention + " trusted {}. Will you help them?".format(
                    sendee.mention
            ))

        await ctx.send(printTrust(ctx))

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
    result = rollPictureDie(ctx, dienumber)
    if result in FAILUREFACES:
        await ctx.send(ctx.message.author.mention + " tried to help, but made things worse. **{}**".format(result))
    else:
        await ctx.send(ctx.message.author.mention + " successfully helped with: **{}**".format(result))


def rollPictureDie(ctx, dienumber):
    state = GLOBALstate.get(ctx.channel.name)
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

        state = GLOBALstate.setdefault(ctx.channel.name,{})
        state['lastroll'] = roll
    except Exception as e:
        print(e)
        return


@bot.command()
async def rr(ctx):
    """rerolls the last thing"""
    state = GLOBALstate.setdefault(ctx.channel.name, {})
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