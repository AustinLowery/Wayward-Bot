import discord
import gspread

### SERVICE_ACCOUNT.JSON MUST HAVE PROPER ACCESS TO THE GOOGLE SHEET TO WORK ###
# Replace the below with the bot token
botToken = None

intents = discord.Intents.default()
intents.members = True
client = discord.Client(intents=intents)

# Dictionaries for various options
updateChars = {"image":"B","bullets":"D","backstory":"E","status":"F","extra":"L"}
updateUsers = {"name":"G", "ign": "H", "timezone":"I", "free":"J", "uncomfortable":"K", "contact":"M"}
hlpOptions = {
    "help":"$help help",
    "create":"""
$create 
Character: John
Bulleted Summary: 
+ Average Guy
+ Parents Died
+ Memory Loss
Simplified Backstory: John Doe was an average man born in an average town. His life was boring, until his parents died tragically. He vows revenge on the people that killed his parents. However, after confronting the person who killed them, he was bonked on the head and lost his memory. He heard of Peregrine and hopes to use the wish to restore his memory.
Character Status: Looking for the dungeon master.
Extra Notes: His favorite food is wheat bread.
""",
    "usercreate":"""
$usercreate 
Preffered Name: Johnny
IGN: JohnnyD420
Timezone: UTC
Times I'm Free: 9 AM - 12 PM except on Thursdays.
Things I'm Uncomfortable With: The mentions of presidents.
How To Contact: DM me on discord.
""",
    "bump":"$bump John",
    "get":"$get John",
    "userinfo":"**[Search By Discord IGN]**\n$userinfo Stianu\n**[Search By Preferred Name]**\n$userinfo Austin\n**[Search By a Person's Character]**\n$userinfo Otto",
    "update":"""**[Update Image]**
$ update John image *paste an image in chat*
**[Update Bulleted Summary]**
$update John bullets
+ Average dude
+ Parents Dead
+ Regained his memory
**[Update Backstory]**
$update John backstory John Doe was an average dude with dead parents killed by a bad dude. He lost his memory, but it's back now. Now he just wants bread.
**[Update Character Status]**
$update John status John is eating some bread.
**[Update Extra Notes]**
$update John extra the bread he is eating is wheat bread.
""",
    "userupdate":"""**[Update Name]**
$userupdate name Johnson
**[Update IGN]**
$userupdate ign JohnnyD123
**[Update Timezone]**
$userupdate timezone HST
**[Update Times I'm Free]**
$userupdate free 10 AM-9 PM on Tuesdays
**[Update Thing I'm Uncomfortable With]**
$userupdate uncomfortable A lot of things
**[Update How To Contact]**
$userupdate contact \@ me on twitter
""",
    "updatewhole":"""$updatewhole John 
Character: John
Bulleted Summary: 
+ Average dude
+ Parents Dead
+ Regained his memory
Simplified Backstory: John Doe was an average dude with dead parents killed by a bad dude. He lost his memory, but it's back now. Now he just wants bread.
Character Status: John is eating some bread.
Extra Notes: the bread he is eating is wheat bread.
"""}


@client.event
async def on_ready():
    '''
    Prints to console that the bot has started.
    '''
    print('We have logged in as {0.user}'.format(client))


