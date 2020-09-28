import random
random.seed()
import re
import time
from discord.ext import commands
import discord

import credentials


## permissions
## read_message_history (to delete input messages)

GLOBALstate = {}



description = '''PictureDice (tm) die rolling and Story Point bot.

Setup assumes the members of the game will have a role to identify them'''
bot = commands.Bot(command_prefix='.', description=description)

try:
    # mac path
    opus = discord.opus.load_opus('libopus.dylib')
except:
    try:
        # docker path
        opus = discord.opus.load_opus('/usr/lib/libopus.so.0')
    except Exception as e:
        print(e)



@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Error: {}\nTry .help for more info.".format(error))
    else:
        await ctx.send("Something odd went wrong. {}".format(error))



#####
#####
#####
#####
#####
#####
#####  story point related functions


def printStory(ctx):
    state = GLOBALstate.setdefault(ctx.channel.id, {})
    return "\n".join(
            ["{}: {}".format(state['players'][p].display_name, int(t)) for p, t in state.get('story',{}).items()])

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
async def setupstory(ctx, totalstory: int, role_or_player1: str,
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
    """Set up story in this channel for users or role.
total story <value>
name of a role or list of @users"""

    try:
        state = GLOBALstate.setdefault(ctx.channel.id, {})

        if role_or_player1.startswith('<@'):
            players = []
            for username in [role_or_player1, player2, player3, player4, player5, player6, player7, player8, player9, player10]:
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
                if r.lower() == role_or_player1.lower():
                    role = botRoles.get(r, userRoles.get(r))
                    break
            if not role:
                await ctx.send(ctx.message.author.mention + " role {} doesn't appear to exist. Try {}".format(
                        role_or_player1, ", ".join(availableroles)))
                return
            players = [m for m in role.members if not m.bot and m.name != state['gm'] and m.status==discord.Status.online]
            state['role']=role_or_player1
        await ctx.message.delete()
        ctx.typing()

        state['gm']=ctx.message.author.name
        state['players'] = {p.name:p for p in players}
        state['story'] = {p.name:0 for p in players}

        numPlayers = len(players)
        totalstory = abs(totalstory)
        intstory = totalstory // numPlayers
        for p in state['story']:
            state['story'][p]+=int(intstory)

        randomstory = int(totalstory - (intstory * numPlayers))
        for p in random.sample(state['story'].keys(),randomstory):
            state['story'][p]+=1

        print(state)

        await ctx.send("{} story reset. You're the GM in this channel now".format(ctx.message.author.mention))
        await ctx.send(printStory(ctx))


    except Exception as e:
        print('setupstory',e)


MAGIC_REMOVE_NUMBER = -231742
@bot.command()
async def storyset(ctx, player:str, newstory:int):
    """For the GM to set player <@X> story to <value>"""

    # find user (leading letters, if unique
    # send story
    # dm (in channel) recipient
    # dm sender current story
    # print all story points to channel
    try:
        state = GLOBALstate.setdefault(ctx.channel.id,{})

        if not state.get('story'):
            await ctx.send(ctx.message.author.mention + " Story Points are not set up. The GM can set it up using .setupstory")
            return

        ## find the sendee - the person storyed
        sendee = getUser(ctx, player)
        if not sendee:
            await ctx.send(ctx.message.author.mention + " @ the person whose Story Points you are trying to change")
            return
        await ctx.message.delete()
        ctx.typing()


        if ctx.message.author.name != state.get('gm'):
            await ctx.send(ctx.message.author.mention + " You are not the GM. {} is.".format(state.get('gm')))
            return
        if newstory == MAGIC_REMOVE_NUMBER:
            if sendee.name in state['story']:
                state['story'].pop(sendee.name,None)
                state['players'].pop(sendee.name)
                await ctx.send(ctx.message.author.mention + " removed " + sendee.mention + " from this Story Point pool")
            else:
                await ctx.send(ctx.message.author.mention + " tried to remove " + sendee.display_name + " but they don't exist.")
        else:
            newstory = max(0,newstory)
            state['story'][sendee.name]=newstory
            state['players'][sendee.name]=sendee
            await ctx.send(sendee.mention+" The GM set your Story Points to {}".format(
                  newstory
            ))

        await ctx.send(printStory(ctx))


    except Exception as e:
        print('storyset',e)


@bot.command()
async def storyremove(ctx, username:str):
    """For the GM to remove players from the current Story Point pool"""

    await storyset(ctx, username, MAGIC_REMOVE_NUMBER)




@bot.command()
async def story(ctx, player:str=None):
    """Sends user <x> a story"""

    try:
        state = GLOBALstate.setdefault(ctx.channel.id,{})
        if not state.get('story'):
            await ctx.send(ctx.message.author.mention + " Story Points are not set up. The GM can set it up using .setupstory")
            return

        if not player:
            await ctx.send(printStory(ctx))
            await ctx.message.delete()
            return

        # find the destination user
        sendee = getUser(ctx, player)
        if not sendee:
            await ctx.send(ctx.message.author.mention + " @ the person you want ask for help from")
            print('failed to find', player)
            return

        ## syntactically correct, so carry on
        await ctx.message.delete()
        ctx.typing()

        # find the sender and their story points
        fromGM=False
        sender = ctx.message.author
        if sender.name not in state['story']:
            if sender.name == state.get('gm'):
                fromGM = True
            else:
                await ctx.send(ctx.message.author.mention + " you aren't set up with Story Points. Your GM can add you in with .storyset".format(
                        state.get('role')
                ))
                return
        elif state['story'][sender.name]<1:
            await ctx.send(ctx.message.author.mention + " you have no Story Points. No-one can help you now")
            return

        # find the person being given Story Points
        if sendee.name not in state['story']:
            if sendee.name == state.get('gm') and fromGM:
                await ctx.send(ctx.message.author.mention + " You are the GM. Why?"
                         )
            elif sendee.name == state.get('gm'):
                await ctx.send(ctx.message.author.mention + " {} is the GM, they're not in this story. @ yourself to spend Story Points".format(
                        sendee.name
                ))
            else:
                await ctx.send(ctx.message.author.mention + " {} isn't set up with Story Points. Try one of these".format(
                        sendee.display_name
                ))
                await ctx.send(printStory(ctx))

            return


        # send it, handling self & gm cases
        if sendee.name == sender.name:
            await ctx.send(ctx.message.author.mention + " spent a Story Point. Awesome!".format(
                    sendee.mention, state['story'][sender.name]
            ))
            state['story'][sender.name]-=1

        elif fromGM:
            await ctx.send(sendee.mention + " the GM gave you a Story Point!")
            state['story'][sendee.name]+=1

        else:
            state['story'][sender.name]-=1
            state['story'][sendee.name]+=1
            await ctx.send(ctx.message.author.mention + " gave {} a Story Point. Will you help them?".format(
                    sendee.mention
            ))

        await ctx.send(printStory(ctx))

    except Exception as e:
        print('story',e)




@bot.command()
async def tcard(ctx):
    """Raises a t-card in the current channel"""
    try:
        await ctx.message.delete()

        embedTcard = discord.Embed.from_dict({
        })
        embedTcard.set_image(url='http://geas.org.uk/wp-content/uploads/2020/08/tcard-1-e1597167776966.png')


        ## now nav to parent group (if there is one, then first active voice channel)
        categoryid = ctx.channel.category_id
        category = ctx.guild.get_channel(categoryid)

        ## try to find relevant role to @ rather than the @here cos on our server that gets the admins too, who are sick of it!
        atRole = None
        for role in category.changed_roles:
            if '@' in role.name:
                continue
            elif ' ' not in role.name:
                # make the wild assumption the relevant has a space in it
                continue
            elif not atRole or len(role.name)> len(atRole.name):
                # make the wild assuptiion that the role we want is the longest one, and has a space in it
                atRole = role


        if not atRole:
            atRole = '@here'
        else:
            atRole = atRole.mention





        await ctx.send("{} **T CARD T CARD T CARD T CARD**".format(atRole), embed=embedTcard)


        for channel in category.voice_channels:
            print('got channel', channel.name)
            voicething = await channel.connect()
            print('connected')
            tcardaudio = discord.PCMAudio(open("tcard.wav", "rb"))
            print('setup sound')
            print('opus loaded')
            voicething.play(tcardaudio)
            print('playeded')
            while voicething.is_playing():
                time.sleep(1)
            await voicething.disconnect()


    except Exception as e:
        print('tcard exception',type(e),e)






#####
#####
#####
#####
#####
#####
#####  Picturedice related functions


DEFAULTDIEFACES = [
    'Description',
    'Title',
    'Past',
    'Other Thing',
    'Team Role'
]
FAILUREFACES = ['????', '!!!!']



# @bot.command()
async def setuppicturedice1(ctx, diename:str, face1:str, face2:str, face3:str, face4:str, failure1:str=None, failure2:str=None):
    """Sets the labels for the dice.
Give a name so you can customise the dice for your game, or even labels per person for serious personalisation
Use 'default' as a die name to change the default"""
    await ctx.message.delete()

    state = GLOBALstate.setdefault(ctx.channel.id,{})
    if not diename or diename =='0':
        diename = 'default'

    thisdie = state.setdefault('dice1',{})[diename] = [face1, face2, face3, face4]+FAILUREFACES
    if failure1:
        thisdie[4] = failure1
    if failure2:
        thisdie[5] = failure2
    await ctx.send(ctx.message.author.mention + " setup picturedice {} as {}".format(
            diename, ' '.join(thisdie)))

@bot.command()
async def setuppicturedice(ctx, diename:str, face1:str, face2:str, face3:str, face4:str, face5:str):
    """Sets the labels for the dice.
Give a name so you can customise the dice for your game, or even labels per person for serious personalisation
Use 'default' as a die name to change the default"""
    await ctx.message.delete()

    state = GLOBALstate.setdefault(ctx.channel.id,{})
    if not diename or diename =='0':
        diename = 'default'

    thisdie = state.setdefault('dice2',{})[diename] = [face1, face2, face3, face4, face5]
    await ctx.send(ctx.message.author.mention + " setup picturedice {} as {}".format(
            diename, ' '.join(thisdie)))

# @bot.command()
async def showpicturedice1(ctx):
    """Show the picture dice sets defined"""
    try:
        await ctx.message.delete()

        state = GLOBALstate.setdefault(ctx.channel.id,{})
        picturedicestring = ''
        for diename, diefaces in state.get('dice1',{}).items():
            picturedicestring+='**{}** {}\n'.format(diename, ' '.join(diefaces))
        picturedicestring+='**default** {}'.format(' '.join(DEFAULTDIEFACES))

        await ctx.send("Current picture dice sets are\n"+picturedicestring)
    except Exception as e:
        print('picturediceshow',e)





@bot.command()
async def showpicturedice(ctx):
    """Show the picture dice sets defined"""
    try:
        await ctx.message.delete()

        state = GLOBALstate.setdefault(ctx.channel.id,{})
        picturedicestring = ''
        for diename, diefaces in state.get('dice2',{}).items():
            picturedicestring+='**{}** {}\n'.format(diename, ' '.join(diefaces))
        picturedicestring+='**default** {}'.format(' '.join(DEFAULTDIEFACES))

        await ctx.send("Current picture dice sets are\n"+picturedicestring)
    except Exception as e:
        print('picturediceshow',e)







@bot.command()
async def rp(ctx, die1:str=None):
    """Rolls both picture dice  when you do something
Give die names you've set up with picturedicesetup for personalised dice, it'll remember the last dice you rolled"""
    try:
        await ctx.message.delete()
        state = GLOBALstate.setdefault(ctx.channel.id,{})
        lastd1,lastd2 = state.get('lastrp2',{}).get(ctx.message.author.name,(None,None))

        ## vestigial handling of 2 input die names
        die2 = None
        if lastd1 and not die1:
            die1 = lastd1
        if lastd2 and not die2:
            die2 = lastd2
        if die1 and not die2:
            die2 = die1
        if die1 or die2:
            state.setdefault('lastrp2', {})[ctx.message.author.name] =  (die1, die2)

        result1, fail1= rollPictureDie2(ctx, die1, FAILUREFACES[0])
        result2, fail2= rollPictureDie2(ctx, die2, FAILUREFACES[1])
        # print(result1,fail1,result2,fail2)
        if fail1 and fail2 and result1==result2:
            await ctx.send(ctx.message.author.mention + " failed, badly. Double **{}**".format(result1))
        elif fail1 and fail2:
            await ctx.send(ctx.message.author.mention + " failed, badly. **{}** and **{}**".format(result1, result2))
        elif fail1 or fail2:
            if fail1:
                failres=result1
                succeedres=result2
            else:
                failres=result2
                succeedres=result1
            await ctx.send(ctx.message.author.mention + " failed. **{}** whilst trying **{}**".format(failres, succeedres))
        elif result1 == result2:
            ## presume using face1+face2
            f1 = getDieFaces2(ctx, die1, dieface=0)
            f2 = getDieFaces2(ctx, die1, dieface=1)

            await ctx.send(ctx.message.author.mention + " messy success! **{} {}**".format(f1,f2))
        else:
            await ctx.send(ctx.message.author.mention + " succeeded! **{}** or **{}** ".format(result1, result2))
    except Exception as e:
        print('rp',e)



# @bot.command()
async def rp1(ctx, die1:str=None, die2:str=None):
    """Rolls both picture dice, when you do something
Give die names you've set up with picturedicesetup for personalised dice, it'll remember the last pair you rolled"""
    try:
        await ctx.message.delete()
        state = GLOBALstate.setdefault(ctx.channel.id,{})
        lastd1,lastd2 = state.get('lastrp',{}).get(ctx.message.author.name,(None,None))

        if lastd1 and not die1:
            die1 = lastd1
        if lastd2 and not die2:
            die2 = lastd2
        if die1 and not die2:
            die2 = die1
        if die1 or die2:
            state.setdefault('lastrp', {})[ctx.message.author.name] =  (die1, die2)

        result1, fail1= rollPictureDie(ctx, die1)
        result2, fail2= rollPictureDie(ctx, die2)
        if fail1 and fail2 and result1==result2:
            await ctx.send(ctx.message.author.mention + " failed, badly. Double **{}**".format(result1))
        elif fail1 and fail2:
            await ctx.send(ctx.message.author.mention + " failed, badly. **{}** and **{}**".format(result1, result2))
        elif fail1 or fail2:
            await ctx.send(ctx.message.author.mention + " succeeded, partly. **{}** but also **{}**".format(result1, result2))
        elif result1 == result2:
            await ctx.send(ctx.message.author.mention + " double succeeded! **{}**".format(result1))
        else:
            await ctx.send(ctx.message.author.mention + " succeeded! **{}** or **{}** ".format(result1, result2))
    except Exception as e:
        print('rp',e)


# @bot.command()
async def rh(ctx, die:str=None):
    """Rolls one picture die, for helping someone.
Supply a die name to use that instead of the default, it'll remember what you rolled last"""
    await ctx.message.delete()
    state = GLOBALstate.setdefault(ctx.channel.id,{})
    lastd = state.get('lastrh', {}).get(ctx.message.author.name)

    if lastd and not die:
        die = lastd
    if die:
        state.setdefault('lastrh', {})[ctx.message.author.name] = die

    ## roll one picture dice - when helping someone
    result, fail = rollPictureDie(ctx, die)
    if fail:
        await ctx.send(ctx.message.author.mention + " tried to help, but made things worse. **{}**".format(result))
    else:
        await ctx.send(ctx.message.author.mention + " successfully helped with: **{}**".format(result))


def rollPictureDie(ctx, diename, faillevel=4, failsymbol=None):
    if not diename:
        diename = 'default'
    state = GLOBALstate.get(ctx.channel.id)
    diefaces = DEFAULTDIEFACES[:4] + FAILUREFACES
    for thisdie, thesediefaces in state.get('dice1',{}).items():
        if thisdie.lower()=='default':
            diefaces = thesediefaces
            break
    for thisdie, thesediefaces in state.get('dice1',{}).items():
        if thisdie.lower()==diename.lower():
            diefaces = thesediefaces
            break

    rollnum = random.randint(0,5)
    # print('rolling {} ({}) got {}'.format(diename, diefaces, rollnum))
    if rollnum >= faillevel and failsymbol:
        return failsymbol, True
    return diefaces[rollnum], rollnum>=faillevel


def getDieFaces2(ctx, diename, dieface:int=None):
    if not diename:
        diename=''
    state = GLOBALstate.get(ctx.channel.id)
    diefaces = DEFAULTDIEFACES
    for thisdie, thesediefaces in state.get('dice2',{}).items():
        # channel default
        if thisdie.lower()=='default':
            diefaces = thesediefaces
            break
    for thisdie, thesediefaces in state.get('dice2',{}).items():
        # specific die name
        if thisdie.lower()==diename.lower():
            diefaces = thesediefaces
            break

    if dieface is not None:
        return diefaces[dieface]
    else:
        return diefaces.copy()

def rollPictureDie2(ctx, diename, failsymbol):
    diefaces = getDieFaces2(ctx, diename)
    diefaces.append(failsymbol)

    rollnum = random.randint(0,5)
    # print('rolling {} ({}) got {}'.format(diename, diefaces, rollnum))
    return diefaces[rollnum], rollnum>=5





#####
#####
#####
#####
#####
#####
#####  Boring dice with numbers related functions


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

        if int(numDice) > 100:
            await ctx.send("I cant roll that many dice %s." % ctx.message.author.name)
            return

        # await delete_messages(ctx.message, ctx.message.author)
        await ctx.message.delete()

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

        state = GLOBALstate.setdefault(ctx.channel.id,{})
        state.setdefault('lastroll',{})[ctx.message.author.name] = roll
    except Exception as e:
        print('r',e)
        return


@bot.command()
async def rr(ctx):
    """rerolls the last boring numbered dice you rolled"""
    state = GLOBALstate.setdefault(ctx.channel.id, {})
    roll = state.get('lastroll', {}).get(ctx.message.author.name,'')

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

    if int(diceCount) > 100:
        await ctx.send("I cant roll that many dice %s." % ctx.message.author.name)
        return

    # await delete_messages(ctx.message, ctx.message.author)
    await ctx.message.delete()


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