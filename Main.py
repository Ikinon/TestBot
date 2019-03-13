import datetime

from discord.ext import commands

import config


class testbotBOT(commands.Bot):

    def __init__(self):
        super().__init__(command_prefix="tb.", case_insensitive=True)
        self.LOGGING_CHANNEL = 444234159033155585
        self.uptime = datetime.datetime.utcnow()
        # load extensions
        self.load_extension('General')
        self.load_extension('Owner')
        self.load_extension('ModCmds')
        self.load_extension('Music')

    async def on_ready(self):
        print(f'Username: {self.user.name}')
        print(f'Client ID: {self.user.id}')

    async def on_command_error(self, ctx, error):
        logging = self.get_channel(self.LOGGING_CHANNEL)
        if isinstance(error, commands.CommandOnCooldown):
            time_left = round(error.retry_after, 2)
            await ctx.send(':hourglass: Command on cooldown. Slow '
                           'down. (' + str(time_left) + 's)',
                           delete_after=max(error.retry_after, 1))
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send(':x: Sorry, '
                           'you don\'t have the permissions '
                           'required for that command')
        elif isinstance(error, commands.CommandNotFound):
            pass
        elif isinstance(error, commands.MissingPermissions):
            await logging.send(error)
            await logging.send('Command :' + str(ctx.command))
            await logging.send('Missing Perms: ' + error.missing_perms)
        else:
            await logging.send('Command: ' + str(ctx.command))
            await logging.send(error)
            print(type(error), error)


bot = testbotBOT()


@bot.after_invoke
async def __after_invoke(ctx):
    a = ctx.command.module
    a = str(a)
    if a != "Owner":
        try:
            await ctx.message.delete()
        except:  # pass MissingPermissions and other things
            pass


bot.run(config.TOKEN)