def botHelp(message:str):
    '''
    Prints out the help message under default the default $help, or prints out an example of a command using $help <command>.

        Parameters:
            message (str): message sent by discord user
    '''
    
    # $help <command>
    if len(str(message.content).split()) == 2 and str(message.content).split()[1] in hlpOptions:
        await message.channel.send(hlpOptions[str(message.content).split()[1]])

        # if it's updatewhole or create, an image is shown of a character example
        if str(message.content).split()[1] == "create" or str(message.content).split()[1] == "updatewhole":
            await message.channel.send("https://upload.wikimedia.org/wikipedia/commons/thumb/c/cb/DnD_Dwarf.png/608px-DnD_Dwarf.png")
    else:
        fullMsg = """**[GETTING STARTED]**
*Use $help <command name> to get an example of how commands are used.*
To get started, run **$create** to create a character. Once you fill out the information, run **$usercreate** to fill out info on yourself. Once you have that set up, bump up your character with **$bump <character>** whenever you can to ensure new people see your character at the top of the list! Please make sure the information is up to date before bumping. Use **$update** for updating characters, and **$userupdate** for updating yourself.
**Character Sheet**: <https://docs.google.com/spreadsheets/d/11pn9SvdBwI9Xy_EMglPViWci7tRp6k2gxfS7_f0p6x8/edit?usp=sharing>
```ini
[$help] Show this screen.
[$help <command>] Shows an example of a specific command
[$create] Creates a character on the google sheet.
[$usercreate] Updates all personal information on your characters.
[$bump <character>] Bump up one of your characters. Make sure the information is up to date.
[$get <character>] See information on a character.
[$userinfo <person's name|ds name|character>] See information on a certain user.
[$update <character> <image|bullets|backstory|status|extra> <updated info>] Updates a specific field on your character.
[$updatewhole <character>] Updates all fields on your character.
[$userupdate <name|ign|timezone|free|uncomfortable|contact> <update text>] Updates information on your personal info.
```
"""
        await message.channel.send(fullMsg, embed=None)


def create(message:str):
    '''
    Creates a character on the google sheet.

        Parameters:
            message (str): message sent by discord user
    '''
    
    sa = gspread.service_account(filename="service_account.json")
    sh = sa.open("Character Info")
    wks = sh.worksheet("Sheet1")

    # if the command fails, something is wrong with the syntax of the command
    try:
        fullMsg = ' '.join(str(message.content).split()[1:])

        # gets each string between each listed attribute
        character = fullMsg[fullMsg.index("Character:")+10:fullMsg.index("Bulleted Summary:")].strip()
        bullets = fullMsg[fullMsg.index("Bulleted Summary:")+17:fullMsg.index("Simplified Backstory:")].strip()
        backstory = fullMsg[fullMsg.index("Backstory:")+10:fullMsg.index("Character Status:")].strip()
        status = fullMsg[fullMsg.index("Character Status:")+17:fullMsg.index("Extra Notes:")].strip()
        extra = fullMsg[fullMsg.index("Extra Notes:")+12:]

        # if image attached then add that image to the sheet; if not, add a default unknown picture to it
        if len(message.attachments):
            wks.update("B101", f'=IMAGE("{message.attachments[0].url}")',raw=False)
        else:
            wks.update("B101", '=IMAGE("https://s.namemc.com/3d/skin/body.png?id=282ed17da571e009&model=classic&width=280&height=280")', raw=False)

        # update a row far below where any information would be written
        wks.update("C101", f'{message.author.name}#{message.author.discriminator}')
        wks.update("D101", bullets.replace("+","\n+"))
        wks.update("E101", backstory)
        wks.update("F101", status)
        wks.update("L101", extra)

        userInfo = True

        # if the author of the message exists already, pull information from them and add it to that row
        if [str(message.author.id)] in wks.get('O2:O100'):
            valueGet = wks.get('O2:O100').index([str(message.author.id)])+2
            wks.update("G101", wks.acell(f"G{valueGet}").value)
            wks.update("H101", wks.acell(f"H{valueGet}").value)
            wks.update("I101", wks.acell(f"I{valueGet}").value)
            wks.update("J101", wks.acell(f"J{valueGet}").value)
            wks.update("K101", wks.acell(f"K{valueGet}").value)
            wks.update("M101", wks.acell(f"M{valueGet}").value)
        else:
            userInfo = False

        wks.update("O101", str(message.author.id))
        wks.update("P101", character)

        date = message.created_at
        wks.update('A101', f'=DATE({date.year}, {date.month}, {date.day})', raw=False)

        await message.channel.send("Character added!")
        if not userInfo:
            await message.channel.send("Please consider adding info on yourself with $usercreate")

        # sort the list
        wks.sort((1,'des'))

    except:
        fullMsg = """**Copy and paste the below and fill out the proper fields; paste an image of your skin or character in the message**:
$create 
Character: 
Bulleted Summary: 
+ 
+ 
+ 
Simplified Backstory: 
Character Status: 
Extra Notes: 
"""
        await message.channel.send(fullMsg)
        await message.channel.send("https://s.namemc.com/3d/skin/body.png?id=282ed17da571e009&model=classic&width=280&height=280")


def userCreate(message:str):
    '''
    Updates all personal information onto your characters.

        Parameters:
            message (str): message sent by discord user
    '''
    
    sa = gspread.service_account(filename="service_account.json")
    sh = sa.open("Character Info")
    wks = sh.worksheet("Sheet1")

    # users cannot make a account without a character
    if [str(message.author.id)] in wks.get('O2:O100'):
        try:
            fullMsg = ' '.join(str(message.content).split()[1:])

            # gets each string between each listed attribute
            name = fullMsg[fullMsg.index("Preffered Name:")+15:fullMsg.index("IGN:")].strip()
            ign = fullMsg[fullMsg.index("IGN:")+4:fullMsg.index("Timezone:")].strip()
            timezone = fullMsg[fullMsg.index("Timezone:")+9:fullMsg.index("Times I'm Free:")].strip()
            free = fullMsg[fullMsg.index("Times I'm Free:")+15:fullMsg.index("Things I'm Uncomfortable With:")].strip()
            comfort = fullMsg[fullMsg.index("Things I'm Uncomfortable With:")+30:fullMsg.index("How To Contact:")]
            contact = fullMsg[fullMsg.index("How To Contact:")+15:]

            # adjust all rows that the person has a character in
            author = [str(message.author.id)]
            for cell,num in zip(wks.get("O2:O100"),range(2,100)):
                if cell == author:
                    wks.update(f"G{num}", name)
                    wks.update(f"H{num}", ign)
                    wks.update(f"I{num}", timezone)
                    wks.update(f"J{num}", free)
                    wks.update(f"K{num}", comfort)
                    wks.update(f"M{num}", contact)
            await message.channel.send("User info added to all of your characters!")
        except:
            fullMsg = """**Copy and paste the below and fill out the proper fields**:
$usercreate 
Preffered Name: 
IGN: 
Timezone: 
Times I'm Free: 
Things I'm Uncomfortable With: 
How To Contact: 
"""
            await message.channel.send(fullMsg)
    else:
        await message.channel.send("Please make a character first by typing $create")


def bump(message):
    '''
    Bump up one of your characters.

        Parameters:
            message (str): message sent by discord user
    '''
    
    sa = gspread.service_account(filename="service_account.json")
    sh = sa.open("Character Info")
    wks = sh.worksheet("Sheet1")

    if len(str(message.content).split()) == 1:
        await message.channel.send("Correct Usage: $bump <character>")
        return
    specialId = str(message.author.id)
    character = ' '.join(str(message.content).split()[1:]).lower()

    # character must exist in the sheet
    try:
        valueEdit = wks.get('P2:P100').index([character.capitalize()])+2
    except:
        await message.channel.send(f"You do not have a character named {character.capitalize()}!")
        return

    # user must own the character they bump
    if wks.acell(f'O{valueEdit}').value == specialId:
        date = message.created_at
        wks.update(f'A{valueEdit}', f'=DATE({date.year}, {date.month}, {date.day})', raw=False)
        await message.channel.send(f"Your character {character.capitalize()} has been bumped up!")
    else:
        await message.channel.send(f"You do not have a character named {character.capitalize()}!")


def getCharacter(message):
    '''
    See information on a character.

        Parameters:
            message (str): message sent by discord user
    '''
    
    sa = gspread.service_account(filename="service_account.json")
    sh = sa.open("Character Info")
    wks = sh.worksheet("Sheet1")

    if len(str(message.content).split()) == 1:
        await message.channel.send("Correct Usage: $get <character>")
        return
    character = ' '.join(str(message.content).split()[1:])
    valueGet = wks.get('P2:P100').index([character])+2

    charRow = wks.get(f"A{valueGet}:P{valueGet}")[0]

    fullMsg = []

    fullMsg.append(f"**Character**: {charRow[15]}")
    fullMsg.append(f"**Bulleted Summary**: {charRow[3]}")
    fullMsg.append(f"**Backstory**: {charRow[4]}")
    fullMsg.append(f"**Character Status**: {charRow[5]}")
    if charRow[11] != "none":
        fullMsg.append(f"**Extra Notes**: {charRow[11]}")

    await message.channel.send('\n'.join(fullMsg))

    img = str(wks.acell(f"B{valueGet}",value_render_option='FORMULA'))
    img = img[img.index('"')+1:img.index('"',img.index('"')+1)]

    await message.channel.send(img)


def userInfo(message):
    '''
    See information on a certain user.

        Parameters:
            message (str): message sent by discord user
    '''
    
    sa = gspread.service_account(filename="service_account.json")
    sh = sa.open("Character Info")
    wks = sh.worksheet("Sheet1")

    if len(str(message.content).split()) == 1:
        await message.channel.send("Correct Usage: $userinfo <person's name|ds name|character>")
        return
    find = str(message.content).split()[1]

    # combines the list of all discord ids, preferred names, and characters
    valueGet = wks.get('P2:P100')
    valueGet.extend(wks.get('C2:C100'))
    valueGet.extend(wks.get('G2:G100'))
    
    # looks first at the shortest strings
    newValueGet = sorted(valueGet,key=lambda x:len(x[0]))

    # searches each value to see if it's within it
    found = None
    for vals in newValueGet:
        if find.lower() in vals[0].lower():
            found = valueGet.index(vals)%(len(valueGet)//3)+2
            break
    if not found is None:
        charRow = wks.get(f"A{found}:P{found}")[0]

        fullMsg = []

        fullMsg.append(f"**Discord**: <RPLC>")
        fullMsg.append(f"**Preferred Name**: {charRow[6]}")
        fullMsg.append(f"**IGN**: {charRow[7]}")
        fullMsg.append(f"**Timezone**: {charRow[8]}")
        fullMsg.append(f"**Free Times**: \n{charRow[9]}")
        fullMsg.append(f"**Things They're Uncomfortable With**: \n{charRow[10]}")
        fullMsg.append(f"**How To Contact**: {charRow[12]}")

        fullMsg = '\n'.join(fullMsg)
        editMsg = await message.channel.send(fullMsg)
        await editMsg.edit(content=fullMsg.replace("<RPLC>",f'<@{charRow[14]}>'))

        user = message.guild.get_member(int(charRow[14]))
        await message.channel.send(user.avatar_url)
    else:
        await message.channel.send("User Not Found.")


def update(message):
    '''
    Updates a specific field on your character.

        Parameters:
            message (str): message sent by discord user
    '''
    
    sa = gspread.service_account(filename="service_account.json")
    sh = sa.open("Character Info")
    wks = sh.worksheet("Sheet1")

    # display becomes false if the command fails
    display = True
    
    specialId = str(message.author.id)
    fullmsg = str(message.content).split()

    # splits word based on spacing and linebreaks
    newmsg = []
    for word in fullmsg:
        newmsg.extend(word.split("\n"))
    fullmsg = newmsg

    if len(fullmsg) <= 2 or not ([fullmsg[1].capitalize()] in wks.get('P2:P100')):
        await message.channel.send("Correct Usage: $update <character> <image\|bullets\|backstory\|status\|extra> <updated info>")
    else:
        character = fullmsg[1]
        valueEdit = wks.get('P2:P100').index([character.capitalize()])+2

        # must own the character
        if wks.acell(f'O{valueEdit}').value == specialId:
            # option must exist
            if fullmsg[2].lower() in updateChars:
                if fullmsg[2].lower() == "image":
                    if len(message.attachments):
                        wks.update(f'B{valueEdit}',f'=IMAGE("{message.attachments[0].url}")',raw=False)
                    else:
                        await message.channel.send("Please paste the image in chat!")
                else:
                    if len(fullmsg) > 3:
                        sentMessage = '\n+'.join(' '.join(fullmsg[3:]).split("+"))
                        wks.update(f'{updateChars[fullmsg[2].lower()]}{valueEdit}',sentMessage)
                    else:
                        await message.channel.send("Correct Usage: $update <character> <image\|bullets\|backstory\|status\|extra> <updated info>")
                        display = False

                if display:
                    charRow = wks.get(f"A{valueEdit}:P{valueEdit}")[0]
                    fullMsg = []

                    fullMsg.append(f"**Character**: {charRow[15]}")
                    fullMsg.append(f"**Bulleted Summary**: {charRow[3]}")
                    fullMsg.append(f"**Backstory**: {charRow[4]}")
                    fullMsg.append(f"**Character Status**: {charRow[5]}")
                    if charRow[11] != "none":
                        fullMsg.append(f"**Extra Notes**: {charRow[11]}")

                    await message.channel.send("**CHARACTER UPDATED!!!**\n\n"+'\n'.join(fullMsg))

                    img = str(wks.acell(f"B{valueEdit}",value_render_option='FORMULA'))
                    img = img[img.index('"')+1:img.index('"',img.index('"')+1)]

                    await message.channel.send(img)
            else:
                await message.channel.send('Invalid Update: Valid options are image, bullets, backstory, status, and extra')
        else:
            await message.channel.send(f"You do not have a character named {character}!")


def updateWhole(message):
    '''
    Updates all fields on your character.

        Parameters:
            message (str): message sent by discord user
    '''
    
    sa = gspread.service_account(filename="service_account.json")
    sh = sa.open("Character Info")
    wks = sh.worksheet("Sheet1")

    # if command fails, syntax is incorrect
    try:
        fullMsg = ' '.join(str(message.content).split()[1:])

        character = str(message.content).split()[1]
        specialId = str(message.author.id)

        # character must exist
        if not [character.capitalize()] in wks.get('P2:P100'):
            await message.channel.send(f"You do not have a character named {character.capitalize()}!")
            return
        valueEdit = wks.get('P2:P100').index([character.capitalize()])+2

        # must own the character to update it
        if wks.acell(f'O{valueEdit}').value == specialId:
            character = fullMsg[fullMsg.index("Character:")+10:fullMsg.index("Bulleted Summary:")].strip()
            bullets = fullMsg[fullMsg.index("Bulleted Summary:")+17:fullMsg.index("Simplified Backstory:")].strip()
            backstory = fullMsg[fullMsg.index("Backstory:")+10:fullMsg.index("Character Status:")].strip()
            status = fullMsg[fullMsg.index("Character Status:")+17:fullMsg.index("Extra Notes:")].strip()
            extra = fullMsg[fullMsg.index("Extra Notes:")+12:]

            # if image provided, change it
            if len(message.attachments):
                wks.update("B{valueEdit}", f'=IMAGE("{message.attachments[0].url}")',raw=False)

            wks.update(f"C{valueEdit}", f'{message.author.name}#{message.author.discriminator}')
            wks.update(f"D{valueEdit}", bullets.replace("+","\n+"))
            wks.update(f"E{valueEdit}", backstory)
            wks.update(f"F{valueEdit}", status)
            wks.update(f"L{valueEdit}", extra)

            userInfo = True

            if [str(message.author.id)] in wks.get('O2:O100'):
                valueGet = wks.get('O2:O100').index([str(message.author.id)])+2
                wks.update(f"G{valueEdit}", wks.acell(f"G{valueGet}").value)
                wks.update(f"H{valueEdit}", wks.acell(f"H{valueGet}").value)
                wks.update(f"I{valueEdit}", wks.acell(f"I{valueGet}").value)
                wks.update(f"J{valueEdit}", wks.acell(f"J{valueGet}").value)
                wks.update(f"K{valueEdit}", wks.acell(f"K{valueGet}").value)
                wks.update(f"M{valueEdit}", wks.acell(f"M{valueGet}").value)
            else:
                userInfo = False

            wks.update(f"O{valueEdit}", str(message.author.id))
            wks.update(f"P{valueEdit}", character)

            date = message.created_at
            wks.update(f'A{valueEdit}', f'=DATE({date.year}, {date.month}, {date.day})', raw=False)

            await message.channel.send(f"Character updated! Use $get {character} to see your updated information.")
            if not userInfo:
                await message.channel.send("Please consider adding info on yourself with $usercreate")

            # sort sheet
            wks.sort((1,'des'))
        else:
            await message.channel.send(f"You do not have a character named {character}!")

    except:
        fullMsg = f"""**Copy and paste the below and fill out the proper fields; paste an image of your skin or character in the message**:
$updatewhole {'<character>' if len(str(message.content).split()) == 1 else str(message.content).split()[1]} 
Character: 
Bulleted Summary: 
+ 
+ 
+ 
Simplified Backstory: 
Character Status: 
Extra Notes: 
"""
        await message.channel.send(fullMsg)
        await message.channel.send("https://s.namemc.com/3d/skin/body.png?id=282ed17da571e009&model=classic&width=280&height=280")


def userUpdate(message):
    '''
    Updates information on your personal info.

        Parameters:
            message (str): message sent by discord user
    '''
    
    sa = gspread.service_account(filename="service_account.json")
    sh = sa.open("Character Info")
    wks = sh.worksheet("Sheet1")

    # must have a character before a user is made
    if [str(message.author.id)] in wks.get('O2:O100'):
        fullMsg = str(message.content).split()
        
        # option must exist
        if fullMsg[1].lower() in updateUsers:
            author = [str(message.author.id)]
            # for each cell with their user id, update that bit of information
            for cell,num in zip(wks.get("O2:O100"),range(2,100)):
                if cell == author:
                    wks.update(f"{updateUsers[fullMsg[1].lower()]}{num}", ' '.join(fullMsg[2:]))
            await message.channel.send(f"User profile updated! Use $userinfo {message.author.name} to see all your information.")
        else:
            await message.channel.send("Correct Usage: $userupdate <name|ign|timezone|free|uncomfortable|contact> <update text>")
    else:
        await message.channel.send("Please make a character first by typing $create")


@client.event
async def on_message(message):
    '''
    Decides on the option chosen.

            Parameters:
                    message (int): A string sent by a discord user.

    '''
    # bot does not read it's own messages
    if message.author == client.user:
        return

    if str(message.content).split()[0] == "$bump":
        bump(message)

    elif str(message.content).split()[0] == "$help":
        botHelp(message)

    elif str(message.content).split()[0] == "$userupdate":
        userUpdate(message)

    elif str(message.content).split()[0] == "$usercreate":
        userCreate(message)

    elif str(message.content).split()[0] == "$create":
        create(message)

    elif str(message.content).split()[0] == "$updatewhole":
        updateWhole(message)

    elif str(message.content).split()[0] == "$get":
        getCharacter(message)

    elif str(message.content).split()[0] == "$userinfo":
        userInfo(message)

    elif str(message.content).split()[0] == "$update":
        update(message)

# run bot
client.run(botToken)
